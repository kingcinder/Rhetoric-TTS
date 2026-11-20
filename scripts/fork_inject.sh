#!/usr/bin/env bash
# Inject fork failure into a command using the LD_PRELOAD shim.
# Usage: fork_inject.sh <budget> <command> [args...]
#   budget: number of fork() calls to fail with EAGAIN (0 means no failure)
#   command: the command to run (remaining args are the command)

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <budget> <command> [args...]" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHIM="$SCRIPT_DIR/scripts/forkfail.so"
SOURCE="$SCRIPT_DIR/scripts/forkfail.c"

# The shim is a host binary and is not committed. Rebuild it when it is missing
# or older than its source, so a checkout on another machine or architecture
# never runs a stale object file.
if [[ ! -f "$SHIM" || "$SOURCE" -nt "$SHIM" ]]; then
  echo "Building forkfail.so..." >&2
  if ! gcc -shared -fPIC -o "$SHIM" "$SOURCE"; then
    echo "ERROR: cannot build $SHIM; install gcc or export LD_PRELOAD yourself." >&2
    exit 1
  fi
fi

export FORK_FAIL_BUDGET="$1"
shift

if [[ -n "${LD_PRELOAD:-}" ]]; then
  export LD_PRELOAD="$SHIM:$LD_PRELOAD"
else
  export LD_PRELOAD="$SHIM"
fi

exec "$@"
