#!/usr/bin/env bash
# Session start: install, verify the environment works, say how to run the app. Every session begins here,
# so an agent never starts work on a machine that cannot run the checks. Fill the two commands.
set -euo pipefail
cd "$(dirname "$0")/.."

INSTALL="${INIT_INSTALL:-<INSTALL_COMMAND>}"  # e.g. npm ci | flutter pub get | uv sync
DEV="${INIT_DEV:-<DEV_COMMAND>}"              # e.g. npm run dev | flutter run

case "$INSTALL$DEV" in *"<"*">"*) echo "init: FAIL (placeholders not filled: set INSTALL and DEV in scripts/init.sh)"; exit 1 ;; esac

bash -c "$INSTALL"
scripts/quick-check.sh
echo "init: OK (dependencies installed, quick check green). Start the app with: $DEV"
