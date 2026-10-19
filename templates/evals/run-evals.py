#!/usr/bin/env python3
"""Run every task in tasks.jsonl through an agent in a fresh copy of the repo, verify, and record results.

  python3 evals/run-evals.py [--tasks evals/tasks.jsonl] [--agent "claude -p {prompt} --permission-mode acceptEdits"]
                            [--repo .] [--out evals/results.jsonl] [--timeout 900] [--min-pass 0.0]

  {prompt} in --agent is replaced by the shell-quoted task prompt. Each task runs in its own git worktree
  (or a copy when the repo is not a git checkout) so runs never share state. The verify command decides
  pass or fail: deterministic first, an LLM judge (judge-rubric.md) only where you need nuance.
  Exit 0 unless the pass rate is below --min-pass. Keep 20-50 tasks drawn from real failures.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


def parse(argv):
    opts = {"tasks": "evals/tasks.jsonl", "agent": "claude -p {prompt} --permission-mode acceptEdits", "repo": ".",
            "out": "evals/results.jsonl", "timeout": 900, "min_pass": 0.0}
    i = 0
    while i < len(argv):
        key = argv[i].lstrip("-").replace("-", "_")
        if key in opts:
            opts[key] = type(opts[key])(argv[i + 1]); i += 2
        else:
            print("unknown option %s" % argv[i]); sys.exit(2)
    return opts


def fresh_copy(repo, task_id):
    target = os.path.join(tempfile.mkdtemp(prefix="eval-"), task_id)
    if os.path.isdir(os.path.join(repo, ".git")):
        done = subprocess.run(["git", "-C", repo, "worktree", "add", "--detach", target, "HEAD"], capture_output=True, text=True)
        if done.returncode == 0:
            return target, True
    shutil.copytree(repo, target, ignore=shutil.ignore_patterns(".git", "node_modules", "dist", "build", ".dart_tool"))
    return target, False


def cleanup(repo, target, is_worktree):
    if is_worktree:
        subprocess.run(["git", "-C", repo, "worktree", "remove", "--force", target], capture_output=True)
    shutil.rmtree(os.path.dirname(target), ignore_errors=True)


def main(argv):
    opts = parse(argv)
    tasks = [json.loads(l) for l in open(opts["tasks"]) if l.strip()]
    results = []
    for task in tasks:
        target, is_worktree = fresh_copy(os.path.abspath(opts["repo"]), task["id"])
        started = time.time()
        agent_cmd = opts["agent"].replace("{prompt}", shlex.quote(task["prompt"]))
        status = "fail"
        try:
            subprocess.run(["bash", "-lc", agent_cmd], cwd=target, capture_output=True, text=True, timeout=opts["timeout"])
            verify = subprocess.run(["bash", "-lc", task["verify"]], cwd=target, capture_output=True, text=True, timeout=opts["timeout"])
            status = "pass" if verify.returncode == 0 else "fail"
            tail = "\n".join((verify.stdout + verify.stderr).splitlines()[-5:])
        except subprocess.TimeoutExpired:
            status, tail = "timeout", ""
        results.append({"id": task["id"], "status": status, "seconds": round(time.time() - started, 1), "tail": tail,
                        "agent": opts["agent"], "date": time.strftime("%Y-%m-%d")})
        print("%-30s %-8s %6.1fs" % (task["id"], status, results[-1]["seconds"]))
        cleanup(os.path.abspath(opts["repo"]), target, is_worktree)
    os.makedirs(os.path.dirname(opts["out"]) or ".", exist_ok=True)
    with open(opts["out"], "w") as handle:
        for row in results:
            handle.write(json.dumps(row) + "\n")
    passed = sum(1 for r in results if r["status"] == "pass")
    rate = passed / len(results) if results else 0.0
    print("evals: %d/%d passed (%.0f%%) -> %s" % (passed, len(results), rate * 100, opts["out"]))
    return 0 if rate >= opts["min_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
