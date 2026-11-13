#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../../.." && pwd)
container=bgp-release-check
port=11795
out_dir=/tmp/bgp-release-check
replace=false

usage() {
  cat <<'EOF'
Usage: bash run_release_check.sh [options]
Check the saved corpus, replay every case, and verify same-prefix withdrawals.

  --container NAME  Lab name (default: bgp-release-check)
  --port PORT       Local BGP port (default: 11795)
  --out DIR         Reports directory (default: /tmp/bgp-release-check)
  --replace         Recreate an existing lab with the same name
  -h, --help        Show this help

Requires Python 3.10+ and a running Docker daemon. The lab stays available
after the check; stop it with: docker stop bgp-release-check
EOF
}
die() { echo "error: $*" >&2; exit 1; }

while (($#)); do
  case "$1" in
    --container|--port|--out)
      (($# >= 2)) || die "$1 needs a value"
      case "$1" in
        --container) container=$2 ;; --port) port=$2 ;; --out) out_dir=$2 ;;
      esac
      shift 2 ;;
    --replace) replace=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done

[[ "$container" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || die "invalid container name"
[[ "$port" =~ ^[0-9]{1,5}$ ]] || die "port must be an integer from 1 to 65535"
port=$((10#$port))
((port >= 1 && port <= 65535)) || die "port must be from 1 to 65535"
[[ -n "$out_dir" ]] || die "--out needs a nonempty directory"
command -v python3 >/dev/null || die "Python 3.10+ is required"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "Python 3.10+ is required"
command -v docker >/dev/null || die "install Docker and start its daemon first"
docker info >/dev/null 2>&1 || die "Docker is not running; start it and retry"

mkdir -p -- "$out_dir"
out_dir=$(cd -- "$out_dir" && pwd)
cd -- "$REPO_ROOT"

echo "Checking offline tests and saved AS_PATH corpus..."
python3 -m unittest models.bgpd.malformed_packets.testing.test_core_release \
  models.bgpd.malformed_packets.testing.test_scripts \
  models.bgpd.malformed_packets.testing.test_aspath_release
python3 -m models.bgpd.malformed_packets.seed_aspath_suite
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite all --dry-run --fail-on-deviation --out "$out_dir/dry-run.json"

setup_args=(--container "$container" --port "$port")
if $replace; then setup_args+=(--replace); fi
bash "$SCRIPT_DIR/setup_frr_container.sh" "${setup_args[@]}"

echo "Replaying the complete saved corpus against FRR..."
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer \
  --suite all --container "$container" --port "$port" \
  --fail-on-deviation --out "$out_dir/live.json"
python3 -m models.bgpd.malformed_packets.testing.strict_withdrawal \
  --container "$container" --port "$port" --out "$out_dir/withdrawal.json"

python3 - "$out_dir/dry-run.json" "$out_dir/live.json" "$out_dir/withdrawal.json" <<'PY'
import json
import sys

dry = json.load(open(sys.argv[1]))['summary']
live = json.load(open(sys.argv[2]))['summary']
withdrawal = json.load(open(sys.argv[3]))
if (dry['total'] < 1 or dry['total'] != live['total']
        or dry['corpus'] != live['corpus']
        or dry['distinct_attribute_sequences'] != live['distinct_attribute_sequences']
        or live['dry_run'] or live['coverage_mode']
        or live['deviations'] or live['connection_failures']
        or live['observation_errors']
        or sum(row['PASS'] for row in live['matrix'].values()) != live['total']
        or withdrawal['total'] < 1 or withdrawal['passed'] != withdrawal['total']
        or withdrawal['failures']):
    raise SystemExit('error: full replay did not match the offline corpus or had failures')
print(f"Release check passed: {live['total']}/{live['total']} live cases matched")
print(f"Strict withdrawals: {withdrawal['passed']}/{withdrawal['total']} distinct cases passed")
PY
git rev-parse HEAD > "$out_dir/commit.txt"
echo "Reports: $out_dir/dry-run.json, $out_dir/live.json, $out_dir/withdrawal.json"
echo "Commit: $(cat "$out_dir/commit.txt")"
echo "Stop the lab when finished: docker stop $container"
