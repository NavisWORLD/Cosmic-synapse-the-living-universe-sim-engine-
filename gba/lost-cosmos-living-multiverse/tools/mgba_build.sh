#!/usr/bin/env bash
set -euo pipefail
TASK_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
"${CC:-cc}" -std=c11 -O2 -fPIC -shared -Wall -Wextra -Werror \
  "$TASK_DIR/mgba_bridge.c" -lmgba -o "$TASK_DIR/mgba_bridge.so"
