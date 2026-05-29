#!/usr/bin/env bash
# Generate arg_dictionary inputs from CrossHair for api_bgp_nh_update.
#
# Run from examples/:
#   bgpd_nexthop_mgmt/gen_tests.sh
#
# Overridable via environment variables:
#   COVERAGE_TYPE                  (default: path)
#   PER_CONDITION_TIMEOUT          (default: 120)
#   PER_PATH_TIMEOUT               (default: 30)
#   MAX_UNINTERESTING_ITERATIONS   (default: 1000)
set -euo pipefail

TARGET="bgpd_nexthop_mgmt.crosshair_target.api_bgp_nh_update_with_precondition"
OUTPUT_DIR="bgpd_nexthop_mgmt/tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/args_${TIMESTAMP}.txt"
LOG_FILE="$OUTPUT_DIR/crosshair_argdict_${TIMESTAMP}.log"

COVERAGE_TYPE="${COVERAGE_TYPE:-path}"
PER_CONDITION_TIMEOUT="${PER_CONDITION_TIMEOUT:-120}"
PER_PATH_TIMEOUT="${PER_PATH_TIMEOUT:-30}"
MAX_UNINTERESTING_ITERATIONS="${MAX_UNINTERESTING_ITERATIONS:-1000}"

mkdir -p "$OUTPUT_DIR"

echo "target:                       $TARGET"
echo "coverage_type:                $COVERAGE_TYPE"
echo "per_condition_timeout:        ${PER_CONDITION_TIMEOUT}s"
echo "per_path_timeout:             ${PER_PATH_TIMEOUT}s"
echo "max_uninteresting_iterations: $MAX_UNINTERESTING_ITERATIONS"
echo "output:                       $OUTPUT_FILE"
echo "log:                          $LOG_FILE"
echo

# Invoke crosshair via python3 -c (instead of the `crosshair` CLI) so we can
# bump sys.setrecursionlimit first. CrossHair's pytest emitter recurses
# through an AbcChain when collecting imports, and large iteration counts
# trip the default limit (RecursionError in path_cover.py). The bump is
# defensive — arg_dictionary doesn't hit that specific path today, but the
# guard costs nothing and keeps the script robust if you switch formats.
PYTHONPATH=".:lib" python3 -c "
import sys
sys.setrecursionlimit(50000)
from crosshair.main import main
sys.argv = [
    'crosshair', 'cover',
    '--example_output_format', 'arg_dictionary',
    '--coverage_type', '$COVERAGE_TYPE',
    '--per_condition_timeout', '$PER_CONDITION_TIMEOUT',
    '--per_path_timeout', '$PER_PATH_TIMEOUT',
    '--max_uninteresting_iterations', '$MAX_UNINTERESTING_ITERATIONS',
    '$TARGET',
]
sys.exit(main())
" > "$OUTPUT_FILE" 2> "$LOG_FILE"

LINES=$(wc -l < "$OUTPUT_FILE" | tr -d ' ')
DISTINCT=$(sort -u "$OUTPUT_FILE" | wc -l | tr -d ' ')
echo "wrote $LINES rows ($DISTINCT distinct) to $OUTPUT_FILE"
