#!/usr/bin/env python3
"""PostToolUse (Edit|Write|MultiEdit|NotebookEdit): remember which files this session edited.

require-check-before-stop.py reads the list at stop time and runs the check only
in the repos that were touched. Always exits 0.
shortcut: edits made through shell commands (sed -i, heredocs) are not seen here.
"""
import json
import os
import re
import sys
from pathlib import Path

METRICS_DIR = Path(os.environ.get("HARNESS_METRICS_DIR") or (Path.home() / ".claude" / "metrics"))


def main():
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not path:
        return
    session = re.sub(r"[^A-Za-z0-9_-]", "_", str(data.get("session_id") or "unknown"))
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    with (METRICS_DIR / ("touched-%s.txt" % session)).open("a") as handle:
        handle.write(path + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
