#!/usr/bin/env bash
# Generate arg_dictionary inputs from CrossHair for BGP state machine sequences.
#
# Run from examples/:
#   bgp_malformed_packets/gen_tests.sh

set -euo pipefail

TARGET="bgp_malformed_packets.crosshair_target.execute_bgp_sequence"
OUTPUT_DIR="bgp_malformed_packets/tests"
OUTPUT_FILE="$OUTPUT_DIR/bgp_argdict.txt"
LOG_FILE="$OUTPUT_DIR/crosshair.log"

COVERAGE_TYPE="path"
PER_CONDITION_TIMEOUT="60"
PER_PATH_TIMEOUT="10"
MAX_UNINTERESTING_ITERATIONS="500"

mkdir -p "$OUTPUT_DIR"

echo "Generating test paths via CrossHair symbolic execution..."
echo "target: $TARGET"
echo "output: $OUTPUT_FILE"

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
echo "Done! Wrote $LINES execution paths to $OUTPUT_FILE."
