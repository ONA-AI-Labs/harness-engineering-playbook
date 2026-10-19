load helpers

audit() { python3 "$ROOT/tools/audit-harness.py" "$@"; }

level1_repo() { # a map that names its check, with an executable quick check
  mkdir -p "$1/scripts"
  printf '# Thing\n\nThis service turns uploaded files into searchable records for the web and mobile apps.\n\n## Commands\n- `scripts/quick-check.sh` lint and types\n- `npm test`\n' > "$1/CLAUDE.md"
  printf '#!/usr/bin/env bash\necho ok\n' > "$1/scripts/quick-check.sh"; chmod +x "$1/scripts/quick-check.sh"
}
level2_extras() {
  mkdir -p "$1/.claude"
  printf '{"permissions":{"allow":["Bash(scripts/quick-check.sh)"]}}' > "$1/.claude/settings.json"
  printf '\n## Done means\n- `npm test`, then `npm run build` and run the built app once.\n' >> "$1/CLAUDE.md"
}
hooks_file() { # a workspace settings file whose scripts are the real ones
  mkdir -p "$1/.claude"
  printf '{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[{"type":"command","command":"python3 \\"$CLAUDE_PROJECT_DIR/hooks/guard-destructive.py\\""}]}],"Stop":[{"hooks":[{"type":"command","command":"python3 \\"$CLAUDE_PROJECT_DIR/hooks/stop-quick-check.py\\""}]}]}}' > "$1/.claude/settings.json"
  ln -s "$HOOKS" "$1/hooks"
}
level3_extras() {
  mkdir -p "$1/docs/agent" "$1/.github/workflows"
  echo '# Topic' > "$1/docs/agent/topic.md"
  printf 'on: [pull_request]\njobs:\n  check:\n    steps:\n      - run: npx eslint src --max-warnings 0\n' > "$1/.github/workflows/ci.yml"
  printf '\n## Hard rules\n| Rule | Enforced by |\n|---|---|\n| Never log tokens | tests/no-token-logs.test.ts |\n| Keep layers apart | prose, no enforcer yet |\n' >> "$1/CLAUDE.md"
}

@test "an empty folder is level 0" {
  mkdir -p "$BATS_TEST_TMPDIR/r0"
  run audit "$BATS_TEST_TMPDIR/r0"
  [[ "$output" == *"Level reached: 0"* ]]
}

@test "a map plus an executable quick check is level 1" {
  level1_repo "$BATS_TEST_TMPDIR/r1"
  run audit "$BATS_TEST_TMPDIR/r1"
  [[ "$output" == *"Level reached: 1"* ]]; [[ "$output" == *"[N/A ] L1 lockfile"* ]]
}

@test "hooks from a workspace file, an allow list and a done section reach level 2" {
  level1_repo "$BATS_TEST_TMPDIR/r2"; level2_extras "$BATS_TEST_TMPDIR/r2"; hooks_file "$BATS_TEST_TMPDIR/ws"
  run audit "$BATS_TEST_TMPDIR/r2" --hooks-file "$BATS_TEST_TMPDIR/ws/.claude/settings.json"
  [[ "$output" == *"Level reached: 2"* ]]
  run audit "$BATS_TEST_TMPDIR/r2"
  [[ "$output" == *"Level reached: 1"* ]]
}

@test "docs, a CI debt gate, enforced rules and a metrics hook reach level 3; --min-level gates" {
  level1_repo "$BATS_TEST_TMPDIR/r3"; level2_extras "$BATS_TEST_TMPDIR/r3"; hooks_file "$BATS_TEST_TMPDIR/ws"; level3_extras "$BATS_TEST_TMPDIR/r3"
  run audit "$BATS_TEST_TMPDIR/r3" --hooks-file "$BATS_TEST_TMPDIR/ws/.claude/settings.json" --json
  [ "$status" -eq 0 ]; [[ "$output" == *'"level": 3'* ]]
  run audit "$BATS_TEST_TMPDIR/r3" --hooks-file "$BATS_TEST_TMPDIR/ws/.claude/settings.json" --min-level 4
  [ "$status" -eq 1 ]
}

@test "a not-applicable declaration counts as passed" {
  level1_repo "$BATS_TEST_TMPDIR/r4"; level2_extras "$BATS_TEST_TMPDIR/r4"; hooks_file "$BATS_TEST_TMPDIR/ws"
  perl -pi -e 's/, then `npm run build` and run the built app once//' "$BATS_TEST_TMPDIR/r4/CLAUDE.md"
  run audit "$BATS_TEST_TMPDIR/r4" --hooks-file "$BATS_TEST_TMPDIR/ws/.claude/settings.json"
  [[ "$output" == *"Level reached: 1"* ]]
  mkdir -p "$BATS_TEST_TMPDIR/r4/.harness"; echo '{"not_applicable":{"ship_check":"library, nothing to boot"}}' > "$BATS_TEST_TMPDIR/r4/.harness/audit.json"
  run audit "$BATS_TEST_TMPDIR/r4" --hooks-file "$BATS_TEST_TMPDIR/ws/.claude/settings.json"
  [[ "$output" == *"Level reached: 2"* ]]; [[ "$output" == *"library, nothing to boot"* ]]
}

@test "a one-line CLAUDE.md that imports AGENTS.md is read through the import; a Makefile target counts as the check" {
  mkdir -p "$BATS_TEST_TMPDIR/r5"; cd "$BATS_TEST_TMPDIR/r5"
  printf '@AGENTS.md\n' > CLAUDE.md
  printf '# Thing\n\nThis service turns uploaded files into searchable records for the web and mobile apps.\n\n## Commands\n- `make quick` lint and types\n' > AGENTS.md
  printf 'quick:\n\t@echo ok\n' > Makefile
  run python3 "$ROOT/tools/audit-harness.py" .
  [[ "$output" == *"Level reached: 1"* ]]; [[ "$output" == *"Makefile targets: quick"* ]]
}
