#!/usr/bin/env bash
# Isolated draft: no host ports, no replacement of the existing frr-lab.
# Requires the image built by setup_frr_coverage.sh. Additional arguments
# are passed to run_parity_fuzzer (e.g. --limit 8 or --suite all).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LAB_NAME="frr-route-draft-$$"
RESULT_DIR="$(mktemp -d /tmp/frr-route-draft.XXXXXX)"
MEASURE=0
CREATED=0
if [[ "${1:-}" == --measure ]]; then
  MEASURE=1
  shift
fi
cleanup() {
  if [[ "$CREATED" != 1 ]]; then return; fi
  docker stop -t 10 "$LAB_NAME" >/dev/null 2>&1 || true
  docker rm "$LAB_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker run -d --name "$LAB_NAME" --network none \
  --mount "type=bind,source=$REPO_DIR,target=/workspace,readonly" \
  --mount "type=bind,source=$SCRIPT_DIR/route_lab.conf,target=/etc/frr/frr.conf,readonly" \
  frr-coverage-lab /usr/lib/frr/bgpd -S -Z -p 1179 \
  -f /etc/frr/frr.conf >/dev/null
CREATED=1
docker exec "$LAB_NAME" touch /etc/frr/vtysh.conf
wait_ready() {
  for attempt in {1..30}; do
    if docker exec "$LAB_NAME" test -S /var/run/frr/bgpd.vty; then return; fi
    sleep 0.2
  done
  docker logs "$LAB_NAME"
  return 1
}
wait_ready
capture() {
  local label="$1"
  # Stop flushes this daemon's gcov counters; restart preserves its filesystem.
  docker stop -t 10 "$LAB_NAME" >/dev/null
  docker start "$LAB_NAME" >/dev/null
  wait_ready
  docker exec "$LAB_NAME" lcov --capture --directory /frr \
    --output-file /tmp/all.info --rc lcov_branch_coverage=1 \
    >"$RESULT_DIR/$label-lcov.log" 2>&1
  docker exec "$LAB_NAME" lcov --extract /tmp/all.info \
    '*/bgpd/bgp_attr.c' '*/bgpd/bgp_fsm.c' '*/bgpd/bgp_open.c' \
    '*/bgpd/bgp_packet.c' '*/bgpd/bgp_route.c' \
    --output-file /tmp/target.info --rc lcov_branch_coverage=1 \
    >>"$RESULT_DIR/$label-lcov.log" 2>&1
  docker cp "$LAB_NAME:/tmp/target.info" "$RESULT_DIR/$label.info"
}
if [[ "$MEASURE" == 1 ]]; then
  docker exec "$LAB_NAME" lcov --zerocounters --directory /frr >/dev/null 2>&1
  docker exec -w /workspace "$LAB_NAME" python3 -m \
    models.bgpd.malformed_packets.run_parity_fuzzer --suite all_existing --limit 100 \
    --coverage-mode --fail-on-deviation --frr-local --lab-profile combined \
    --frr-log /tmp/route-lab.log \
    --out /tmp/baseline.json
  docker cp "$LAB_NAME:/tmp/baseline.json" "$RESULT_DIR/baseline.json"
  # Also establish all three peers before the baseline capture. This keeps
  # the basic multi-peer topology from being credited to generated traces.
  docker exec -w /workspace "$LAB_NAME" python3 -m \
    models.bgpd.malformed_packets.run_parity_fuzzer --suite routecompetition \
    --route-baseline --coverage-mode --fail-on-deviation --frr-local \
    --lab-profile combined --frr-log /tmp/route-lab.log --out /tmp/control.json
  docker cp "$LAB_NAME:/tmp/control.json" "$RESULT_DIR/control.json"
  capture baseline
fi
status=0
if [[ "$MEASURE" == 1 ]]; then set -- "$@" --coverage-mode; fi
docker exec -w /workspace "$LAB_NAME" python3 -m \
  models.bgpd.malformed_packets.run_parity_fuzzer --suite generated \
  --frr-local --lab-profile combined --frr-log /tmp/route-lab.log \
  --fail-on-deviation "$@" \
  --out /tmp/route-stateful.json || status=$?
docker cp "$LAB_NAME:/tmp/route-stateful.json" "$RESULT_DIR/report.json"
docker cp "$LAB_NAME:/tmp/route-lab.log" "$RESULT_DIR/bgpd.log"
echo "Report and log: $RESULT_DIR"
if [[ "$MEASURE" == 1 && "$status" == 0 ]]; then
  capture generated
  python3 "$SCRIPT_DIR/compare_c_coverage.py" \
    "$RESULT_DIR/baseline.info" "$RESULT_DIR/generated.info" | tee "$RESULT_DIR/delta.txt"
fi
exit "$status"
