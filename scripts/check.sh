#!/usr/bin/env bash
# The one verification command for this repository: everything CI runs. Exit code is the verdict.
set -euo pipefail
cd "$(dirname "$0")/.."
make check
echo "check: OK"
