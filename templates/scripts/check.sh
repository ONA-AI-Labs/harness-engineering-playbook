#!/usr/bin/env bash
# Full check, the definition of done: quick check, tests, build, then boot the built artifact.
# Copy to scripts/check.sh and fill the commands (or export CHECK_TEST, CHECK_BUILD, CHECK_BOOT).
set -euo pipefail
cd "$(dirname "$0")/.."

TEST="${CHECK_TEST:-<TEST_COMMAND>}"     # e.g. npm test | flutter test | pytest -q
BUILD="${CHECK_BUILD:-<BUILD_COMMAND>}"  # e.g. npm run build | flutter build apk --debug | cargo build --release
BOOT="${CHECK_BOOT:-scripts/boot-check.sh}"

start=$SECONDS
finished=0
trap '[ "$finished" = 1 ] || echo "check: FAIL (script error, see above)"' EXIT
fail() { finished=1; echo "check: FAIL ($1)"; exit 1; }

case "$TEST$BUILD" in *"<"*">"*) fail "placeholders not filled: set TEST and BUILD in scripts/check.sh" ;; esac

scripts/quick-check.sh || fail "quick check"
bash -c "$TEST" || fail "tests"
bash -c "$BUILD" || fail "build"
if [ -x "$BOOT" ]; then
  "$BOOT" || fail "boot check"
  boot="boot"
else
  boot="boot skipped: no $BOOT"
fi

finished=1
echo "check: OK (quick, tests, build, $boot, $((SECONDS - start))s)"
