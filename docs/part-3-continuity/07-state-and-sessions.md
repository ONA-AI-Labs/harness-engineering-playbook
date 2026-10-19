# 7. State and sessions

**Why do long tasks lose the thread?**

Because every session starts with no memory of the last one. Anthropic's image is exact: engineers working in shifts, where each new engineer arrives with no memory of the previous shift. Whatever was not written to disk at the end of a session does not exist at the start of the next.

## The short answer

Put the state on disk in three small files the agent reads at the start and updates at the end: a progress file, a feature list, and an init script. Then make the session boundaries explicit: one feature per session, a start ritual, a clean exit.

## How it fails without this

Anthropic observed two failure modes in long-running work: the agent tries to implement everything at once, exhausts its context mid-feature and leaves undocumented partial work; or it sees some progress and declares the project complete. A third shows up in teams: the next session cannot tell what the last one verified, so it either re-verifies everything or trusts everything.

## The pattern

### Three files

| File | Holds | Template |
|---|---|---|
| `docs/PROGRESS.md` | current commit and check results, what was done, what is next, what is blocked on a person | [template](../../templates/docs/PROGRESS.md) |
| `feature_list.json` | every feature with a verify command and a `passes` flag; the scope boundary | [template](../../templates/feature_list.json) |
| `scripts/init.sh` | install, run the quick check, say how to start the app | [template](../../templates/scripts/init.sh) |

Anthropic's initializer agent produced the same three (an `init.sh`, a progress file, a feature list of 200+ items all marked failing) plus a first commit, and every later session began by reading them.

### The start ritual

1. Confirm the working directory and the branch.
2. Read the progress file and the git log.
3. Run `scripts/init.sh`: dependencies present, quick check green. Never start work on a machine that cannot run the checks.
4. Pick the single highest-priority feature that does not pass.
5. Run a basic end-to-end check before touching anything, so a pre-existing failure is known before it is blamed on the new work.

The [session context hook](../../templates/hooks/scripts/session-start-context.py) does the first two steps for the agent: branch, uncommitted count and the head of the progress file arrive before the first prompt.

### One feature per session

The feature list is a scope boundary the agent cannot argue with. A feature is done when `scripts/verify-feature.py <id>` runs its verify command and flips `passes` to true with the evidence recorded. An agent may not edit the flag by hand; the [script](../../templates/scripts/verify-feature.py) is the only path. Features are sized for one session; a feature that needs two is two features.

### Context anxiety

An agent that senses its context filling wraps up early and sloppily. Smaller features and a progress file that is updated as work happens, not at the end, remove the reason to hurry. Anthropic's second harness dropped sprint decomposition when a newer model sustained longer tasks on its own; the files stayed.

### The clean exit

Before the session ends: commit, so the next session can resume from a known state; update the progress file with the next step; record what was not verified; leave no temporary hacks. The [clean-state check](../../templates/scripts/clean-state-check.sh) fails on uncommitted changes, on leftover markers and on a progress file without a Next section, and the [handoff template](../../templates/docs/session-handoff.md) is the shape of the note.

### Worktrees and shared checkouts

Several agents or people on one repository need their own working trees. Rules from the field: give each worktree real dependencies (a symlinked `node_modules` gets wiped by the next install); before any write in a shared checkout, check the branch and the status, because another session may be mid-work there; stage by explicit path, never `git add -A`, when two agents share a tree; and never run a bare stash in a shared repository, because the stash stack is shared too.

### Tests are not editable state

"It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality." Anthropic put that sentence in the agent's instructions; put it in your map's Hard rules, and give it an enforcer: a test-count ratchet, or a review rule that a pull request deleting a test needs a person's approval.

### Clear between features

A session that carries the previous feature's context into the next pays for it on every turn. In interactive tools, clear the context between features; in automated loops, start a fresh session per feature.

## Do this today

1. Create `docs/PROGRESS.md` from the template and fill the Current state section.
2. Write `scripts/init.sh` and run it on a fresh clone. If it fails, that is your first finding.
3. Write five features into `feature_list.json` with verify commands. Mark them all failing.

## Sources

Anthropic, *Effective harnesses for long-running agents* (initializer and coding agents, the start ritual, the feature list, tests are not editable); Anthropic, *Harness design for long-running application development* (context anxiety; sprints dropped on a newer model); field notes (worktrees, shared checkouts, stash). Links in [references](../references.md).
