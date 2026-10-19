#!/usr/bin/env bash
# Clean-state check for the end of a session: nothing half-done is left for the next one.
#   scripts/clean-state-check.sh [--allow-dirty]
# Fails on uncommitted changes (unless --allow-dirty), on leftover verification markers in tracked
# files, and on a progress file without a "Next" section. Exit code is the verdict.
set -euo pipefail
cd "$(dirname "$0")/.."

allow_dirty=0; [ "${1:-}" = "--allow-dirty" ] && allow_dirty=1
problems=""

if [ "$allow_dirty" = 0 ] && [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  git status --short | head -20
  problems="uncommitted changes"
fi

markers=$(git grep -n -E 'TEMP-VERIFY|TODO-VERIFY|XXX-REMOVE|DO NOT COMMIT' -- . ':!scripts/clean-state-check.sh' 2>/dev/null || true)
if [ -n "$markers" ]; then
  printf '%s\n' "$markers" | head -20
  problems="${problems:+$problems, }leftover markers"
fi

if [ -f docs/PROGRESS.md ] && ! grep -qiE '^##+ *next' docs/PROGRESS.md; then
  problems="${problems:+$problems, }docs/PROGRESS.md has no Next section"
fi

if [ -n "$problems" ]; then
  echo "clean-state: FAIL ($problems)"
  exit 1
fi
echo "clean-state: OK"
