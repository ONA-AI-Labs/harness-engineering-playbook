# 12. Observability

**What should the harness measure?**

Whether it fired, what it caught, and what it cost. A harness nobody measures is a set of beliefs about what the agent does.

## The short answer

Log every hook decision and every stop-time check to one append-only file; stamp every generated output with the versions that produced it; read the log weekly and the transcripts monthly; adopt the OpenTelemetry conventions when the log outgrows a file.

## How it fails without this

Marmelab's survey found that five of 391 repositories measure whether their harness is used at all. Without measurement: the guard that blocks nothing and the guard that blocks everything look the same; a hook that fails silently is indistinguishable from one that never fires; a rule in the map cannot be shown to have mattered; and when quality drops, nobody can say which prompt version produced the bad outputs.

## The pattern

### One line per event

The [guard](../../templates/hooks/scripts/guard-destructive.py) and the [stop check](../../templates/hooks/scripts/require-check-before-stop.py) each append one JSON line per decision to a metrics file (`~/.claude/metrics/harness.jsonl` by default; set `HARNESS_METRICS_FILE` to move it). The file is private and rotated, an allowed command is logged as its program name and a hash only, and the command text kept for ask and deny decisions is redacted of known secret shapes first; `HARNESS_LOG_COMMANDS` switches that between `none`, `redacted` and `full`. A log of what agents tried to run is sensitive by nature: keep it where your other audit logs live. timestamp, event, decision or status, reason or summary, session, agent type, and the command or repository. The [stats script](../../tools/harness-stats.py) answers the first question a team asks:

```text
184 events
  PreToolUse   allow    175
  PreToolUse   ask      8
  PreToolUse   deny     1
last interventions:
  16:02 PreToolUse deny  git push --force origin main   force-push to main/master rewrites shared history
  16:14 PreToolUse ask   rm -rf $S/depstest             the guard cannot resolve that variable; confirm
  (allowed commands appear as a program name and a hash, never as text)
```

The second line of that example is how the guard's first bug was found: three "ask" decisions on scratch-folder cleanups whose paths used a variable set earlier in the same command. The fix shipped within the hour because the log showed it.

### What to log

| Signal | Why |
|---|---|
| guard decisions (allow, ask, deny) with the command | shows what the harness prevents and its false positives |
| stop-check results per repository with timings | shows whether the quick check is fast enough and how often it catches something |
| which skills fired, which hooks ran, per session | tells you which parts of the harness are dead weight |
| edits per file and tool calls per session | loop detection; a file edited twelve times is a doom loop |
| cost: cached versus output tokens, per turn | the authors' delegation redesign started from one sample of their own sessions showing a million cached tokens against twenty-four thousand output |
| eval pass rate per run, with versions | the only trend that proves a harness change helped |

### Stamp outputs with their provenance

Every generated artefact (a summary, a report, a code change made by an automated loop) carries the model, the prompt version, the renderer or template version, and a fingerprint of the exact instructions. When quality moves, the fingerprint says which combination produced it. Prompts live in files with hash-pinned versions ([Knowledge in the repo](../part-1-foundations/03-knowledge-in-the-repo.md)), so the stamp is cheap.

### An observer hook that never blocks

A hook on every event can post the event to a dashboard, a queue or a local app. The field version posts with half-second and one-and-a-half-second timeouts, falls back to a capped local file when the receiver is down, skips tool events in the fallback to bound the size, and always exits 0. An observer that can block a session is a liability; one that cannot is free telemetry.

### Shadow numbers, never shadow content

A pipeline in shadow mode logs parse rate, structure match, length ratio and cost. It never logs the content it produced from real traffic; the comparison runs on numbers and on an eval set with fixtures you own.

### OpenTelemetry when the file is not enough

The generative-AI semantic conventions define span and attribute names for model calls, tool calls and agent runs. A team with more than one service emitting agent telemetry should adopt them early; renaming attributes later is the expensive part. Marmelab's recommendation is the same: instrument everything, log to OpenTelemetry or a custom collector.

### Read the transcripts

Numbers say that something changed; transcripts say why. Anthropic's eval guide is blunt: you do not know whether your graders work until you read transcripts and grades from many trials. Put it on the calendar: ten transcripts a month, picked from the runs that moved.

## Do this today

1. Install the guard and the stop check; after a week, run `tools/harness-stats.py` (from a playbook checkout, or copied next to your hooks) on `~/.claude/metrics/harness.jsonl` and read the interventions.
2. Add the prompt version and model to every generated output's metadata.
3. Pick ten transcripts from last week and read them.

## Sources

Marmelab (five of 391 measure usage; instrument everything); Anthropic, *Demystifying evals for AI agents* (read transcripts); OpenTelemetry semantic conventions for generative AI; field notes (the metrics file, the observer hook, output provenance, shadow numbers). Links in [references](../references.md).
