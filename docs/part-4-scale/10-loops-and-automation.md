# 10. Loops and automation

**How do you stop prompting?**

By giving the work a loop instead of a conversation: a goal, a maker, a checker, a stop condition, a budget and a kill switch. Then let a schedule, a pull request or a CI job start it, and read the results instead of the chat.

## The short answer

Start with one loop that already has a deterministic checker (the quick check, a test suite, a verify command). Put the budget and the stop condition in before the first run. Measure the loop the same way you measure a harness change: with an eval set, before and after.

## How it fails without this

- A loop with no checker produces output that looks like progress. A loop with no stop condition runs until the budget is gone.
- An agent in a loop re-runs a failing check until the harness's continuation cap ends the turn (Claude Code stops after eight consecutive hook-driven continuations); the same failure, retried eight times, is noise, not work.
- The contributing guide says the end-to-end suite runs on every push; it runs only on manual dispatch, because someone made a cost decision and did not write it down. Agents and people both trust the guide.

## The pattern

### The maker-checker loop

The simplest loop that works: a maker agent implements one feature from the feature list; a checker runs `scripts/verify-feature.py`; the maker gets the failing verify output and tries again, at most N times; the loop stops on pass, on N, or on budget. The checker is deterministic wherever possible. Anthropic's three-agent harness (planner, generator, evaluator) is this loop with an inferential checker and a planner in front; it produced a playable application where a single agent produced an unplayable one, at twenty times the cost.

### Loops that already exist in your tools

- **The Stop hook** is a one-step loop: the agent wants to stop, the check runs, the agent continues once if it failed. The [template](../../templates/hooks/scripts/require-check-before-stop.py) blocks once and lets the second identical failure through with a note, so a pre-existing failure cannot trap the agent.
- **Loop detection middleware**, as in LangChain's harness, counts edits per file and tells the agent to reconsider after N. The same idea fits a hook that counts tool calls per session.
- **Headless runs**: every tool has one (`claude -p`, `codex exec`, `gemini -p`, `copilot -p`, `agent -p`; [matrix](../tool-support-matrix.md)). A headless run with a prompt, a verify command and a timeout is the unit of every automated loop, including the [eval runner](../../templates/evals/run-evals.py).

### Scheduled and CI-triggered agents

A nightly agent that opens one pull request cleaning stale documentation; a pull-request agent that runs the quick check, reads the diff and comments; a release agent that drafts the changelog from merged pull requests. Each is a headless run with a narrow brief and a deterministic check. Three rules from the field:

- **Budget before loop.** A spend cap per run and per day, enforced by the tool's limits, not by the prompt.
- **Idempotent, and bounded by time.** A recovery or backfill job selects with a look-back window and is safe to run twice. Its first production run is a dry run with counts ([Permissions and consent](../part-2-control/06-permissions-and-consent.md)).
- **A kill switch that is a file or a flag**, not a conversation: `off`, `shadow`, `on`.

### Shadow mode

Before a new automated pipeline replaces an old one, run both on real traffic and log numbers only: parse rate, structure match, length ratio, cost. Never log content from the shadow path. When the numbers hold for a week, flip the flag. The field pattern is three states, `off`, `shadow`, `on`, and a flag per pipeline.

### CI cost decisions, written down

Automation costs minutes. The decisions teams make to save them are sensible, and dangerous when undocumented:

- CI runs on pull requests only, and the deploy job repeats the gates on `main`, so a second full run is not paid for.
- Expensive runners (macOS, GPUs) run only when the paths they cover change.
- The slow end-to-end suite runs on manual dispatch until traffic justifies the minutes.

Each of these goes into the map's sharp edges and the contributing guide, with the condition that reverses it. The field repository whose guide claimed "end-to-end on every push" had the suite on manual dispatch for a month; the map fix was one paragraph.

### Scale, honestly

Stripe's internal agents reportedly open about 1,300 pull requests a week with about 70 % merged without rework (figures via Marmelab's survey). That rate comes from the same mechanics at larger scale: narrow briefs, deterministic checks, and a merge gate that is a check, not a person reading everything. It also comes with an eval set and an observability stack ([Evals](11-evals.md), [Observability](12-observability.md)); do not copy the throughput without the two.

## Do this today

1. Turn one recurring chore into a headless run with a verify command and a timeout. Run it by hand three times before scheduling it.
2. Add a budget and a kill-switch flag before the first scheduled run.
3. Find one CI cost decision that is not written down. Write it into the map with its reversal condition.

## Sources

Anthropic, *Harness design for long-running application development* (planner, generator, evaluator); LangChain (loop detection, time budgets); Claude Code hooks reference (the continuation cap); Marmelab (Stripe figures); field notes (shadow mode, CI cost decisions, the documentation drift). Links in [references](../references.md).
