#!/usr/bin/env python3
"""Stop hook: run the quick check before the agent is allowed to stop.

usage in a hook: python3 .claude/hooks/require-check-before-stop.py [--command CMD] [--root-marker FILE] [--budget SECONDS]

  --command      what to run in each repo (default: scripts/quick-check.sh)
  --root-marker  the file that marks a repo root (default: the command's script path, else Makefile)
  --budget       total seconds for all repos (default 120)

Behaviour:
  - exits 0 at once when stop_hook_active is true (we are already continuing);
  - finds the repos to check: from the touched-files list written by track-touched.py
    when one exists, otherwise the project dir when it has uncommitted changes;
  - runs the command through a login shell so the user's PATH applies;
  - a failure blocks the stop ONCE with the command's last line as the reason; the
    same failure on the next stop lets it through with a systemMessage, so a
    pre-existing failure cannot trap the agent in a loop;
  - timeouts and missing tools pass with a systemMessage (fail open);
  - every run appends one line to the metrics file.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

METRICS_DIR = Path(os.environ.get("HARNESS_METRICS_DIR") or (Path.home() / ".claude" / "metrics"))
METRICS_FILE = Path(os.environ.get("HARNESS_METRICS_FILE") or (METRICS_DIR / "harness.jsonl"))


def log(record):
    try:
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with METRICS_FILE.open("a") as handle:
            handle.write(json.dumps(record) + "\n")
    except OSError:
        pass


def parse_args(argv):
    opts = {"command": "scripts/quick-check.sh", "root_marker": None, "budget": 120}
    i = 0
    while i < len(argv):
        if argv[i] == "--command":
            opts["command"] = argv[i + 1]; i += 2
        elif argv[i] == "--root-marker":
            opts["root_marker"] = argv[i + 1]; i += 2
        elif argv[i] == "--budget":
            opts["budget"] = int(argv[i + 1]); i += 2
        else:
            i += 1
    if not opts["root_marker"]:
        first = opts["command"].split()[0]
        opts["root_marker"] = first if "/" in first else "Makefile"
    return opts


def repo_for(path, marker):
    folder = Path(os.path.abspath(path)).parent
    while True:
        if (folder / marker).exists():
            return folder
        if folder.parent == folder:
            return None
        folder = folder.parent


def dirty(folder):
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=str(folder), capture_output=True, text=True, timeout=10)
        return out.returncode == 0 and bool(out.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        return False


def run_check(repo, command, seconds):
    shell = os.environ.get("SHELL") or "/bin/bash"
    started = time.time()
    try:
        proc = subprocess.run([shell, "-lc", command], cwd=str(repo), capture_output=True, text=True, timeout=seconds)
    except subprocess.TimeoutExpired:
        return "timeout", "%s: TIMEOUT after %ds" % (command, seconds), time.time() - started
    lines = [l for l in (proc.stdout + "\n" + proc.stderr).splitlines() if l.strip()]
    summary = lines[-1].strip() if lines else "%s: (no output)" % command
    return ("ok" if proc.returncode == 0 else "fail"), summary[:300], time.time() - started


def main(argv):
    opts = parse_args(argv)
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    session = re.sub(r"[^A-Za-z0-9_-]", "_", str(data.get("session_id") or "unknown"))
    touched_file = METRICS_DIR / ("touched-%s.txt" % session)
    state_file = METRICS_DIR / ("stop-state-%s.json" % session)
    repos = []
    if touched_file.is_file():
        for path in [l.strip() for l in touched_file.read_text().splitlines() if l.strip()]:
            repo = repo_for(path, opts["root_marker"])
            if repo and repo not in repos:
                repos.append(repo)
    else:
        project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd())
        if (project / opts["root_marker"]).exists() and dirty(project):
            repos.append(project)
    if not repos:
        if touched_file.is_file():
            touched_file.unlink()
        return
    deadline = time.time() + opts["budget"]
    results = []
    for repo in repos:
        remaining = int(deadline - time.time())
        if remaining < 5:
            results.append((repo, "timeout", "SKIPPED (stop-hook budget spent)", 0.0))
            continue
        status, summary, seconds = run_check(repo, opts["command"], remaining)
        results.append((repo, status, summary, seconds))
        log({"ts": time.time(), "event": "Stop", "session": session, "repo": str(repo), "status": status,
             "summary": summary, "seconds": round(seconds, 1)})
    failures = [(r, s) for r, st, s, _ in results if st == "fail"]
    timeouts = [r for r, st, _, _ in results if st == "timeout"]
    if failures:
        signature = "|".join("%s:%s" % (r, s) for r, s in failures)
        last = ""
        if state_file.is_file():
            try:
                last = json.loads(state_file.read_text()).get("signature", "")
            except ValueError:
                last = ""
        detail = "; ".join("%s: %s" % (r.name, s) for r, s in failures)
        if last == signature:
            print(json.dumps({"systemMessage": "Check still failing (%s); letting the stop through. Report it under 'Not verified'." % detail}))
            return
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"signature": signature}))
        print(json.dumps({"decision": "block", "reason": "Check failed in %s. Fix it if the failure is in files you changed; otherwise say so under 'Not verified' and stop." % detail}))
        return
    if touched_file.is_file():
        touched_file.unlink()
    if state_file.is_file():
        state_file.unlink()
    if timeouts:
        print(json.dumps({"systemMessage": "Check timed out in %s; not verified." % ", ".join(r.name for r in timeouts)}))


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as err:
        log({"ts": time.time(), "event": "Stop", "status": "error", "summary": repr(err)})
    sys.exit(0)
