#!/usr/bin/env python3
"""Summarise ~/.claude/metrics/harness.jsonl: did the harness fire, and on what?"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".claude" / "metrics" / "harness.jsonl"
if not path.is_file():
    print("no metrics yet at %s" % path)
    sys.exit(0)
rows = []
for line in path.read_text().splitlines():
    try:
        rows.append(json.loads(line))
    except ValueError:
        continue
counts = Counter((r.get("event"), r.get("decision") or r.get("status")) for r in rows)
print("%d events in %s" % (len(rows), path))
for (event, outcome), n in sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0]))):
    print("  %-12s %-8s %d" % (event, outcome, n))
notable = [r for r in rows if (r.get("decision") in ("deny", "ask")) or (r.get("status") in ("fail", "timeout"))]
if notable:
    print("last %d interventions:" % min(5, len(notable)))
    for r in notable[-5:]:
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(r.get("ts", 0)))
        what = r.get("subject") or r.get("repo") or ""
        print("  %s %-10s %-5s %s  %s" % (when, r.get("event"), r.get("decision") or r.get("status"), what[:60], r.get("reason") or r.get("summary") or ""))
