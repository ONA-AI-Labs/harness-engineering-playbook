load helpers

@test "quick-check fails on unfilled placeholders, passes with green commands, fails with a red one" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/scripts; cp "$SCRIPTS/quick-check.sh" r/scripts/
  run r/scripts/quick-check.sh; [ "$status" -eq 1 ]; [[ "$output" == *'placeholders not filled'* ]]
  run env QUICK_LINT=true QUICK_TYPES=true r/scripts/quick-check.sh; [ "$status" -eq 0 ]; [[ "${output##*$'\n'}" == quick-check:\ OK* ]]
  run env QUICK_LINT=false QUICK_TYPES=true r/scripts/quick-check.sh; [ "$status" -eq 1 ]; [[ "${output##*$'\n'}" == 'quick-check: FAIL (lint)' ]]
}

@test "check.sh runs quick check, tests and build, and skips a missing boot check honestly" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/scripts; cp "$SCRIPTS/quick-check.sh" "$SCRIPTS/check.sh" r/scripts/
  run env QUICK_LINT=true QUICK_TYPES=true CHECK_TEST=true CHECK_BUILD=true r/scripts/check.sh
  [ "$status" -eq 0 ]; [[ "${output##*$'\n'}" == *'boot skipped'* ]]
  run env QUICK_LINT=true QUICK_TYPES=true CHECK_TEST=false CHECK_BUILD=true r/scripts/check.sh
  [ "$status" -eq 1 ]; [[ "${output##*$'\n'}" == 'check: FAIL (tests)' ]]
}

@test "boot-check waits for a health signal and stops the process" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/scripts; cp "$SCRIPTS/boot-check.sh" r/scripts/
  port=$((20000 + RANDOM % 20000))
  run env BOOT_START="python3 -m http.server $port --bind 127.0.0.1" BOOT_HEALTH_URL="http://127.0.0.1:$port/" BOOT_TIMEOUT=15 r/scripts/boot-check.sh
  [ "$status" -eq 0 ]; [[ "${output##*$'\n'}" == boot-check:\ OK* ]]
  ! curl -fsS --max-time 1 "http://127.0.0.1:$port/" >/dev/null 2>&1
  run env BOOT_START="true" BOOT_HEALTH_URL="http://127.0.0.1:$port/" BOOT_TIMEOUT=3 r/scripts/boot-check.sh
  [ "$status" -eq 1 ]; [[ "${output##*$'\n'}" == *'process exited'* ]]
}

@test "ratchet passes at the baseline, fails above it, asks to lower it below, and hard-fails a crashed checker" {
  run "$SCRIPTS/ratchet.sh" --name lint --max 2 -- bash -c 'echo "a: error x"; echo "b: error y"; exit 1'; [ "$status" -eq 0 ]; [[ "$output" == *'2 of 2'* ]]
  run "$SCRIPTS/ratchet.sh" --name lint --max 1 -- bash -c 'echo "a: error x"; echo "b: error y"; exit 1'; [ "$status" -eq 1 ]; [[ "$output" == *'over the baseline'* ]]
  run "$SCRIPTS/ratchet.sh" --name lint --max 5 -- bash -c 'echo "a: error x"; exit 0'; [ "$status" -eq 0 ]; [[ "$output" == *'lower --max to 1'* ]]
  run "$SCRIPTS/ratchet.sh" --name lint --max 5 -- bash -c 'echo crashed; exit 2'; [ "$status" -eq 2 ]; [[ "$output" == *'crashed checker'* ]]
}

@test "arch-check reports WHAT/WHY/FIX for a forbidden import and respects the allow list" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/.harness r/src/controllers; cd r
  printf '{"rules":[{"name":"controllers never import the db","paths":["src/controllers"],"forbid":"from .*db","allow":["src/controllers/ok.ts"],"why":"data access lives in services","fix":"call a service"}]}' > .harness/arch-rules.json
  echo 'import { db } from "../db";' > src/controllers/bad.ts; echo 'import { db } from "../db";' > src/controllers/ok.ts
  run python3 "$SCRIPTS/arch-check.py"; [ "$status" -eq 1 ]
  [[ "$output" == *'WHAT: controllers never import the db at src/controllers/bad.ts:1'* ]]; [[ "$output" == *'FIX:  call a service'* ]]; [[ "$output" != *'ok.ts'* ]]
  rm src/controllers/bad.ts; run python3 "$SCRIPTS/arch-check.py"; [ "$status" -eq 0 ]
}

@test "verify-feature flips passes only through the script and records evidence" {
  cd "$BATS_TEST_TMPDIR"; printf '{"features":[{"id":"f1","description":"a feature here","priority":1,"verify":"test -f ok.txt","passes":false,"evidence":null}]}' > feature_list.json
  run python3 "$SCRIPTS/verify-feature.py" f1; [ "$status" -eq 1 ]; grep -q '"passes": false' feature_list.json
  touch ok.txt; run python3 "$SCRIPTS/verify-feature.py" f1; [ "$status" -eq 0 ]; grep -q '"passes": true' feature_list.json; grep -q '"command": "test -f ok.txt"' feature_list.json
  run python3 "$SCRIPTS/verify-feature.py" nope; [ "$status" -eq 2 ]
}

@test "clean-state-check fails on dirty trees, leftover markers and a progress file without Next" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/scripts r/docs; cd r; git init -q; cp "$SCRIPTS/clean-state-check.sh" scripts/
  printf '# P\n\n## Next\n1. x\n' > docs/PROGRESS.md; git add -A; git -c user.email=t@t -c user.name=t commit -qm init
  run scripts/clean-state-check.sh; [ "$status" -eq 0 ]
  echo 'x // TEMP-VERIFY' > hack.ts; git add hack.ts; git -c user.email=t@t -c user.name=t commit -qm hack
  run scripts/clean-state-check.sh; [ "$status" -eq 1 ]; [[ "$output" == *'leftover markers'* ]]
  git rm -q hack.ts; printf '# P\n' > docs/PROGRESS.md; git -c user.email=t@t -c user.name=t commit -qam fix
  run scripts/clean-state-check.sh; [ "$status" -eq 1 ]; [[ "$output" == *'no Next section'* ]]
  echo dirty > d.txt; run scripts/clean-state-check.sh; [[ "$output" == *'uncommitted changes'* ]]
  run scripts/clean-state-check.sh --allow-dirty; [[ "$output" != *'uncommitted'* ]]
}

@test "run-evals runs each task in a fresh worktree with a fake agent and compare-results shows deltas" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/evals; cd r; git init -q; echo base > base.txt; git add -A; git -c user.email=t@t -c user.name=t commit -qm init
  printf '{"id":"t1","prompt":"make done","verify":"test -f done.txt"}\n{"id":"t2","prompt":"x","verify":"test -f never.txt"}\n' > evals/tasks.jsonl
  run python3 "$ROOT/templates/evals/run-evals.py" --agent "touch done.txt && echo {prompt}" --out evals/before.jsonl
  [ "$status" -eq 0 ]; [[ "$output" == *'1/2 passed'* ]]; [ ! -f done.txt ]
  run python3 "$ROOT/templates/evals/run-evals.py" --agent "touch done.txt never.txt" --out evals/after.jsonl --min-pass 1.0; [ "$status" -eq 0 ]
  run python3 "$ROOT/templates/evals/compare-results.py" evals/before.jsonl evals/after.jsonl; [ "$status" -eq 0 ]; [[ "$output" == *'t2'*'fixed'* ]]
}

@test "the starter kit stays byte-identical to the full templates" {
  cd "$ROOT/templates"
  cmp starter/AGENTS.md AGENTS.md; cmp starter/CLAUDE.md CLAUDE.md; cmp starter/scripts/quick-check.sh scripts/quick-check.sh
  cmp starter/.claude/settings.json hooks/claude-code/settings.json; cmp starter/.claude/hooks/guard-destructive.py hooks/scripts/guard-destructive.py
  cmp starter/.claude/hooks/require-check-before-stop.py hooks/scripts/require-check-before-stop.py
  cmp starter/docs/definition-of-done.md docs/definition-of-done.md; cmp starter/docs/PROGRESS.md docs/PROGRESS.md
}

@test "the starter kit also ships check.sh, the tracker and the session context, byte-identical" {
  cd "$ROOT/templates"
  cmp starter/scripts/check.sh scripts/check.sh; cmp starter/.claude/hooks/track-touched.py hooks/scripts/track-touched.py
  cmp starter/.claude/hooks/session-start-context.py hooks/scripts/session-start-context.py
}

@test "the starter kit, filled in as its guide says, audits at level 2 with every hook script present" {
  mkdir -p "$BATS_TEST_TMPDIR/kit"; cp -R "$ROOT/templates/starter/." "$BATS_TEST_TMPDIR/kit/"; cd "$BATS_TEST_TMPDIR/kit"
  perl -pi -e 's/<LINT_COMMAND>/true/; s/<TYPECHECK_COMMAND>/true/' scripts/quick-check.sh
  perl -pi -e 's/<TEST_COMMAND>/true/; s/<BUILD_COMMAND>/true/' scripts/check.sh .claude/settings.json
  perl -pi -e 's/<PROJECT_NAME>/Thing/; s/<ONE_PARAGRAPH:[^>]*>/This service turns uploaded files into searchable records for the web and mobile apps./' AGENTS.md
  run python3 "$ROOT/tools/audit-harness.py" .
  [[ "$output" == *"Level reached: 2"* ]]; [[ "$output" == *"scripts present"* ]]
  rm .claude/hooks/track-touched.py
  run python3 "$ROOT/tools/audit-harness.py" .
  [[ "$output" == *"hook scripts missing"* ]]
}

@test "init.sh refuses placeholders and runs install then the quick check" {
  cd "$BATS_TEST_TMPDIR"; mkdir -p r/scripts; cp "$SCRIPTS/init.sh" "$SCRIPTS/quick-check.sh" r/scripts/
  run r/scripts/init.sh; [ "$status" -eq 1 ]; [[ "$output" == *'placeholders not filled'* ]]
  run env INIT_INSTALL=true INIT_DEV="echo dev" QUICK_LINT=true QUICK_TYPES=true r/scripts/init.sh
  [ "$status" -eq 0 ]; [[ "${output##*$'\n'}" == init:\ OK* ]]
}

@test "harness-stats summarises a metrics file" {
  printf '{"ts": 1, "event": "PreToolUse", "decision": "deny", "reason": "r", "subject": "git push --force"}\n{"ts": 2, "event": "Stop", "status": "ok", "repo": "/x"}\n' > "$BATS_TEST_TMPDIR/m.jsonl"
  run python3 "$ROOT/tools/harness-stats.py" "$BATS_TEST_TMPDIR/m.jsonl"
  [ "$status" -eq 0 ]; [[ "$output" == *"2 events"* ]]; [[ "$output" == *"deny"* ]]
}
