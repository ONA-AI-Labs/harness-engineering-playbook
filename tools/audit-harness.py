#!/usr/bin/env python3
"""Score a repo on the harness maturity model (levels 0-4) by checking ENFORCEMENT, not file presence.

Part of the Harness Engineering Playbook (MIT). Python 3 standard library only.
  python3 tools/audit-harness.py /path/to/repo
  curl -fsSL https://raw.githubusercontent.com/ONA-AI-Labs/harness-engineering-playbook/main/tools/audit-harness.py | python3 - /path/to/repo

usage: audit-harness.py <repo> [--app-dir SUB] [--hooks-file settings.json] [--json] [--min-level N]

  --app-dir     folder inside the repo that holds the manifest, scripts and tests (default ".")
  --hooks-file  a Claude settings.json whose hooks apply to this repo (e.g. the workspace one)
  --min-level   exit 1 when the repo scores below N

Level 1 instructed: an instruction map exists, says what the system is, stays short, names a
          check command that exists; a lockfile is present when there is a manifest.
Level 2 enforced:   hooks are configured and their scripts exist; a destructive-command guard;
          a pre-stop check; an allow list; a definition of done that verifies what ships.
Level 3 continuous: knowledge docs in the repo; a debt gate in CI (ratchet or zero tolerance);
          hard rules with at least one real enforcer; evals/e2e or a metrics log.
Level 4 governed:   CODEOWNERS on harness files; CI runs the checks on pull requests; hard rules
          carry an expiry or review date; a budget rule.
A check can be declared not applicable in <repo>/.harness/audit.json:
  {"not_applicable": {"ship_check": "docs repo, ships no runtime"}}
"""
import json
import os
import re
import sys
from pathlib import Path

INSTRUCTION_NAMES = ("CLAUDE.md", "AGENTS.md")


def read(path):
    try:
        return Path(path).read_text(errors="replace")
    except OSError:
        return ""


class Audit:
    def __init__(self, repo, app_dir, hooks_file):
        self.repo = Path(repo).resolve()
        self.app = (self.repo / app_dir).resolve()
        self.hooks_file = Path(hooks_file).resolve() if hooks_file else None
        self.checks = []
        try:
            self.na = json.loads(read(self.repo / ".harness" / "audit.json")).get("not_applicable", {})
        except ValueError:
            self.na = {}
        self.instruction = self.find_instruction()
        self.text = self.expand_imports(read(self.instruction), self.instruction) if self.instruction else ""

    # ---- helpers -------------------------------------------------------
    def add(self, level, check, status, detail):
        if check in self.na:
            status, detail = "N/A", self.na[check]
        self.checks.append({"level": level, "check": check, "status": status, "detail": detail})

    def find_instruction(self):
        # the app folder's map wins over a root file that only routes to it
        for folder in (self.app, self.repo):
            for name in INSTRUCTION_NAMES:
                if (folder / name).is_file():
                    return folder / name
        return None

    @staticmethod
    def expand_imports(text, path, depth=0):
        """Inline `@relative/path` import lines (one per line, up to 4 hops) the way Claude Code does."""
        if depth > 4:
            return text
        out = []
        for line in text.splitlines():
            m = re.match(r"^@(\S+)\s*$", line)
            target = (path.parent / m.group(1)).resolve() if m else None
            if target and target.is_file():
                out.append(Audit.expand_imports(read(target), target, depth + 1))
            else:
                out.append(line)
        return "\n".join(out)

    def manifest(self):
        for folder in (self.app, self.repo):
            if (folder / "package.json").is_file():
                return folder / "package.json", "node"
            if (folder / "pubspec.yaml").is_file():
                return folder / "pubspec.yaml", "dart"
            if (folder / "Cargo.toml").is_file():
                return folder / "Cargo.toml", "rust"
            if (folder / "pyproject.toml").is_file():
                return folder / "pyproject.toml", "python"
        return None, None

    def package_scripts(self):
        path, kind = self.manifest()
        if kind != "node":
            return {}
        try:
            return json.loads(read(path)).get("scripts", {}) or {}
        except ValueError:
            return {}

    def settings(self):
        for folder in (self.app, self.repo):
            path = folder / ".claude" / "settings.json"
            if path.is_file():
                try:
                    return json.loads(read(path)), path
                except ValueError:
                    return {}, path
        return {}, None

    def hooks(self):
        """Return (hooks dict, project dir for $CLAUDE_PROJECT_DIR) from the repo settings or --hooks-file."""
        local, path = self.settings()
        if local.get("hooks"):
            return local["hooks"], path.parent.parent
        if self.hooks_file and self.hooks_file.is_file():
            try:
                return json.loads(read(self.hooks_file)).get("hooks", {}) or {}, self.hooks_file.parent.parent
            except ValueError:
                return {}, None
        return {}, None

    def hook_commands(self, event):
        hooks, project = self.hooks()
        out = []
        for group in hooks.get(event, []) or []:
            for hook in group.get("hooks", []) or []:
                if hook.get("type", "command") == "command" and hook.get("command"):
                    out.append((hook["command"], project))
        return out

    @staticmethod
    def script_paths(command, project):
        found = []
        for token in re.findall(r'"([^"]+)"|(\S+)', command):
            token = token[0] or token[1]
            if re.search(r"\.(py|sh|js|mjs|rb)$", token):
                expanded = token.replace("${CLAUDE_PROJECT_DIR}", str(project or "")).replace("$CLAUDE_PROJECT_DIR", str(project or ""))
                found.append(Path(os.path.expanduser(expanded)))
        return found

    def workflows(self):
        folder = self.repo / ".github" / "workflows"
        return [read(p) for p in folder.glob("*.y*ml")] if folder.is_dir() else []

    def section(self, heading_regex):
        match = re.search(r"^#+\s*(%s).*$" % heading_regex, self.text, re.I | re.M)
        if not match:
            return ""
        rest = self.text[match.end():]
        nxt = re.search(r"^#+\s", rest, re.M)
        return rest[:nxt.start()] if nxt else rest

    # ---- level 1 -------------------------------------------------------
    def level1(self):
        if not self.instruction:
            self.add(1, "instruction_file", "FAIL", "no CLAUDE.md or AGENTS.md in %s" % self.repo.name)
            self.add(1, "says_what_it_is", "FAIL", "no instruction file")
            self.add(1, "instruction_length", "FAIL", "no instruction file")
            self.add(1, "names_check_command", "FAIL", "no instruction file")
        else:
            lines = self.text.splitlines()
            rel = self.instruction.relative_to(self.repo)
            self.add(1, "instruction_file", "PASS", "%s (%d lines)" % (rel, len(lines)))
            head = [l for l in lines[:10] if l.strip() and not l.lstrip().startswith("#")]
            self.add(1, "says_what_it_is", "PASS" if any(len(l.split()) >= 8 for l in head) else "FAIL",
                     "first 10 lines %s a sentence about the system" % ("contain" if any(len(l.split()) >= 8 for l in head) else "lack"))
            n = len(lines)
            status = "PASS" if n <= 100 else ("WARN" if n <= 200 else "FAIL")
            self.add(1, "instruction_length", status, "%d lines (target under 100, limit 200)" % n)
            names = re.search(r"quick-check\.sh|check\.sh|npm (run )?(check|lint|test)|flutter (analyze|test)|make (check|quick|test|lint)|cargo (check|test)|pytest", self.text)
            self.add(1, "names_check_command", "PASS" if names else "FAIL",
                     "mentions `%s`" % names.group(0) if names else "no check command named")
        quick = self.app / "scripts" / "quick-check.sh"
        full = self.app / "scripts" / "check.sh"
        scripts = self.package_scripts()
        make_targets = re.findall(r"^(quick|check|lint|test):", read(self.app / "Makefile") + read(self.repo / "Makefile"), re.M)
        if quick.is_file() and os.access(quick, os.X_OK):
            self.add(1, "check_command_exists", "PASS", "scripts/quick-check.sh is executable")
        elif full.is_file() and os.access(full, os.X_OK):
            self.add(1, "check_command_exists", "PASS", "scripts/check.sh is executable")
        elif make_targets:
            self.add(1, "check_command_exists", "PASS", "Makefile targets: %s" % ", ".join(sorted(set(make_targets))))
        elif quick.is_file():
            self.add(1, "check_command_exists", "WARN", "scripts/quick-check.sh exists but is not executable")
        elif any(k in scripts for k in ("check", "lint", "test")):
            self.add(1, "check_command_exists", "WARN", "no scripts/quick-check.sh; package scripts: %s" % ", ".join(k for k in ("check", "lint", "test") if k in scripts))
        elif (self.app / "pubspec.yaml").is_file():
            self.add(1, "check_command_exists", "WARN", "no scripts/quick-check.sh; flutter analyze is implicit")
        else:
            self.add(1, "check_command_exists", "FAIL", "no quick check script or package check script")
        path, kind = self.manifest()
        if kind is None:
            self.add(1, "lockfile", "N/A", "no package manifest")
        else:
            locks = {"node": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock"],
                     "dart": ["pubspec.lock"], "rust": ["Cargo.lock"], "python": ["uv.lock", "poetry.lock", "requirements.txt"]}[kind]
            # a workspace (monorepo) keeps one lockfile at the repo root
            present = [l for l in locks if (path.parent / l).is_file() or (self.repo / l).is_file()]
            self.add(1, "lockfile", "PASS" if present else "FAIL", present[0] if present else "no lockfile next to %s or at the repo root" % path.name)

    # ---- level 2 -------------------------------------------------------
    def level2(self):
        pre = self.hook_commands("PreToolUse")
        stop = self.hook_commands("Stop")
        missing = []
        everything = []
        for event in (self.hooks()[0] or {}):
            everything += self.hook_commands(event)
        for command, project in everything:
            for script in self.script_paths(command, project):
                if not script.is_file():
                    missing.append(str(script))
        if not pre and not stop:
            self.add(2, "hooks_configured", "FAIL", "no PreToolUse/Stop hooks in .claude/settings.json" + (" or the hooks file" if self.hooks_file else " (pass --hooks-file for workspace hooks)"))
        elif missing:
            self.add(2, "hooks_configured", "FAIL", "hook scripts missing: %s" % ", ".join(missing))
        else:
            self.add(2, "hooks_configured", "PASS", "%d PreToolUse, %d Stop hook commands, scripts present" % (len(pre), len(stop)))
        guard = [c for c, _ in pre if "guard" in c.lower()]
        self.add(2, "destructive_guard", "PASS" if guard else "FAIL", guard[0][:80] if guard else "no PreToolUse hook with 'guard' in its command")
        self.add(2, "pre_stop_check", "PASS" if stop else "FAIL", stop[0][0][:80] if stop else "no Stop hook")
        settings, path = self.settings()
        allow = (settings.get("permissions") or {}).get("allow") or []
        self.add(2, "allow_list", "PASS" if allow else "FAIL", "%d entries in %s" % (len(allow), path.relative_to(self.repo)) if allow else "no permissions.allow in .claude/settings.json")
        dod = self.section(r"done means|definition of done|verification ritual|what .done. means")
        self.add(2, "definition_of_done", "PASS" if dod.strip() else "FAIL", "section found" if dod.strip() else "no 'Done means' / 'Definition of done' section")
        ship = re.search(r"check:boot|boot-check|\b(smoke|build|boot|install|device|simulator|emulator|flutter run)\b", dod, re.I)
        self.add(2, "ship_check", "PASS" if ship else "FAIL", "done means includes `%s`" % ship.group(0) if ship else "done means never verifies the built artifact (boot/build/smoke/install)")

    # ---- level 3 -------------------------------------------------------
    def level3(self):
        docs = []
        for folder in (self.repo / "docs", self.app / "docs"):
            if folder.is_dir():
                docs += [p for p in folder.rglob("*.md") if p.name.lower() != "readme.md"]
        self.add(3, "knowledge_docs", "PASS" if docs else "FAIL", "%d markdown files under docs/" % len(docs) if docs else "no docs/ with markdown")
        gate = None
        for text in self.workflows():
            m = re.search(r"check-baseline|ratchet|--max-warnings[= ]0\b|flutter analyze|dart analyze|-D warnings|--strict|\btsc\b|npm run (lint|typecheck|type-check|check)\b|\beslint\b|cargo clippy|markdownlint|shellcheck|\bruff\b|flake8|pylint|golangci-lint|make (check|lint|quick)", text)
            if m:
                gate = m.group(0)
                break
        self.add(3, "debt_gate", "PASS" if gate else "FAIL", "CI runs `%s`" % gate if gate else "no CI workflow with a ratchet or zero-tolerance gate")
        rules = self.section(r"hard rules|non-negotiables|rules")
        rows = [l for l in rules.splitlines() if l.strip().startswith("|") and not re.match(r"^\|\s*-", l.strip()) and "enforced by" not in l.lower()]
        def last_cell(line):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            return cells[-1] if cells else ""
        enforcer = re.compile(r"\.test\.|_test\.|lint|eslint|hook|\bCI\b|workflow|\.sh|\.mjs|analyze|spec|guard|check", re.I)
        # the Enforced-by cell may name an enforcer for part of the rule and say "prose" for the rest; a cell that STARTS with prose enforces nothing
        enforced = [l for l in rows if enforcer.search(last_cell(l)) and not re.match(r"^\s*prose", last_cell(l), re.I)]
        self.add(3, "enforced_rules", "PASS" if enforced else "FAIL", "%d of %d hard-rule rows name an enforcer" % (len(enforced), len(rows)) if rows else "no hard-rules table")
        scripts = self.package_scripts()
        evals = [k for k in scripts if re.search(r"eval|e2e|playwright", k)] or ([p.name for p in self.app.glob("playwright.config.*")]) or (["integration_test/"] if (self.app / "integration_test").is_dir() else [])
        hooks, _ = self.hooks()
        hook_text = json.dumps(hooks)
        metrics = bool(re.search(r"harness\.jsonl|metrics|guard-destructive|require-check-before-stop|stop-quick-check", hook_text))
        if evals:
            self.add(3, "evals_or_metrics", "PASS", "evals/e2e: %s" % ", ".join(evals[:4]))
        elif metrics:
            self.add(3, "evals_or_metrics", "PASS", "hooks log to a metrics file")
        else:
            self.add(3, "evals_or_metrics", "FAIL", "no eval/e2e scripts and no metrics logging hook")

    # ---- level 4 -------------------------------------------------------
    def level4(self):
        owners = ""
        for cand in (self.repo / "CODEOWNERS", self.repo / ".github" / "CODEOWNERS", self.repo / "docs" / "CODEOWNERS"):
            owners = owners or read(cand)
        covered = bool(re.search(r"CLAUDE\.md|AGENTS\.md|\.claude", owners))
        self.add(4, "codeowners", "PASS" if covered else "FAIL", "harness files have owners" if covered else "no CODEOWNERS covering CLAUDE.md/.claude")
        pr_ci = any(re.search(r"pull_request", t) and re.search(r"lint|test|analyze|check", t) for t in self.workflows())
        self.add(4, "ci_on_pull_requests", "PASS" if pr_ci else "FAIL", "a workflow runs checks on pull_request" if pr_ci else "no pull_request workflow running checks")
        expiry = re.search(r"expires|review by|until \d{4}|remove after|drop after|revisit", self.text, re.I)
        self.add(4, "rules_have_expiry", "PASS" if expiry else "FAIL", "found `%s`" % expiry.group(0) if expiry else "no expiry/review dates on rules")
        budget = re.search(r"budget|spend cap|cost cap", self.text, re.I)
        self.add(4, "budget_rule", "PASS" if budget else "FAIL", "found `%s`" % budget.group(0) if budget else "no budget rule in the instruction file")

    def run(self):
        self.level1(); self.level2(); self.level3(); self.level4()
        level = 0
        for lv in (1, 2, 3, 4):
            if all(c["status"] in ("PASS", "WARN", "N/A") for c in self.checks if c["level"] == lv):
                level = lv
            else:
                break
        return level


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    repo, app_dir, hooks_file, as_json, min_level = argv[0], ".", None, False, None
    i = 1
    while i < len(argv):
        if argv[i] == "--app-dir":
            app_dir = argv[i + 1]; i += 2
        elif argv[i] == "--hooks-file":
            hooks_file = argv[i + 1]; i += 2
        elif argv[i] == "--json":
            as_json = True; i += 1
        elif argv[i] == "--min-level":
            min_level = int(argv[i + 1]); i += 2
        else:
            print("unknown argument %s" % argv[i]); return 2
    audit = Audit(repo, app_dir, hooks_file)
    level = audit.run()
    if as_json:
        print(json.dumps({"repo": str(audit.repo), "level": level, "checks": audit.checks}, indent=1))
    else:
        print("Harness audit: %s" % audit.repo.name)
        for c in audit.checks:
            print("  [%-4s] L%d %-22s %s" % (c["status"], c["level"], c["check"], c["detail"]))
        print("Level reached: %d" % level)
        todo = [c for c in audit.checks if c["status"] == "FAIL" and c["level"] == level + 1]
        if todo:
            print("To reach level %d: %s" % (level + 1, "; ".join(c["check"] for c in todo)))
    if min_level is not None and level < min_level:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
