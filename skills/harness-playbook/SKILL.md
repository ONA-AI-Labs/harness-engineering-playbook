---
name: harness-playbook
description: Audit this repository against the harness maturity model and install the missing pieces (instruction map, quick check, hooks, definition of done, memory, evals) from the Harness Engineering Playbook templates, one level at a time. Use when asked to "set up the harness", "harness this repo", "run the harness audit" or "raise the harness level".
---

# Harness playbook

You install and upgrade the harness around a coding agent in the current repository, using the templates that ship with this skill's playbook. Work one maturity level at a time and never overwrite a file the repository already has without showing the diff first.

## Where the templates are

Resolve `PLAYBOOK` first, in this order: the environment variable `HARNESS_PLAYBOOK_DIR`; a sibling checkout named `harness-engineering-playbook`; otherwise clone `https://github.com/ONA-AI-Labs/harness-engineering-playbook` into a temporary folder. Templates are under `$PLAYBOOK/templates/`, the audit at `$PLAYBOOK/tools/audit-harness.py`.

## Steps

1. **Audit.** Run `python3 $PLAYBOOK/tools/audit-harness.py .` (add `--app-dir <folder>` when the app lives in a subfolder, `--hooks-file <path>` when hooks are configured at the workspace level). Report the level and the "To reach level N" line verbatim.
2. **Plan the next level only.** List the FAIL checks of the next level and the template that fixes each. Show the list and stop if the user asked only for the audit.
3. **Install, adapting placeholders from the repo.** Read `package.json`, `pubspec.yaml`, `pyproject.toml`, `Makefile` or `Cargo.toml` once to find the real lint, type, test, build and install commands, and put them where the templates say `<LINT_COMMAND>` and friends. Rules per level:
   - Level 1: `templates/AGENTS.md` (write it from what the repo is: under 100 lines, the first 10 lines say what the system is, a Commands block, the check command named), `templates/CLAUDE.md`, `templates/scripts/quick-check.sh`.
   - Level 2: `templates/hooks/claude-code/settings.json` into `.claude/` and all four `templates/hooks/scripts/*.py` into `.claude/hooks/` (for Codex: `templates/hooks/codex/hooks.json` into `.codex/` and the same four scripts into `.codex/hooks/`), `templates/docs/definition-of-done.md`, `templates/scripts/check.sh`, `templates/scripts/boot-check.sh` when there is a runtime to boot.
   - Level 3: `templates/docs/PROGRESS.md`, `templates/docs/DECISIONS/`, `templates/memory/`, `templates/docs/incident-to-rule.md`, `templates/scripts/ratchet.sh` with today's count as the baseline, `templates/scripts/arch-check.py` with one real rule, `templates/evals/` with five tasks from real failures.
   - Level 4: `templates/ci/harness-gates.yml`, CODEOWNERS lines for the harness files, an owner and an expiry on every hard rule, a budget line in the map.
4. **Never silently overwrite.** When the target exists, show a unified diff of what you would change and ask. Keep every existing allow-list entry and every existing rule.
5. **Verify.** Run `scripts/quick-check.sh`, then the audit again. The level must have risen by exactly one, or you explain why not.
6. **Report** in at most twelve lines: level before and after, files added or changed, the check commands you wired in, what you could not fill in (placeholders left), and what the user must do by hand (restart the session for hooks to load, commit).

## Rules

- Hooks load at session start: say so, and never claim a hook is active in the current session.
- Prose rules go in the Hard rules table with "prose, no enforcer yet"; do not invent enforcers.
- Do not run tests, builds or dev servers unless the audit step needs the check command's exit code.
- Do not commit, push or open pull requests unless asked.
