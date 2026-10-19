load helpers

@test "a failing check blocks the stop once, then lets it through with a message" {
  make_repo "$BATS_TEST_TMPDIR/bad" 1
  printf '{"session_id":"s","tool_name":"Edit","tool_input":{"file_path":"%s/bad/a.ts"}}' "$BATS_TEST_TMPDIR" | python3 "$HOOKS/track-touched.py"
  run bash -c "echo '{\"session_id\":\"s\"}' | python3 \"$HOOKS/require-check-before-stop.py\""
  [[ "$output" == *'"decision": "block"'* ]]; [[ "$output" == *'bad: quick-check: FAIL (lint)'* ]]
  run bash -c "echo '{\"session_id\":\"s\"}' | python3 \"$HOOKS/require-check-before-stop.py\""
  [[ "$output" == *'systemMessage'* ]]; [[ "$output" != *'"block"'* ]]
}

@test "a passing check is silent and clears the touched list" {
  make_repo "$BATS_TEST_TMPDIR/good" 0
  printf '{"session_id":"s","tool_name":"Write","tool_input":{"file_path":"%s/good/lib/x.dart"}}' "$BATS_TEST_TMPDIR" | python3 "$HOOKS/track-touched.py"
  run bash -c "echo '{\"session_id\":\"s\"}' | python3 \"$HOOKS/require-check-before-stop.py\""
  [ "$status" -eq 0 ]; [ -z "$output" ]; [ ! -f "$HARNESS_METRICS_DIR/touched-s.txt" ]
}

@test "without a touched list it checks the project dir only when it is dirty, with a custom command" {
  cd "$CLAUDE_PROJECT_DIR"; git init -q; printf 'quick:\n\t@echo "lint ok"\n' > Makefile; git add Makefile; git -c user.email=t@t -c user.name=t commit -qm init
  run bash -c "echo '{\"session_id\":\"d\"}' | python3 \"$HOOKS/require-check-before-stop.py\" --command 'make quick' --root-marker Makefile"
  [ -z "$output" ]
  echo change > file.txt
  run bash -c "echo '{\"session_id\":\"d\"}' | python3 \"$HOOKS/require-check-before-stop.py\" --command 'exit 3' --root-marker Makefile"
  [[ "$output" == *'"block"'* ]]
}

@test "stop_hook_active and missing lists pass silently; session context prints the branch" {
  run bash -c "echo '{\"session_id\":\"s\",\"stop_hook_active\":true}' | python3 \"$HOOKS/require-check-before-stop.py\""; [ -z "$output" ]
  run bash -c "echo '{\"session_id\":\"none\"}' | python3 \"$HOOKS/require-check-before-stop.py\""; [ -z "$output" ]
  cd "$CLAUDE_PROJECT_DIR"; git init -q; mkdir -p docs; printf '# Progress\n\n## Next\n1. thing\n' > docs/PROGRESS.md
  run bash -c "echo '{\"session_id\":\"s\"}' | python3 \"$HOOKS/session-start-context.py\""
  [[ "$output" == *'additionalContext'* ]]; [[ "$output" == *'Next'* ]]
}
