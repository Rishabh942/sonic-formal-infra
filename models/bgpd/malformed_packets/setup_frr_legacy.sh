#!/usr/bin/env bash
# Optional historical FRR 7.5 lab; the default release uses FRR 10.0.1.
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
exec bash "$SCRIPT_DIR/setup_frr_container.sh" --image frrouting/frr:v7.5.0 "$@"
