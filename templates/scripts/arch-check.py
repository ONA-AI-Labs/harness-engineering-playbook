#!/usr/bin/env python3
"""Architecture check: forbidden patterns per folder, with WHAT / WHY / FIX messages an agent can act on.

Rules live in .harness/arch-rules.json:
{
  "rules": [
    {
      "name": "controllers never touch the database",
      "paths": ["src/controllers"],
      "forbid": "from ['\\"].*(db|prisma|knex)['\\"]",
      "allow": ["src/controllers/health.ts"],
      "why": "data access lives in services so it can be tested without HTTP",
      "fix": "call a service in src/services instead"
    }
  ]
}
A source-reading test like this is the cheapest architecture guard there is. Exit 1 on any hit.
"""
import json
import os
import re
import sys

SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".dart_tool", "target", "coverage", ".next", "vendor", "__pycache__"}


def main(root):
    rules_path = os.path.join(root, ".harness", "arch-rules.json")
    try:
        rules = json.load(open(rules_path)).get("rules", [])
    except (OSError, ValueError) as err:
        print("arch-check: FAIL (cannot read %s: %s)" % (rules_path, err))
        return 2
    hits = 0
    for rule in rules:
        pattern = re.compile(rule["forbid"])
        allow = {os.path.normpath(a) for a in rule.get("allow", [])}
        for base in rule.get("paths", ["."]):
            for folder, dirs, files in os.walk(os.path.join(root, base)):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in files:
                    path = os.path.join(folder, name)
                    rel = os.path.normpath(os.path.relpath(path, root))
                    if rel in allow or os.path.getsize(path) > 2_000_000:
                        continue
                    try:
                        lines = open(path, encoding="utf-8", errors="strict").read().splitlines()
                    except (OSError, UnicodeDecodeError):
                        continue
                    for number, line in enumerate(lines, 1):
                        if pattern.search(line):
                            hits += 1
                            print("WHAT: %s at %s:%d\nWHY:  %s\nFIX:  %s\n" % (rule["name"], rel, number, rule.get("why", ""), rule.get("fix", "")))
    if hits:
        print("arch-check: FAIL (%d violation%s)" % (hits, "" if hits == 1 else "s"))
        return 1
    print("arch-check: OK (%d rule%s)" % (len(rules), "" if len(rules) == 1 else "s"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
