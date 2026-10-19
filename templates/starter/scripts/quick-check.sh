#!/usr/bin/env bash
# Quick check: lint and types in well under 90 seconds. The last line is the verdict, the exit code is the truth.
# Copy to scripts/quick-check.sh, then fill the two commands (or export QUICK_LINT and QUICK_TYPES).
# No tests, no build, no dev server, no network: scripts/check.sh does those.
set -euo pipefail
cd "$(dirname "$0")/.."

LINT="${QUICK_LINT:-<LINT_COMMAND>}"         # e.g. npm run lint | flutter analyze | ruff check . | cargo clippy -- -D warnings
TYPES="${QUICK_TYPES:-<TYPECHECK_COMMAND>}"  # e.g. npx tsc --noEmit | mypy src | true (when lint already covers types)

start=$SECONDS
finished=0
trap '[ "$finished" = 1 ] || echo "quick-check: FAIL (script error, see above)"' EXIT
fail() { finished=1; echo "quick-check: FAIL ($1)"; exit 1; }

case "$LINT$TYPES" in *"<"*">"*) fail "placeholders not filled: set LINT and TYPES in scripts/quick-check.sh" ;; esac
[ -f package.json ] && [ ! -d node_modules ] && fail "deps missing: run npm ci"
[ -f pubspec.yaml ] && [ ! -d .dart_tool ] && fail "deps missing: run flutter pub get"
[ -f pyproject.toml ] && [ -n "${VIRTUAL_ENV:-}" ] && [ ! -d "$VIRTUAL_ENV" ] && fail "deps missing: create the virtualenv"

failed=""
bash -c "$LINT" || failed="lint"
bash -c "$TYPES" || failed="${failed:+$failed, }types"
[ -z "$failed" ] || fail "$failed"

finished=1
echo "quick-check: OK (lint + types, $((SECONDS - start))s)"
