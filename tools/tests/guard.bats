load helpers

@test "force-push to main is denied; other force-pushes and hard resets ask" {
  run bash -c "$(declare -f guard bash_event); bash_event 'git push --force origin main' /tmp | guard"
  [ "$status" -eq 0 ]; [[ "$output" == *'"permissionDecision": "deny"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'git push -f origin feature/x' /tmp | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'git reset --hard HEAD~1' /tmp | guard"; [[ "$output" == *'"ask"'* ]]
}

@test "normal commands and removing a build folder inside the workspace pass silently" {
  mkdir -p "$CLAUDE_PROJECT_DIR/repo"
  run bash -c "$(declare -f guard bash_event); bash_event 'npm test && rm -rf node_modules' $CLAUDE_PROJECT_DIR/repo | guard"
  [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "recursive delete outside the workspace is denied, inside a source folder asks, in temp passes" {
  mkdir -p "$CLAUDE_PROJECT_DIR/repo/src"
  run bash -c "$(declare -f guard bash_event); bash_event 'rm -rf /Users/someone/Documents' $CLAUDE_PROJECT_DIR/repo | guard"; [[ "$output" == *'"deny"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'rm -rf src' $CLAUDE_PROJECT_DIR/repo | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'S=/tmp/scratch-abc; mkdir -p \$S/x && rm -rf \$S/x' $CLAUDE_PROJECT_DIR/repo | guard"; [ -z "$output" ]
  run bash -c "$(declare -f guard bash_event); bash_event 'rm -rf \$UNKNOWN_DIR/x' $CLAUDE_PROJECT_DIR/repo | guard"; [[ "$output" == *'cannot resolve that variable'* ]]
}

@test "database resets are denied; destructive SQL, merges, kubectl delete and publishes ask" {
  run bash -c "$(declare -f guard bash_event); bash_event 'supabase db push' /tmp | guard"; [[ "$output" == *'"deny"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'npx prisma migrate reset' /tmp | guard"; [[ "$output" == *'"deny"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'psql \$DB -c \"DROP TABLE users\"' /tmp | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'gh pr merge 12 --squash' /tmp | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'kubectl delete deployment api' /tmp | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'npm publish' /tmp | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard bash_event); bash_event 'terraform destroy -auto-approve' /tmp | guard"; [[ "$output" == *'"deny"'* ]]
}

@test "editing a .env file or an existing migration asks; .env.example and new files pass" {
  mkdir -p "$BATS_TEST_TMPDIR/db/migrations"; echo x > "$BATS_TEST_TMPDIR/db/migrations/001_init.sql"
  run bash -c "$(declare -f guard file_event); file_event Edit /x/.env.production | guard"; [[ "$output" == *'"ask"'* ]]
  run bash -c "$(declare -f guard file_event); file_event Edit /x/.env.example | guard"; [ -z "$output" ]
  run bash -c "$(declare -f guard file_event); file_event Edit $BATS_TEST_TMPDIR/db/migrations/001_init.sql | guard"; [[ "$output" == *'existing migration'* ]]
  run bash -c "$(declare -f guard file_event); file_event Write $BATS_TEST_TMPDIR/db/migrations/002_new.sql | guard"; [ -z "$output" ]
}

@test "heredoc bodies are data, not commands" {
  cmd=$'cat > notes.md <<\'EOF\'\nNever run rm -rf / or git push --force origin main.\nEOF\necho done'
  run bash -c "$(declare -f guard bash_event); bash_event \"\$1\" \"\$2\" | guard" _ "$cmd" "$CLAUDE_PROJECT_DIR"
  [ "$status" -eq 0 ]; [ -z "$output" ]
}

@test "garbage input exits 0 silently and is logged" {
  run bash -c "echo 'not json' | python3 \"$HOOKS/guard-destructive.py\""
  [ "$status" -eq 0 ]; [ -z "$output" ]; grep -q unparseable "$HARNESS_METRICS_FILE"
}

@test "the log never holds secrets: allow logs only the program, ask/deny log a redacted command, the file is private" {
  run bash -c "$(declare -f guard bash_event); bash_event 'curl -H \"Authorization: Bearer abc123SECRET\" https://api.example.com' /tmp | guard"
  [ -z "$output" ]; ! grep -q 'abc123SECRET' "$HARNESS_METRICS_FILE"; grep -q '"program": "curl"' "$HARNESS_METRICS_FILE"; ! grep -q '"subject"' "$HARNESS_METRICS_FILE"
  run bash -c "$(declare -f guard bash_event); bash_event 'psql postgres://app:p4ssw0rd@db.internal/x -c \"DROP TABLE users\"' /tmp | guard"
  [[ "$output" == *'"ask"'* ]]; ! grep -q 'p4ssw0rd' "$HARNESS_METRICS_FILE"; grep -q 'app:\[redacted\]@' "$HARNESS_METRICS_FILE"
  run bash -c "$(declare -f guard bash_event); bash_event 'API_KEY=sk-live-abcdefghijk git push --force origin main' /tmp | guard"
  [[ "$output" == *'"deny"'* ]]; ! grep -q 'abcdefghijk' "$HARNESS_METRICS_FILE"
  run bash -c "$(declare -f guard bash_event); HARNESS_LOG_COMMANDS=none; export HARNESS_LOG_COMMANDS; bash_event 'git reset --hard' /tmp | guard"
  [[ "$output" == *'"ask"'* ]]; ! grep -q 'git reset --hard' "$HARNESS_METRICS_FILE"
  [ "$(python3 -c 'import os,stat,sys; print(oct(stat.S_IMODE(os.stat(sys.argv[1]).st_mode)))' "$HARNESS_METRICS_FILE")" = "0o600" ]
}
