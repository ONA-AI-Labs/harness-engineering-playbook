# 9. Scope and delegation

**When should one agent become many?**

Later than you think. One agent, one task, one repository is the default. A second agent is justified when a task genuinely spans two repositories, or when the work would bloat the main session's context; never "just in case", and never to supervise another agent.

## The short answer

Keep process and knowledge apart; take the cheapest route that fits; give every worker agent the same three closing blocks; fence it to one repository with a pasted contract; resume it instead of respawning it; and make review opt-in.

## How it fails without this

- A triage agent hands to a lead agent who hands to a repository agent: three contexts paid to do one job. The authors measured one sample turn of their own setup at about a million cached re-read tokens against about twenty-four thousand output tokens, and wrote in the commit that most of the spend came from stacked contexts and long-lived sessions, not from the work itself.
- Microsoft's Azure SRE agent found that problems needing more than four handoffs almost always failed, and rolled fifty-plus specialists back to a generalist.
- Marmelab's survey found reviewer agents reduced success by about 8 % in the settings it measured.
- Parallel builder agents each re-implemented shared components that already existed, because nobody told them to look first.

## The pattern

### Process in one place, knowledge in another

A workspace-level plugin or skill owns *how* work flows: when to spawn, what to paste, how to report. Each repository's map owns *what* the code is. The field version is a plugin of five repository agents, one reviewer and two commands, with the note "this plugin holds process only; product knowledge lives in each repo's own map". When the process changes, one file changes.

### The cheapest route

1. **Small task, one repository**: do it in the main session. No subagent, no plan file, no report file.
2. **Large task, one repository**: dispatch that repository's agent with a self-contained brief (goal, files if known, acceptance criteria).
3. **More than one repository**: write a contract, confirm it once, dispatch one agent per repository in a single step.

Two rules keep the route cheap. Never read a repository's code yourself before dispatching its agent: the agent will read it anyway, and doing both pays twice. And answer an agent's question by resuming the same agent, never by spawning a fresh one that re-reads everything.

### The three closing blocks

Every worker agent's definition ends with the same three blocks, identical across repositories (verify with a hash in CI):

- **Checks for this repo**: the exact commands, plus the traps written next to the checks that miss them ("after a new dependency, build and run the boot check").
- **Token budget**: read the map once; open only the files the brief names or one targeted grep points at; read line ranges; no exploratory tours; verify once at the end; errors already present in files you did not touch are not yours; no servers, screenshots, CI watching or deploys unless the brief says so; pipe noisy output through `tail`.
- **Report**: at most fifteen lines, fixed fields: `Done`, `Files`, `Checks` (command → result, with timings), `Other repos need`, `Question`, `Not verified`.

The [repo agent template](../../templates/agents/repo-agent.md) has all three.

### The scope fence and the contract

A worker works only inside its repository or the named worktree of it. For a change that crosses repositories, a [contract](../../templates/docs/contract.md) of twenty lines or fewer is pasted into every brief: routes, fields with their casing per endpoint, auth, errors, one task line per repository, and what each agent must not touch. The contract is the source of truth; a worker that needs a deviation reports it under `Question` rather than making it silently, and it never reads another repository's tree to find out.

Changing an existing API shape stays backward compatible unless the contract says otherwise: clients already installed on phones keep calling the old shape.

### Review is opt-in

A read-only contract reviewer on a cheap model, with five fixed checks (routes, field casing, auth, error handling, compatibility with installed clients) and a one-word verdict, runs only when asked or when a shipped client's API shape changed. The [template](../../templates/agents/contract-reviewer.md) is sixteen lines. Everything else is reviewed by the checks and by a person.

### A heavy flow, when it is earned

A design approved section by section, one plan per repository, a build ledger with a "cost if wrong" line on every judgment call, a fresh reviewer on a stronger model, and a GO-gated runbook: the field team uses this flow for one kind of change, the irreversible kind (deleting data, changing what is stored). Every other change takes the cheap route. The heavy flow is opt-in because it is expensive, and because used by default it gets abandoned.

### Operations

- Spawn in batches of three or four; a burst of parallel agents reading large inputs hits rate limits together, and resuming them costs less than relaunching.
- Use a cheaper model for boilerplate-heavy fan-outs and the frontier model for the main session.
- Watch for stalls: an agent listed as running that has changed no file in fifteen minutes needs a nudge.
- Check "I built X" against git before trusting it.

## Do this today

1. Write the cheapest-route rule into your workspace instructions.
2. Create one repository agent from the template, with the real checks and traps.
3. Count the handoffs in your current multi-agent setup. More than two: remove one.

## Sources

Marmelab (Azure SRE handoffs; reviewer agents); Anthropic, *How we built our multi-agent research system* (when subagents pay off); field notes (the plugin's evolution, the cost sample, the three blocks, the contract). Links in [references](../references.md).
