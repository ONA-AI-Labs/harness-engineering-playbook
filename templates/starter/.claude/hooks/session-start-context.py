#!/usr/bin/env python3
"""SessionStart hook: tell the agent where the repo stands before its first prompt.

Prints additionalContext with the branch, the number of uncommitted files, the
head of docs/PROGRESS.md (first 25 lines) and the check command. Fails silently.
"""
import json
import os
import subprocess
import sys
from pathlib import Path


def git(args, cwd):
    try:
        return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def main():
    data = json.load(sys.stdin)
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd())
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    changed = [l for l in git(["status", "--porcelain"], root).splitlines() if l.strip()]
    lines = ["Repo state: branch %s, %d uncommitted file(s)." % (branch or "?", len(changed))]
    progress = root / "docs" / "PROGRESS.md"
    if progress.is_file():
        lines.append("docs/PROGRESS.md (head):")
        lines.extend(progress.read_text(errors="replace").splitlines()[:25])
    if (root / "scripts" / "quick-check.sh").is_file():
        lines.append("Quick check: scripts/quick-check.sh (it runs before you stop).")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "\n".join(lines)}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
