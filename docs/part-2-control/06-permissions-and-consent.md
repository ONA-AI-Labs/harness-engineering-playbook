# 6. Permissions and consent

**How much autonomy, safely?**

As much as the irreversible actions allow. Pre-approve the checks, enforce the few things that cannot be undone, and make every consent explicit, momentary and non-transferable.

## The short answer

A short allow list of exactly the commands the agent must run without asking; a guard that denies the handful of actions no agent should ever take and asks before the rest; and written consent rules that an earlier yes does not carry over.

## How it fails without this

- Permission prompts are approved 93 % of the time, according to Marmelab's survey; a prompt the person always approves protects nothing.
- A workspace accumulated dozens of one-off "always allow" entries, including unrestricted database and remote-shell access, one approval at a time, because each one was reasonable in the moment.
- A scheduled recovery job was enabled in production without a dry run; its first pass reprocessed every stuck item ever recorded, and the spend could not be undone.
- A design was approved; the agent treated the approval as consent for the deletion the design described.

## The pattern

### Allow exactly the checks

The repository's settings pre-approve the quick check, the full check, the test and build commands, and nothing broader. An agent that can run its checks without asking runs them; an agent that must ask learns to skip them. The [settings template](../../templates/hooks/claude-code/settings.json) has the four entries. Audit the user-level allow list quarterly and delete anything broader than a check.

### The guard: deny, ask, allow

| Decision | Actions |
|---|---|
| deny | force-push to `main`; recursive delete of the root, the home directory, `.git` or anything outside the workspace and temp folders; database resets and migration pushes; deleting the main branch; deleting a repository; `terraform destroy` with auto-approve |
| ask | other force-pushes and remote branch deletes; hard resets, whole-tree checkouts, `git clean`, dropping stashes; recursive deletes inside the workspace except build folders; destructive SQL; remote commands that delete, stop or restart; container prunes and volume removal; cluster and cloud delete commands; merges that may auto-deploy; releases and package publishes; edits to `.env*` files or an existing migration |
| allow | everything else, and anything the guard cannot parse |

"Ask" is for actions that are sometimes right; the person decides at that moment. "Deny" is for actions that are never right for an agent. "Allow what you cannot parse" keeps a guard bug from becoming a wall; the metrics log shows what it allowed.

### Consent is explicit and non-transferable

Write these in the map, in the Hard rules table, as prose, and keep them prose: they are about the relationship, not the code.

- No commit, push, deploy, merge or migration unless the person asked for that one.
- Owner-only steps are listed separately (applying migrations, flipping production flags, purging data).
- A rollout runbook marks each step **GO**, and each GO needs a yes at that moment; an earlier yes does not carry over. The [runbook template](../../templates/docs/rollout-runbook.md) has the shape.
- Approving a design is not approving a purge. Before any irreversible operation: dry-run it, show the counts, ask.

### Dry runs with counts

A scheduled job, a backfill, a cleanup: before it runs for real, run its selection and show the number. "This will touch 12 items" is a decision; "this will touch 40,000" is a different one. Give every such job a look-back bound.

### Secrets and untrusted content

- Secrets never appear in instruction files, logs, error messages or hook output. The guard asks before any edit to a `.env` file.
- Content an agent fetches from the web, from a ticket or from a downloaded archive is data, not instruction. Downloads go into their own empty directory; scripts the agent writes live elsewhere; interpreters that read the downloads run in isolated mode.
- Test suites hold no admin credentials. They act as ordinary test users, record what they created, and clean up only that.

### Sandboxes and managed policy

Claude Code offers sandboxed execution and organisation-managed settings that a project cannot override; Codex and the IDE tools have their own approval modes ([matrix](../tool-support-matrix.md)). Use managed policy for the deny list once more than one team runs agents: a deny that lives in a repository can be edited by the agent working in it.

### Isolate what runs where

A test build that inherits the real user's session, a dev run that talks to production because no environment was set, a shared cache with a connection cap used by both test and production: each is a consent problem disguised as a configuration one. The map's sharp edges list them with the fix.

## Do this today

1. Replace the user-level allow list with per-repository allow lists that name only the checks.
2. Install the guard and read its decisions after a week: every decision lands in `~/.claude/metrics/harness.jsonl` (override with `HARNESS_METRICS_FILE`); `tools/harness-stats.py` from a playbook checkout summarises it, or copy that script next to your hooks.
3. Write the consent rules into the map. Add "dry run, show counts, ask" to the runbook template.

## Sources

Marmelab (93 % approval; permission prompts without enforcement); Claude Code documentation on permissions, sandboxing and managed settings; field notes (permission creep, the recovery job, the design-versus-purge approval). Links in [references](../references.md).
