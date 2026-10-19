# Glossary

**Agent.** A model plus a harness: the loop that lets a model read, act, observe and act again inside your environment.

**Harness.** Everything around the model that is not the model: instructions, tools, permissions, memory, hooks, checks, orchestration. The part you engineer. See [What a harness is](part-1-foundations/01-what-a-harness-is.md).

**Harness engineering.** Making the harness explicit, enforced and measured, so that the same model produces reliable work in your repositories.

**Guide and sensor.** A guide acts before the agent (an instruction file, a skill, a bootstrap script, a code generator). A sensor acts after (a linter, a type checker, a test, a boot check, a review agent). Böckeler's terms.

**Computational and inferential.** A computational control is deterministic and fast (a test, a lint rule). An inferential control uses a model (a review agent, an LLM judge). Prefer computational where it exists; calibrate inferential before trusting it.

**Instruction file.** The file an agent reads at the start of every session: `AGENTS.md` for most tools, `CLAUDE.md` for Claude Code. A map, not an encyclopedia.

**Map, not encyclopedia.** An instruction file under about a hundred lines that says what the system is, which commands to run, what done means, which rules are enforced by what, and where the detail lives.

**Hook.** A script the agent tool runs at a lifecycle event (before a tool call, after one, when the agent wants to stop). The mechanism that turns a prose rule into an enforced one.

**Guard.** A hook that denies or asks before a destructive action. Fails open by design.

**Quick check.** Lint and types in under 90 seconds; the command a Stop hook runs. **Full check.** The definition of done: quick check, tests, build, boot check.

**Boot check.** Starting the built artifact and waiting for a health signal. Catches what unit tests cannot: a bundle that does not load.

**Ratchet.** A gate that allows no more than today's count of pre-existing findings and lowers the number over time. The honest alternative to a zero-tolerance gate that gets switched off.

**Architecture check.** A test or script that reads source files and fails on forbidden patterns per folder, with a WHAT, WHY and FIX message.

**Definition of done.** The list a change must satisfy before anyone says "done", including what a person checks by hand and the rule that "not verified" must be stated.

**Feature list.** A machine-readable list of what the system must do, with a verify command and a `passes` flag per item. The scope boundary for long-running work.

**Progress file.** The handoff between sessions: current state, what was done, what is next, what is blocked.

**Memory.** Small files, one lesson each, with a rule, the incident behind it, how to apply it, its scope and its expiry; indexed by a one-line-per-memory file loaded every session.

**Incident to rule.** The workflow that turns a mistake into a rule, the rule into a guard, and gives the guard an owner and an expiry.

**Contract.** A short, pasted description of an API change that crosses repositories: routes, fields with casing, auth, errors, one task line per repo. The source of truth for every agent working on it.

**Subagent.** An agent spawned by another agent with its own context. Costs a full context; use one per repository the task touches, never "just in case".

**Eval.** A set of tasks with a verify command (or a calibrated judge), run through the agent to measure whether a harness change helped. Capability evals start low; regression evals stay near 100 %.

**Judge.** A model that grades an output against a rubric and a schema. Needs a negative control, an "unknown" option and calibration against human grades.

**Harness rot.** Controls that stay after the failure they prevented stopped happening, costing tokens and attention. The cure is an incident and an expiry on every control.

**Maturity level.** 0 unharnessed, 1 instructed, 2 enforced, 3 continuous, 4 governed. Scored by `tools/audit-harness.py` on enforcement, not on file presence.
