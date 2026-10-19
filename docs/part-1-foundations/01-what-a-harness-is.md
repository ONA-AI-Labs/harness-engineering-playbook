# 1. What a harness is

**Why do strong models still fail in real repositories?**

Because the model is half of the agent. The other half is the harness: what the model sees, what it may do, how it finds out it was wrong, and what survives the session. That half is yours, and until you engineer it on purpose, it is whatever your repository happens to be.

## The short answer

Agent = Model + Harness. The model decides what code to write. The harness decides everything else. Reliability lives in the harness, and the same model behaves very differently inside different ones.

## How it fails without one

The failures look like model failures and are not:

- The agent reports "done" after its tests pass, and the build does not boot.
- A long task loses the thread halfway through a second session, because nothing from the first was written down.
- The agent fixes the bug you asked about and three things you did not, because nothing bounded the scope.
- The same mistake comes back next week, because the correction lived in a chat thread.
- The agent cannot find the design decision that explains the odd shape of a module, because it lives in someone's head.

Every one of these has a harness fix, and none of them has a prompt fix that lasts.

## The pattern

### Guides and sensors

Böckeler's model is the most useful split. A **guide** acts before the agent does: an instruction file, a skill, a bootstrap script, a code generator, a language server. A **sensor** acts after: a linter, a type checker, a test, a boot check, a review agent. Her warning is the whole discipline in one sentence: with only sensors you get an agent that keeps repeating the same mistakes, with only guides you get an agent that encodes rules but never finds out whether they worked. You need both, and they need to agree.

Each kind comes in two flavours. **Computational** controls are deterministic and fast: tests, linters, type checkers, architecture checks. **Inferential** controls use a model: a review agent, an LLM judge. Use computational controls wherever one exists; calibrate inferential ones before you trust them (see [Evals](../part-4-scale/11-evals.md)).

### What you can edit

Two recent attempts to list the editable parts agree closely. Weng lists seven: the system prompt, tool descriptions, tool implementations, middleware, skills, sub-agent configuration and long-term memory. Harness² lists eight, grouped as context construction (system prompt, guardrails, memory, skills), tool interface (tool guidance, scripts), orchestration (subagents) and middleware (plugins). Whichever list you use, notice what is on it: files in your repository and settings in your agent tool. Nothing requires retraining a model.

### Every component encodes an assumption

Anthropic's harness team put it precisely: every component in a harness encodes an assumption about what the model cannot do on its own, and those assumptions are worth stress-testing because they may be wrong and because they go stale as models improve. That is why this playbook asks for an incident and an expiry condition on every control ([Maintaining the harness](../part-5-operate/13-maintaining-the-harness.md)).

## The evidence that the harness moves results

| Report | Same model, different harness | Source |
|---|---|---|
| LangChain, Terminal-Bench 2.0 | 52.8 % → 66.5 % from prompt phases, a pre-completion checklist, loop detection and time budgets; the model fixed | [references](../references.md) |
| Anthropic, long-running app build | $9 and 20 minutes solo (unplayable) against $200 and 6 hours with planner, generator and evaluator (playable) | [references](../references.md) |
| Lin et al., automatic harness evolution | pass@1 69.7 % → 77.0 % over ten iterations, above a human-designed harness at 71.9 % | [references](../references.md) |
| Marmelab survey | one model across eight harnesses on 25 tasks: 68 % to 88 % success | [references](../references.md) |
| Harness², frozen models | +11.5, +4.5 and +11.8 points on three professional benchmarks | [references](../references.md) |

The spread inside a single row is the point: the harness is worth as much as a model generation.

## Where this playbook starts

An introduction to coding agents teaches the basics on a toy application: an instruction file, a progress file, a test command. A real product adds what the toy does not have: several repositories, pre-existing debt, a production environment that auto-deploys, other people's uncommitted work, budgets, and an organisation that must adopt the practice. The next thirteen chapters are about that.

## Do this today

1. Write down, for one repository, every guide (what the agent reads before acting) and every sensor (what tells it it was wrong). Most teams find three guides and one sensor.
2. Next to each sensor, write the failure it would miss. "Tests pass but the bundle does not boot" is the usual first entry.
3. Pick the one sensor you can add this week. Chapter 5 shows the boot check.

## Sources

Böckeler, *Harness engineering for coding agent users*; Weng, *Harness Engineering for Self-Improvement*; Google Research, *Harness²*; Anthropic, *Harness design for long-running application development*; LangChain, *Improving Deep Agents with harness engineering*; Lin et al., *Agentic Harness Engineering*; Marmelab, *The State of AI Harness Engineering 2026*. Links in [references](../references.md).
