# <PROJECT_NAME>: agent map

<!-- Copy to the repo root as AGENTS.md. Under 100 lines. The first ten lines say what this system is; the rest is a map
     of where to look and what is enforced. Knowledge that does not fit goes in docs/agent/<topic>.md with one index line here.
     Claude Code reads CLAUDE.md: make that file one line, "@AGENTS.md". -->

<ONE_PARAGRAPH: what the system does, for whom, and the two or three facts an engineer needs on day one
(stack, where it runs, what it talks to).>

## Commands

- `scripts/quick-check.sh`: lint and types, under 90 s. Runs before you stop.
- `scripts/check.sh`: the full check, the definition of done (quick check, tests, build, boot check).
- `<DEV_COMMAND>`: run the app locally. `<INSTALL_COMMAND>`: install dependencies.

## Done means

1. `scripts/quick-check.sh` ends `quick-check: OK`.
2. `scripts/check.sh` ends `check: OK`: tests, build, and the boot check on the built artifact; while iterating, run only the tests for the code you changed.
3. By hand: <WHAT_A_PERSON_MUST_CHECK, e.g. open the screen you changed in a browser at phone and desktop width>.
4. List what you did not verify. Never say done without that list.

## Hard rules

| Rule | Enforced by |
|---|---|
| No type errors | `<TYPECHECK_COMMAND>` in `scripts/quick-check.sh` and CI |
| No new lint findings | `scripts/ratchet.sh` at the baseline in CI |
| <RULE_WITH_A_TEST> | `<test file>` |
| <RULE_WITHOUT_AN_ENFORCER> | prose, no enforcer yet |
| Never apply migrations, deploy, push to main or merge yourself | prose; the guard hook asks before `gh pr merge` |

## Layout

- `<src/folder>`: <one line>
- `<src/folder>`: <one line>
- `docs/agent/`: the detail that used to live in this file, one topic per file (index below)

## Detail by topic

- `docs/agent/<topic>.md`: <what it covers, one line>

## Known sharp edges (dated)

- <FACT_THAT_BITES, with the date you checked it>
