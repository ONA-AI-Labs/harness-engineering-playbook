# 11. Evals

**How do you know a harness change helped?**

By running the same frozen set of tasks before and after, grading each task the same way, and reading the transcripts of the ones that changed. Everything else is an anecdote.

## The short answer

Twenty to fifty tasks drawn from real failures, each with a deterministic verify command where one exists and a calibrated judge where one does not; an environment that leaks nothing into production metrics; a negative control that must fail; results written to a file you can diff. Measure, then gate only where a threshold truly matters.

## How it fails without this

Marmelab's survey found that 60 % of harnesses have neither tests nor evals and that seven repositories out of 246 have both. Without an eval set, every harness change is argued from one run. Anthropic's eval guide lists the ways evals go wrong once they exist: rigid step-checking that breaks on valid variations, saturated tasks at 100 % that no longer signal, shared state between runs, tasks nobody can solve, graders with inverted logic, and agents that bypass the task instead of solving it. From the field: a small judge model gave full marks to outputs written in the wrong language and to outputs whose two parties had swapped roles, until a negative control exposed it.

## The pattern

### Vocabulary

A **task** has inputs and success criteria; a **trial** is one attempt; a **grader** scores it; a **transcript** is the full record; the **outcome** is the final state. **Capability evals** start at low pass rates and are targets; **regression evals** stay near 100 % and catch decay. **pass@k** is the chance of at least one success in k tries; **pass^k** the chance all k succeed, which is what a user feels.

### Build the set from failures

Start with the pre-release checks you already do by hand and the tasks users actually attempt. Prioritise by the bug tracker. Each task needs a reference solution so you know it is solvable, and two people must agree on pass or fail before it joins the set. Balance the set: tasks where the agent should act and tasks where it should refuse, so you are not optimising one side. The [task file](../../templates/evals/tasks.jsonl) is one JSON line per task: an id, a prompt, a verify command.

### Deterministic first

The verify command decides. `npm test -- --grep 'profile without email'` is a grader that is fast, cheap, objective and easy to debug. Run cheap deterministic lints before any model-based judge and let the two cross-check each other: the authors' own eval runs eleven deterministic lints (placeholders present, forbidden sections, labels leaked, length policy) before the judge sees anything.

### The judge, when you need one

- Give the judge what it cannot know: today's date and timezone, the exact headings asked for, the length budget and the actual length, the ground-truth facts, each scoped to a short explicit list.
- Fence untrusted text (the transcript, the agent's output) in tags and defuse any tags inside it.
- A strict output schema ([template](../../templates/evals/judge-schema.json)), temperature zero, one retry that sends back the exact parse error, and a null verdict after that.
- Give the judge an "unknown" out and separate judges per dimension; a single grader that scores everything drifts toward the mean.
- Grade what the agent produced, not the path it took.
- Pick the judge model by the mistakes it missed, not by its price. Run the rubric ([template](../../templates/evals/judge-rubric.md)) against a few human-graded cases first.

### The negative control

Every run includes one case where the output belongs to a different task. It must score at the bottom. A judge that passes it is broken, and nothing else in the run can be trusted. The authors' end-to-end suite grades output B against input A as its first test, and fails the run if the score is above 2 of 5.

### Through the real path

Evaluate through the same path production uses, the real endpoint and the real streaming, not a faster in-process shortcut. If a shortcut exists for speed, label it non-faithful in its own name and never quote its numbers as production numbers. The field learned this when the shortcut drifted from production and the numbers stayed green.

### Reproducible and diffable

Each run writes a labelled JSON file with the model, prompt and renderer versions, the options, the aggregate numbers and every row, plus every generated output as a readable file. The [runner](../../templates/evals/run-evals.py) writes one line per task; the [comparer](../../templates/evals/compare-results.py) prints per-task deltas and counts fixed against regressed. Three modes pay for themselves: compare two runs; re-judge saved outputs with a new rubric without regenerating; dry-run to print the prompts and spend nothing. Freeze sampled upstream steps when you compare downstream models, or the noise swamps the signal.

### Gate where thresholds are real

Most evals measure; they do not gate. A classifier whose wrong-answer rate above 5 % or p95 latency above 800 ms would ship a visible defect gets an exit-code stop rule. A summary quality score does not; it gets a comparison and a person reading the ten transcripts that moved.

### End-to-end runs with a judge

Long production-like runs need soft assertions: every check is recorded to an append-only log, a crash still leaves a report, verdicts are pass, warn or fail, the judge being unavailable is a warning and never a failure, and the run fails by exit code at the end. Keep a negative control in the corpus (an empty input, a document with nothing to extract), use no admin credentials, and clean up only what the run created.

## Do this today

1. Write ten tasks from your last ten agent failures into `evals/tasks.jsonl` with verify commands.
2. Run the [runner](../../templates/evals/run-evals.py) once with your agent and keep the results file as the baseline.
3. Make your next harness change, run it again, and read the transcripts of every task that changed.

## Sources

Anthropic, *Demystifying evals for AI agents* (taxonomy, 20–50 tasks, graders, pitfalls); Marmelab (60 % without tests or evals); LangChain (benchmarks as the measure of harness changes); field notes (deterministic lints before the judge, the judge's inputs, the negative control, faithful versus shortcut paths, soft assertions). Links in [references](../references.md).
