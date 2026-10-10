#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../../.." && pwd)
container=frr-lab
port=1179
limit=100
out_dir="$SCRIPT_DIR/coverage_html_c"
baseline=false

usage() {
  cat <<'EOF'
Usage: bash collect_c_coverage.sh [options]
Start a fresh daemon, send the saved cases, and collect bgpd C coverage.
Requires a running lab created by setup_frr_coverage.sh.

  --baseline        Save this run as the baseline for later comparisons
  --container NAME  Container name (default: frr-lab)
  --port PORT       Local BGP port (default: 1179)
  --limit N         Maximum cases per suite (default: 100)
  --out DIR         Report directory (default: coverage_html_c beside this script)
  -h, --help        Show this help

Outputs: index.html, target.info, summary.json, parity.json;
         baseline.json when --baseline is used.
The lab is restarted after capture. Coverage mode does not check RFC parity.
EOF
}
die() { echo "error: $*" >&2; exit 1; }
while (($#)); do
  case "$1" in
    --container|--port|--limit|--out)
      (($# >= 2)) || die "$1 needs a value"
      case "$1" in
        --container) container=$2 ;; --port) port=$2 ;; --limit) limit=$2 ;; --out) out_dir=$2 ;;
      esac
      shift 2 ;;
    --baseline) baseline=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done
[[ "$container" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || die "invalid container name"
[[ "$port" =~ ^[0-9]{1,5}$ ]] || die "port must be an integer from 1 to 65535"
port=$((10#$port))
((port >= 1 && port <= 65535)) || die "port must be from 1 to 65535"
[[ "$limit" =~ ^[0-9]{1,9}$ ]] || die "limit must be a positive integer"
limit=$((10#$limit))
((limit > 0)) || die "limit must be positive"
command -v docker >/dev/null || die "install Docker and start its daemon first"
command -v python3 >/dev/null || die "Python 3.10+ is required"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "Python 3.10+ is required"
docker info >/dev/null 2>&1 || die "Docker is not running; start it and retry"
label=$(docker inspect --format '{{index .Config.Labels "org.sonic-formal-infra.coverage"}}' "$container" 2>/dev/null || true)
[[ "$label" == true ]] || die "$container is not the current coverage lab; run setup_frr_coverage.sh (see --help)"
docker exec "$container" pgrep -x bgpd >/dev/null || die "bgpd is not running in $container; rerun setup_frr_coverage.sh --replace"
docker exec -u frr "$container" test -w /frr/bgpd || die "the FRR build tree is not writable by frr; rebuild the coverage lab"
mkdir -p "$out_dir"
out_dir=$(cd -- "$out_dir" && pwd)
tmp_dir=$(mktemp -d)
restart=false
cleanup() {
  status=$?
  if $restart; then
    docker restart "$container" >/dev/null || echo "error: could not restart $container" >&2
  fi
  rm -rf "$tmp_dir"
  return "$status"
}
trap cleanup EXIT
stop_bgpd() {
  restart=true
  docker exec "$container" pkill -TERM -x bgpd
  for ((attempt=0; attempt<30; attempt++)); do
    if ! docker exec "$container" pgrep -x bgpd >/dev/null; then return; fi
    sleep 1
  done
  die "bgpd did not exit; counters were not captured"
}
revision=$(docker exec -u frr "$container" git -C /frr rev-parse HEAD)
echo "Starting a fresh coverage run in $container..."
stop_bgpd
# Clear files while bgpd is stopped; an active process retains in-memory counts.
docker exec "$container" lcov --zerocounters --directory /frr
docker restart "$container" >/dev/null
restart=false
echo "Waiting for the coverage observer's BGP session..."
observer=false
for ((attempt=0; attempt<60; attempt++)); do
  peers=$(docker exec "$container" vtysh -c 'show bgp summary json' 2>/dev/null || true)
  if python3 -c 'import json, sys
try:
    peer = json.load(sys.stdin)["ipv4Unicast"]["peers"]["127.0.0.1"]
    sys.exit(peer["state"] != "Established")
except (ValueError, KeyError):
    sys.exit(1)' <<< "$peers"; then observer=true; break; fi
  sleep 1
done
$observer || die "coverage observer did not establish BGP within 60 seconds; rerun setup_frr_coverage.sh --replace"
echo "Sending up to $limit cases per suite (coverage only)..."
cd -- "$REPO_ROOT"
python3 -m models.bgpd.malformed_packets.run_parity_fuzzer --suite all \
  --container "$container" --port "$port" --limit "$limit" --coverage-mode \
  --fail-on-deviation --out "$out_dir/parity.json"

echo "Stopping bgpd to flush counters..."
stop_bgpd
echo "Capturing coverage before restarting bgpd..."
docker exec "$container" lcov --capture --directory /frr --output-file /tmp/bgp-coverage-all.info --rc lcov_branch_coverage=1
docker exec "$container" lcov --extract /tmp/bgp-coverage-all.info \
  '*/bgpd/bgp_attr.c' '*/bgpd/bgp_open.c' '*/bgpd/bgp_packet.c' '*/bgpd/bgp_route.c' \
  --output-file /tmp/bgp-coverage-target.info --rc lcov_branch_coverage=1
docker exec "$container" genhtml /tmp/bgp-coverage-target.info \
  --output-directory /tmp/bgp-coverage-html --rc lcov_branch_coverage=1
docker cp "$container:/tmp/bgp-coverage-target.info" "$out_dir/target.info"
docker cp "$container:/tmp/bgp-coverage-html/." "$out_dir"
args=(--info "$out_dir/target.info" --revision "$revision" --out "$out_dir" --parity "$out_dir/parity.json")
if $baseline; then args+=(--baseline); fi
python3 -m models.bgpd.malformed_packets.testing.c_coverage "${args[@]}"
docker restart "$container" >/dev/null
restart=false
python3 - "$port" <<'PY'
import socket, sys, time
deadline = time.monotonic() + 60
while time.monotonic() < deadline:
    try:
        with socket.create_connection(('127.0.0.1', int(sys.argv[1])), timeout=1):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit('error: lab restarted but BGP did not become ready')
PY
echo "Report: $out_dir/index.html"
echo "Metrics: $out_dir/summary.json"
