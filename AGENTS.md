# Harness Engineering Playbook: agent map

This repository is a public playbook: Markdown chapters under `docs/`, drop-in templates under `templates/`, Python tools under `tools/`, and a skill under `skills/`. It teaches harness engineering and follows its own advice. No product or company internals belong here; see `CONTRIBUTING.md`.

## Commands

- `make quick`: markdownlint, shellcheck, JSON parse. Seconds. The Stop hook runs it before you finish.
- `make check` (also `scripts/check.sh`): quick plus the offline link check, the bats suites and the repo's own audit. The definition of done.
- `bats tools/tests/`: the hook, script and audit tests. `python3 tools/audit-harness.py <repo>`: the audit.

## Done means

1. `make check` passes; paste its last line in the pull request.
2. A new or changed script template has a bats test; a new chapter has its "Sources" section.
3. `grep -rniF -f <your private terms file> .` is empty if you are a maintainer with one.
4. List what you did not verify.

## Hard rules

| Rule | Enforced by |
|---|---|
| Every relative link resolves | `lychee --offline` in `make check` and CI |
| Markdown stays lint-clean; every `.sh` passes shellcheck; every JSON parses | `make quick`, run by the Stop hook and CI |
| Hook and script templates behave as documented | `tools/tests/*.bats` |
| The repo scores at least level 2 on its own audit | `make audit` in CI (`.harness/audit.json` declares the two checks that do not apply) |
| No private names, hosts, credentials | prose, no enforcer yet (maintainers run a private sweep before each release) |
| No destructive git or shell commands from an agent without a person's confirmation | `.claude/settings.json` → `templates/hooks/scripts/guard-destructive.py` |

## Layout

- `docs/00-start-here.md`, then `docs/part-1-foundations/` … `docs/part-5-operate/` (14 chapters), `docs/field-lessons.md`, `docs/tool-support-matrix.md`, `docs/glossary.md`, `docs/references.md`.
- `templates/` (copy into a repo; `templates/starter/` is the 11-file kit), `tools/` (audit, tests), `skills/harness-playbook/` (the installer skill), `assets/` (diagrams).

## Writing rules

Short sentences, plain English, headings as questions or verbs, one idea per paragraph, sources in the same section as the claim. See `CONTRIBUTING.md`.
