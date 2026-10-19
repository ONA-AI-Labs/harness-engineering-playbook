# Start here

This playbook is for teams that already run coding agents in real repositories and want them to stay reliable as the codebase, the team and the number of agents grow. It assumes you know what an instruction file is and have felt an agent declare victory on a broken build.

## Three ways to read it

**Thirty minutes.** Read [What a harness is](part-1-foundations/01-what-a-harness-is.md), then [Enforcement over prose](part-2-control/04-enforcement-over-prose.md) and [Verify what you ship](part-2-control/05-verify-what-you-ship.md). Copy the [starter kit](../templates/STARTER.md) into one repository. Run the [audit](../tools/audit-harness.py). You will be at level 2 by the end of the day.

**The full path.** The five parts in order. Each chapter opens with the question it answers, gives the short answer, shows how things fail without it, describes the pattern, points at a template, and ends with a "Do this today" list and its sources.

**Just the files.** Go to [templates](../templates/) and the [tool support matrix](tool-support-matrix.md). Every template says where it goes and what it enforces.

## The map

| Part | Chapters | What you can do afterwards |
|---|---|---|
| 1 Foundations | [What a harness is](part-1-foundations/01-what-a-harness-is.md) · [Instruction files](part-1-foundations/02-instruction-files.md) · [Knowledge in the repo](part-1-foundations/03-knowledge-in-the-repo.md) | Explain the model-plus-harness split to your team; write a map instead of an encyclopedia |
| 2 Control | [Enforcement over prose](part-2-control/04-enforcement-over-prose.md) · [Verify what you ship](part-2-control/05-verify-what-you-ship.md) · [Permissions and consent](part-2-control/06-permissions-and-consent.md) | Turn repeated corrections into guards; stop "done" from meaning "tests passed" |
| 3 Continuity | [State and sessions](part-3-continuity/07-state-and-sessions.md) · [Memory and lessons](part-3-continuity/08-memory-and-lessons.md) | Hand work between sessions without loss; make the harness learn |
| 4 Scale | [Scope and delegation](part-4-scale/09-scope-and-delegation.md) · [Loops and automation](part-4-scale/10-loops-and-automation.md) · [Evals](part-4-scale/11-evals.md) · [Observability](part-4-scale/12-observability.md) | Run several agents across several repos; prove a harness change helped |
| 5 Operate | [Maintaining the harness](part-5-operate/13-maintaining-the-harness.md) · [Enterprise rollout](part-5-operate/14-enterprise-rollout.md) | Prune what rots; roll the practice out across an organisation |

Then: [Field lessons](field-lessons.md) (rules from real incidents), the [tool support matrix](tool-support-matrix.md), the [glossary](glossary.md) and the [references](references.md).

## The one idea

The model decides what code to write. The harness decides everything else: what the model sees, what it may do, how it finds out it was wrong, what survives the session. Reliability lives in the second half. Every chapter is about making one piece of that second half explicit, enforced and measured.

## Vocabulary you will meet on every page

- **Guide**: something that acts before the agent does (an instruction file, a skill, a bootstrap script). **Sensor**: something that acts after (a linter, a test, a review agent). A harness needs both. (Böckeler, see [references](references.md).)
- **Quick check**: lint and types in under 90 seconds, run before the agent stops. **Full check**: the definition of done, including booting what you ship.
- **Level**: where a repository stands on the [maturity model](part-5-operate/14-enterprise-rollout.md#the-maturity-model), 0 to 4, as scored by the audit.
