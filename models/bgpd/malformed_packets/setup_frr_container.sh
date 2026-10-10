#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../../.." && pwd)
container=frr-lab
port=1179
image=quay.io/frrouting/frr:10.0.1
coverage=false
replace=false

usage() {
  cat <<'EOF'
Usage: bash setup_frr_container.sh [options]
Create a local FRR lab and wait until BGP is listening.

  --container NAME  Container name (default: frr-lab)
  --port PORT       Local BGP port (default: 1179; bound to 127.0.0.1)
  --replace         Remove an existing container with this name first
  --coverage        Build and use the FRR 10.0.1 gcov image
  --image IMAGE     Use another FRR image (standard mode only)
  -h, --help        Show this help
EOF
}
die() { echo "error: $*" >&2; exit 1; }
while (($#)); do
  case "$1" in
    --container|--port|--image)
      (($# >= 2)) || die "$1 needs a value"
      case "$1" in
        --container) container=$2 ;; --port) port=$2 ;; --image) image=$2 ;;
      esac
      shift 2 ;;
    --replace) replace=true; shift ;;
    --coverage) coverage=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done
[[ "$container" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || die "invalid container name"
[[ "$port" =~ ^[0-9]{1,5}$ ]] || die "port must be an integer from 1 to 65535"
port=$((10#$port))
((port >= 1 && port <= 65535)) || die "port must be from 1 to 65535"
command -v docker >/dev/null || die "install Docker and start its daemon first"
command -v python3 >/dev/null || die "Python 3.10+ is required"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "Python 3.10+ is required"
docker info >/dev/null 2>&1 || die "Docker is not running; start it and retry"
if docker container inspect "$container" >/dev/null 2>&1 && ! $replace; then
  die "$container already exists. Use --replace to recreate it, or choose --container and --port."
fi
if $coverage; then
  [[ "$image" == quay.io/frrouting/frr:10.0.1 ]] || die "--image cannot be combined with --coverage"
  image=frr-coverage-lab
  echo "Building FRR 10.0.1 with gcov (the first build can take several minutes)..."
  docker build -t "$image" -f "$SCRIPT_DIR/Dockerfile.coverage" "$SCRIPT_DIR"
else
  docker image inspect "$image" >/dev/null 2>&1 || docker pull "$image"
fi
if $replace && docker container inspect "$container" >/dev/null 2>&1; then
  docker rm -f "$container" >/dev/null
fi

tmp_dir=$(mktemp -d)
created=false
cleanup() {
  status=$?
  if ((status != 0)) && $created; then
    echo "Setup failed; recent logs from $container:" >&2
    docker logs --tail 20 "$container" >&2 || true
  fi
  rm -rf "$tmp_dir"
}
trap cleanup EXIT
cat > "$tmp_dir/frr.conf" <<'EOF'
log file /tmp/bgpd.log debugging
router bgp 65001
 bgp router-id 10.0.0.1
 no bgp ebgp-requires-policy
 neighbor FUZZ peer-group
 neighbor FUZZ remote-as 65002
 neighbor FUZZ disable-connected-check
 neighbor FUZZ ebgp-multihop 255
 bgp listen range 0.0.0.0/0 peer-group FUZZ
EOF
if $coverage; then
  cat >> "$tmp_dir/frr.conf" <<'EOF'
 neighbor 127.0.0.1 remote-as 65003
 neighbor 127.0.0.1 port 1790
 neighbor 127.0.0.1 timers 3 9
EOF
fi
chmod 644 "$tmp_dir/frr.conf"
docker create --init --name "$container" --cap-add NET_ADMIN --cap-add SYS_ADMIN \
  --label org.sonic-formal-infra.lab=bgp-malformed-packets \
  -p "127.0.0.1:$port:179" "$image" >/dev/null
created=true
docker cp "$tmp_dir/frr.conf" "$container:/etc/frr/frr.conf"
printf 'service integrated-vtysh-config\n' > "$tmp_dir/vtysh.conf"
chmod 644 "$tmp_dir/vtysh.conf"
docker cp "$tmp_dir/vtysh.conf" "$container:/etc/frr/vtysh.conf"
if ! $coverage; then
  docker cp "$container:/etc/frr/daemons" "$tmp_dir/daemons"
  python3 - "$tmp_dir/daemons" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
path.write_text(path.read_text().replace('bgpd=no', 'bgpd=yes'))
PY
  docker cp "$tmp_dir/daemons" "$container:/etc/frr/daemons"
fi
docker start "$container" >/dev/null
echo "Waiting for BGP at 127.0.0.1:$port..."
ready=false
for ((attempt=0; attempt<60; attempt++)); do
  config=$(docker exec "$container" vtysh -c 'show running-config' 2>/dev/null || true)
  if [[ "$config" == *"router bgp 65001"* ]] && python3 - "$port" <<'PY'
import socket, sys
try:
    with socket.create_connection(('127.0.0.1', int(sys.argv[1])), timeout=1):
        pass
except OSError:
    sys.exit(1)
PY
  then
    if $coverage; then
      peers=$(docker exec "$container" vtysh -c 'show bgp summary json' 2>/dev/null || true)
      if ! python3 -c 'import json, sys
try:
    peer = json.load(sys.stdin)["ipv4Unicast"]["peers"]["127.0.0.1"]
    sys.exit(peer["state"] != "Established")
except (ValueError, KeyError):
    sys.exit(1)' <<< "$peers"; then
        sleep 1
        continue
      fi
    fi
    ready=true
    break
  fi
  sleep 1
done
$ready || die "BGP or its coverage observer did not become ready within 60 seconds"
echo "Ready: $container ($image), BGP 127.0.0.1:$port, peer ASN 65002."
echo "From the repository root ($REPO_ROOT), run:"
if $coverage; then
  printf '  bash models/bgpd/malformed_packets/collect_c_coverage.sh --container %q --port %q --baseline\n' "$container" "$port"
else
  printf '  python3 -m models.bgpd.malformed_packets.run_parity_fuzzer --suite all --container %q --port %q --fail-on-deviation\n' "$container" "$port"
fi
printf 'Stop the lab when finished: docker stop %q\n' "$container"
