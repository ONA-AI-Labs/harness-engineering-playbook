# 4. Enforcement over prose

**Why are prose rules ignored?**

Because a rule the model must remember competes with every other instruction for attention, while a rule a script enforces costs nothing to remember. The agent does not ignore your rule out of carelessness. It has a hundred and fifty of them.

## The short answer

Every repeated correction becomes a guard. The ladder is rule, then script, then hook: write the rule once, turn it into a script that fails, then wire the script into the agent's loop so it runs without being asked.

## How it fails without this

Marmelab's survey of 481 public instruction files found that only 4.4 % of the security rules in them were backed by a real control, and estimates that prose rules fail about 85 % of the time. Lin et al. found that structural harness elements (tools, middleware, memory) transfer across models while prose prompting does not. In the field, the same correction ("run the boot check after adding a dependency", "never apply migrations yourself") appeared in instruction files, in briefs, in memory, and was still missed, until it became a check that could not be skipped.

## The pattern

### The ladder

| Step | Example | Cost | Reliability |
|---|---|---|---|
| Rule in the map | "Lint and type errors are ratcheted; never add to the baseline" | one line | low |
| Script that fails | `scripts/ratchet.sh --max 12 -- eslint .` | an hour | high when run |
| Hook that runs it | a Stop hook that runs the quick check before the agent may finish | ten minutes | high, always |

The map keeps the rule, in the Hard rules table, with the enforcer named in the second column. The rule is for the reader; the script is for the gate; the hook is for the moment the agent would otherwise skip it.

### Hooks: the mechanism

Claude Code and Codex both run scripts at lifecycle events ([matrix](../tool-support-matrix.md)). Four hooks carry most of the value:

- **Before a tool runs** (`PreToolUse`): a guard that denies or asks before destructive commands and edits. The [guard template](../../templates/hooks/scripts/guard-destructive.py) denies force-pushes to `main`, recursive deletes outside the workspace, database resets and repository deletion; asks before hard resets, destructive SQL, risky remote commands, merges that auto-deploy and package publishes; and allows everything else, including anything it cannot parse.
- **After an edit** (`PostToolUse`): a tracker that remembers which files the session touched.
- **When the agent wants to stop** (`Stop`): a check that runs the quick check in every repository the session touched and blocks the stop once with the last line of the failing check as the reason.
- **At session start** (`SessionStart`): the branch, the uncommitted count and the head of the progress file, so the agent begins from the truth.

### Hooks fail open and stay fast

A hook that hangs blocks every session. A hook that crashes must not become a wall. Rules from the field: a short timeout on every hook (10 seconds for a guard, 150 for a stop check), exit 0 on any internal error, allow what you cannot parse, and emit one output field only. Two behaviours observed on Claude Code 2.1.280, October 2026, and worth knowing: the tool reads both a hook's stdout and its JSON without de-duplicating, and context injected at `SessionStart` does not reach subagents, so inject at `SubagentStart` too.

### The ratchet: a gate that survives

Demanding zero lint errors in a codebase that has forty of them gets the gate switched off within a day. The [ratchet](../../templates/scripts/ratchet.sh) says "no more than today": it counts findings, fails above a committed baseline, tells you to lower the baseline when the count drops, and hard-fails when the checker exits with an unexpected code, because a gate that passes because the tool failed to run is worse than no gate. Agents check only the files they touched; CI checks the count.

### Source-reading tests: the cheapest architecture guard

Before you reach for a dependency analyser, write a test that reads source files as text and fails on a forbidden pattern per folder: controllers never import the database client, workers never emit to sockets directly, only two files may sign a storage URL, every query carries the tenant filter, credentials never appear in trace payloads. The [architecture check](../../templates/scripts/arch-check.py) does this from a JSON rules file and prints `WHAT`, `WHY` and `FIX` lines an agent can act on. A field codebase enforces about thirty boundaries this way, in the ordinary test suite.

### Lint rules whose message names the fix

A restricted-syntax rule whose message says "window.scrollY is banned here; use the shared scroll helper, because the page scrolls inside a container on one mobile browser" is a guide and a sensor at once. The agent reads the fix in the error. The map's Hard rules row points at the rule.

### Pre-approve the checks

An agent that must ask permission to run the quick check learns to skip it. The repository's settings pre-approve exactly the check commands, and nothing broader ([Permissions and consent](06-permissions-and-consent.md)).

### Name the enforcer in the map

The Hard rules table is the contract between the two halves of the harness. A row with an enforcer is a sensor the agent can trust; a row that says "prose, no enforcer yet" is honest, visible, and next on the list.

## Do this today

1. Copy the [guard](../../templates/hooks/scripts/guard-destructive.py) and the [stop check](../../templates/hooks/scripts/require-check-before-stop.py) into `.claude/hooks/`, the [settings](../../templates/hooks/claude-code/settings.json) into `.claude/`, and start a new session.
2. Take the rule your agents break most often. Write the script that fails on it. Add the row to the Hard rules table with the script named.
3. Replace your zero-tolerance lint gate with the ratchet at today's count.

## Sources

Marmelab (4.4 %, ~85 %, "replace rules with executable scripts"); Lin et al. (structural elements transfer, prose does not); Hashimoto ("engineer a solution such that the agent never makes that mistake again"); Böckeler (sensors); Claude Code and Codex hook references; field notes. Links in [references](../references.md).
