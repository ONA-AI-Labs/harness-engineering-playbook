#!/usr/bin/env bash
# Boot check: start the built artifact, wait for a health signal, stop it. Unit tests run your sources;
# this proves the thing you ship starts. Copy to scripts/boot-check.sh and fill the two values
# (or export BOOT_START and BOOT_HEALTH_URL). Run it after the build, with placeholder credentials.
set -euo pipefail
cd "$(dirname "$0")/.."

START="${BOOT_START:-<START_COMMAND>}"        # e.g. node dist/server.js | java -jar build/app.jar | ./target/release/app
HEALTH="${BOOT_HEALTH_URL:-<HEALTH_URL>}"     # e.g. http://127.0.0.1:3000/health
TIMEOUT="${BOOT_TIMEOUT:-30}"

case "$START$HEALTH" in *"<"*">"*) echo "boot-check: FAIL (placeholders not filled: set START and HEALTH in scripts/boot-check.sh)"; exit 1 ;; esac

bash -c "$START" >/tmp/boot-check.log 2>&1 &
pid=$!
trap 'pkill -P "$pid" 2>/dev/null || true; kill "$pid" 2>/dev/null || true' EXIT

for ((i = 1; i <= TIMEOUT; i++)); do
  if curl -fsS --max-time 2 "$HEALTH" >/dev/null 2>&1; then
    echo "boot-check: OK (healthy after ${i}s)"
    exit 0
  fi
  if ! kill -0 "$pid" 2>/dev/null; then
    tail -20 /tmp/boot-check.log
    echo "boot-check: FAIL (process exited before answering $HEALTH)"
    exit 1
  fi
  sleep 1
done
tail -20 /tmp/boot-check.log
echo "boot-check: FAIL (no health response from $HEALTH in ${TIMEOUT}s)"
exit 1
