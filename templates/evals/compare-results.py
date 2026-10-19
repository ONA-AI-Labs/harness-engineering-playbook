#!/usr/bin/env python3
"""Compare two eval runs task by task: python3 evals/compare-results.py before.jsonl after.jsonl"""
import json
import sys


def load(path):
    return {r["id"]: r for r in (json.loads(l) for l in open(path) if l.strip())}


def main(before_path, after_path):
    before, after = load(before_path), load(after_path)
    print("%-30s %-8s %-8s %s" % ("task", "before", "after", "change"))
    better = worse = 0
    for task_id in sorted(set(before) | set(after)):
        b = before.get(task_id, {}).get("status", "-")
        a = after.get(task_id, {}).get("status", "-")
        change = ""
        if b != a:
            change = "fixed" if a == "pass" else ("regressed" if b == "pass" else "changed")
            better += a == "pass"
            worse += b == "pass" and a != "pass"
        print("%-30s %-8s %-8s %s" % (task_id, b, a, change))
    bp = sum(1 for r in before.values() if r["status"] == "pass")
    ap = sum(1 for r in after.values() if r["status"] == "pass")
    print("pass rate %d/%d -> %d/%d (%d fixed, %d regressed)" % (bp, len(before), ap, len(after), better, worse))
    return 1 if worse else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
