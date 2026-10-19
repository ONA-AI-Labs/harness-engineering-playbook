# 13. Maintaining the harness

**What rots, and how do you prune?**

Every control in a harness encodes an assumption about what the model cannot do on its own. Models improve; the assumptions stay. A control that outlives its reason costs tokens and attention on every session and teaches the team to ignore controls. That is harness rot, and the cure is bookkeeping: an incident and an expiry on every control, and a habit of removing one thing at a time.

## The short answer

Write down why each control exists and when it should go. Review the list on a schedule. Remove one control at a time and measure. Keep the structure (hooks, scripts, files) and expect the prose to be the first thing to retire.

## How it fails without this

- Anthropic's harness team tried radical simplification first and could not tell which components were load-bearing; methodical single-component removal worked.
- A plugin for delegating work grew a triage front door, a five-state machine, a report file per task and a knowledge loop; the team measured that most of the spend came from stacked contexts and long-lived sessions, not from the work, and cut it to two commands and six agent definitions.
- A map said lint was "advisory only" for months after lint had become a CI gate. Nobody was wrong when they wrote it.

## The pattern

### An incident and an expiry on everything

The [incident-to-rule file](../../templates/docs/incident-to-rule.md) and the [memory template](../../templates/memory/_template.md) both end with an expiry: the condition under which the control is no longer needed. "When the tool validates this itself." "When the test suite runs against the built artifact." "Review on 2027-01-01." A control without an expiry is a control nobody is allowed to remove.

### Ablate one at a time

Anthropic's rule: find the simplest solution possible, and only increase complexity when needed; and, because every component encodes an assumption, stress-test the assumptions as models improve. The method is to remove one component, run the eval set, read the transcripts of what changed, and keep or restore. Their second harness dropped sprint decomposition when a newer model sustained longer tasks on its own; the files, the evaluator and the feature list stayed. Expect the same shape: prose scaffolding retires first, structural pieces last.

### What transfers and what does not

Lin et al. found that structural harness elements (tools, middleware, memory) transferred across models with gains of 5.1 to 10.1 points, while prose prompting did not. Fan et al. found that planning scaffolds help weaker models for accuracy and stronger models for cost, which is a different reason to keep them, and that context management matters most under tight budgets. The practical reading: when a model upgrade lands, re-run the evals, then retire prose before you touch structure.

### Recursive harnessing, for humans

Harness² formalises the loop a team runs by hand: propose a change to one editable component, probe it on tasks, compose the version that helped, and keep the lessons in a persistent improvement harness that guides the next round. Lin et al. go one step further and make each edit a falsifiable contract: it states the effect it expects, and the next run confirms or refutes it. You do not need the automation to adopt the discipline. Each harness change in a pull request says what it expects to improve and which eval will show it.

### Versioning the harness itself

- Templates carry a version in the changelog; a repository records which version it adopted in its map.
- Shared blocks in agent definitions (the token budget, the report format) stay identical across agents; a CI check hashes them.
- The map's "Known sharp edges" are dated; a sharp edge older than six months is reviewed.
- Hook scripts are tested like code ([tests](../../tools/tests/)). A hook change without a test is a change to the harness nobody can verify.

### The maintenance calendar

| When | What |
|---|---|
| every pull request | the Hard rules table still names a real enforcer for each row; new rules get an expiry |
| monthly | read the harness stats and ten transcripts; retire or fix controls that fired on false positives |
| each model upgrade | run the eval set; remove prose controls one at a time; keep structure |
| quarterly | review every expiry; audit allow lists; garbage-collect `docs/agent/` |

### Signs of rot

- A hook that has not fired in a quarter, or fires only on false positives.
- A rule everyone has learned to work around.
- A map section nobody can explain.
- Two documents that disagree and both are linked from the map.
- A reviewer agent whose verdicts nobody reads.

## Do this today

1. List every hook, script and hard rule. Next to each, write the incident that created it and the condition that retires it. Blanks are the first review.
2. Pick the control with the weakest reason. Remove it on a branch, run the evals, decide.
3. Put the maintenance calendar in the contributing guide.

## Sources

Anthropic, *Harness design for long-running application development* (assumptions, simplest solution, single-component removal); Lin et al. (what transfers; falsifiable edits); Fan et al. (planning and context management by model strength); Google Research, *Harness²* (propose, probe, compose; the improvement harness); Marmelab (harness rot, expiry conditions); field notes (the plugin that shrank; the "advisory" lint line). Links in [references](../references.md).
