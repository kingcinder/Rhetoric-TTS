#!/usr/bin/env bash
# Inject fork failure into a command using the LD_PRELOAD shim.
# Usage: fork_inject.sh <budget> <command>
#   budget: number of fork() calls to fail with EAGAIN (0 means no failure)
#   command: the command to run (remaining args are the command)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHIM="$SCRIPT_DIR/scripts/forkfail.so"

if [[ ! -f "$SHIM" ]]; then
    echo "Building forkfail.so..." >&2
    gcc -shared -fPIC -o "$SHIM" "$SCRIPT_DIR/scripts/forkfail.c" 2>/dev/null || {
        echo "Warning: gcc not available, fork shim will not be built" >&2
        exec "$@"
    }
fi

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <budget> <command>" >&2
    exit 1
fi

BUDGET="$1"
shift

export FORK_FAIL_BUDGET="$BUDGET"

if [[ -n "${LD_PRELOAD:-}" ]]; then
    export LD_PRELOAD="$SHIM:${LD_PRELOAD}"
else
    export LD_PRELOAD="$SHIM"
fi

exec "$@"