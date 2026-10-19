# 14. Enterprise rollout

**How does an organisation adopt this?**

One repository at a time, in level order, owned by the people who own the developer platform, measured by an audit that checks enforcement rather than file presence. The practice spreads when the first repository's agents visibly stop declaring victory on broken builds.

## The short answer

Adopt the maturity model below, score every repository with the audit, take each to level 2 in a week and level 3 in a quarter, put the deny list under managed policy, and report four numbers a month.

## The maturity model

| Level | Name | A repository at this level has | The audit checks |
|---|---|---|---|
| 0 | unharnessed | no instruction file, or one nobody maintains | nothing passes |
| 1 | instructed | a map under 100 lines that says what the system is and names a check command that exists; a lockfile when there is a manifest | instruction file, first ten lines, length, named check, check exists, lockfile |
| 2 | enforced | hooks whose scripts exist; a destructive-command guard; a pre-stop check; an allow list; a definition of done that verifies what ships | hooks configured, guard, pre-stop check, allow list, done section, ship check (or a declared exemption) |
| 3 | continuous | knowledge docs in the repository; a debt gate in CI; hard rules with at least one real enforcer; evals or a metrics log | docs folder, CI gate, enforced rules, evals or metrics |
| 4 | governed | owners on the harness files; CI running the checks on pull requests; an expiry on hard rules; a budget rule | CODEOWNERS, pull-request CI, expiry dates, budget rule |

Score a repository with the [audit](../../tools/audit-harness.py):

```sh
python3 tools/audit-harness.py path/to/repo                 # prints PASS/WARN/FAIL/N/A per check and the level reached
python3 tools/audit-harness.py path/to/repo --min-level 2   # exit 1 below level 2: use it in CI
```

A check that does not apply (a documentation repository has nothing to boot) is declared with a reason in `.harness/audit.json` and reported as N/A, never silently skipped.

### Field results

The authors' own six repositories (an API, a web app with a desktop shell, an admin panel, a marketing site, two mobile apps) went from levels 0, 1, 1, 0, 0, 0 to 3, 3, 3, 2, 3, 2 in one working day in October 2026, with the [starter kit](../../templates/STARTER.md), one agent per repository, and a person reviewing each pull request. The largest single change was a 23,000-word instruction file becoming a 95-line map with 27 topic files.

## The pattern

### Owners

The harness is a platform concern. A platform or developer-experience team owns the shared pieces (the guard, the stop check, the audit, the templates, the maturity model) and the workspace-level policy; each repository's team owns its map, its quick check and its hard rules. CODEOWNERS routes changes to harness files (`AGENTS.md`, `.claude/`, `templates/hooks/`, `tools/`) to the platform owners.

### Managed policy for the deny list

A deny rule in a repository's settings can be edited by the agent working in that repository. Claude Code's managed settings, Codex's requirements file, Cursor's team dashboard, Copilot's organisation policies and Gemini CLI's admin policy tier all exist for this ([matrix](../tool-support-matrix.md)). Put the deny list and the sandbox defaults there; leave allow lists to repositories.

### Order of rollout

Böckeler's word is harnessability: a strongly typed, modular, well-tested codebase gives a harness more to hold on to. Start there, so the first result is visible and the templates get tuned on an easy case. Legacy repositories with debt come later, with the ratchet. Within a repository, the order is the level order: the map first, because every other piece refers to it.

### Thirty, sixty, ninety days

| By day | Platform team | Each repository team |
|---|---|---|
| 30 | starter kit published internally; audit in CI at `--min-level 1`; guard and stop check under managed policy; harness stats collected | map under 100 lines; quick check; definition of done; hooks installed; level 2 |
| 60 | eval runner adopted; memory convention; incident-to-rule files; monthly transcript reading | ratchet at today's count; architecture check with one real rule; ten eval tasks from real failures; level 3 |
| 90 | maintenance calendar; expiry review; cost dashboard | CODEOWNERS; expiry on hard rules; budget line; CI gates workflow; level 4 |

### Four numbers a month

1. Level per repository, from the audit.
2. Guard interventions (ask and deny) and false positives, from the stats.
3. Stop-check failures caught before a pull request, from the stats.
4. Eval pass rate on the frozen task set, per repository.

Add cost per task when the telemetry exists. These four are enough to show the board whether the harness is working and to show the team which repository needs help.

### Budget and model choice

Spend follows context, not output: the field's largest saving came from removing stacked agent contexts, not from a cheaper model. Within that, a cheaper model for boilerplate-heavy fan-outs and the frontier model for the main session is the usual split. Each repository's map carries one budget line: what a session may spend, and who approves more.

### Compliance notes

- The metrics file is an audit log of what agents were prevented from doing; keep it where your other audit logs live.
- Secrets never enter instruction files, hook output or memory; the guard asks before `.env` edits.
- Transcripts and eval fixtures are data about your users' data; apply the same residency and retention rules.
- Managed policy makes the deny list reviewable by security without reading every repository.

### Training

The thirty-minute path in [Start here](../00-start-here.md) is the onboarding. A new engineer copies the starter kit into one repository, runs the audit, and reads the field lessons. The habit that matters most is the last section of every report: what was not verified.

## Do this today

1. Score every repository with the audit. Publish the table.
2. Put the guard's deny list under managed policy.
3. Pick the most harnessable repository and take it to level 2 this week with the starter kit.

## Sources

Böckeler (harnessability; harness templates per topology); Marmelab (what the field has and lacks); Claude Code, Codex, Cursor, Copilot and Gemini CLI documentation on managed policy ([matrix](../tool-support-matrix.md)); field notes (the one-day rollout). Links in [references](../references.md).
