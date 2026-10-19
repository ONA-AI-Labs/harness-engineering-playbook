# Shared setup for the bats suites: an isolated HOME and metrics folder so tests never touch a real one.
setup() {
  export ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export HOME="$BATS_TEST_TMPDIR/home"; mkdir -p "$HOME"
  export HARNESS_METRICS_DIR="$HOME/.claude/metrics"; export HARNESS_METRICS_FILE="$HARNESS_METRICS_DIR/harness.jsonl"
  export HOOKS="$ROOT/templates/hooks/scripts"; export SCRIPTS="$ROOT/templates/scripts"
  export CLAUDE_PROJECT_DIR="$BATS_TEST_TMPDIR/ws"; mkdir -p "$CLAUDE_PROJECT_DIR"
}
guard() { python3 "$HOOKS/guard-destructive.py"; }
bash_event() { python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":"Bash","cwd":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$1" "$2"; }
file_event() { python3 -c 'import json,sys; print(json.dumps({"session_id":"t","tool_name":sys.argv[1],"tool_input":{"file_path":sys.argv[2]}}))' "$1" "$2"; }
make_repo() { # make_repo <dir> <quick-check exit code>
  mkdir -p "$1/scripts"
  printf '#!/usr/bin/env bash\necho "quick-check: %s (lint)"\nexit %s\n' "$([ "$2" = 0 ] && echo OK || echo FAIL)" "$2" > "$1/scripts/quick-check.sh"
  chmod +x "$1/scripts/quick-check.sh"
}
