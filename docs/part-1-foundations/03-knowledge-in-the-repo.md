# 3. Knowledge in the repository

**If the agent cannot see it, does it exist?**

No. A decision in a chat thread, a runbook in a wiki, a convention in someone's head: to the agent, none of these exist. The repository is the only system of record an agent can read, so everything it needs to work correctly has to be in it.

## The short answer

Give the repository a small, predictable knowledge layout, keep every document that the map points at current, mark the ones that are not, and treat prompts and rules as versioned code.

## How it fails without this

- The agent re-derives a decision the team already made, and decides differently.
- The agent follows a document that was true two migrations ago.
- A prompt is edited in place; nobody knows which version produced last week's outputs.
- Three agents on three branches each write their own explanation of the same subsystem.

## The pattern

### The layout

```text
AGENTS.md                 the map (chapter 2)
docs/
  ARCHITECTURE.md         one screen: request path, data, background work, enforced boundaries
  DECISIONS/              numbered decision records: context, decision, consequences
  PROGRESS.md             the handoff between sessions (chapter 7)
  agent/<topic>.md        the detail the map points at, one topic per file
  generated/              schema dumps and API descriptions produced by a script, never by hand
  references/             vendor and library notes in a form the agent reads well (llms.txt style)
  incidents/              one file per incident that became a rule (chapter 8)
```

OpenAI's field report describes the same shape at larger scale: a routing instruction file, design documents, execution plans split into active and completed, a quality score by domain, generated references, and a standing "garbage collection" duty for the agents themselves.

### Decisions get records

A decision record is three paragraphs: the context, the decision, the consequences. The map points at it. An agent that wants to change a constrained thing reads the record and proposes a new one instead of making a silent change. The [template](../../templates/docs/DECISIONS/0001-record-architecture-decisions.md) is the first record: the decision to keep records.

### Generated, not hand-written

A database schema dump, an OpenAPI description, a route list: if a script can produce it, a script produces it, and a test fails when the committed copy drifts from what the script would produce today. The test's name tells the agent which command regenerates the file.

### Prompts and rules are code

A prompt that lives in a code string is edited by accident. A prompt that lives in `prompts/<name>.md` can be pinned: a test records the file's hash next to a version constant and keeps every past hash as history, so editing the prompt without bumping the version fails the suite. Every output the prompt produces carries the version, and an evaluation can be compared across versions ([Evals](../part-4-scale/11-evals.md)). The same goes for deterministic rules and for question wording that thresholds were measured against.

### Stale is a state, not a deletion

Old documents are evidence. Mark them in the map ("stale, don't follow") and in their own first line, and move on. Deleting them loses the history and does not stop the agent from finding them in git.

### Garbage collection is a task

Knowledge rots at the speed of the codebase. Make cleanup a recurring task rather than a virtue: once a sprint, an agent reads the map and every topic file, lists what no longer matches the code, and opens one pull request. OpenAI's report calls this mechanism garbage collection; the point is that small problems get cleaned at any time instead of piling up.

## Do this today

1. Create `docs/ARCHITECTURE.md` from the [template](../../templates/docs/ARCHITECTURE.md): one screen, pointers only.
2. Find the one document the agent followed last month that was wrong. Mark it stale in the map.
3. Move your prompts into files and pin them with a hash test.

## Sources

OpenAI, *Harness engineering* (docs as the knowledge base, garbage collection); field notes (prompt hash pins, generated seed drift tests). Links in [references](../references.md).
