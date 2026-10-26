#!/usr/bin/env bash
# Legacy name; forwarding to run_rhetoric.sh.
exec "$(dirname "${BASH_SOURCE[0]}")/run_rhetoric.sh" "$@"
