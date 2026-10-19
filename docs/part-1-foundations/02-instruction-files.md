# 2. Instruction files

**Why does one giant instruction file fail?**

Because it is read in full at the start of every session, competes with the tool's own instructions for the model's attention, and rots faster than anyone maintains it.

## The short answer

Write a map, not an encyclopedia: under a hundred lines that say what the system is, which commands to run, what done means, which rules are enforced by what, and where the detail lives. Move everything else into topic files the agent opens only when a task needs them.

## How it fails without this

A field example, numbers rounded. A backend's instruction file started at about 1,400 words. Every feature pull request appended its deployment order, environment variables and failure modes, because that felt like the responsible place. Ten weeks later it was 23,000 words, roughly 66,000 tokens, and the delegation rules said "read the instruction file once". Every agent paid that bill before reading a line of code, and the file still said lint was "advisory only" long after lint had become a CI gate.

The mechanics behind the failure are known. HumanLayer reports that frontier models follow about 150 to 200 instructions reliably and that an agent tool's own prompt already spends about 50 of them; past that, every instruction degrades the others. Marmelab's survey found that adding instructions raises reasoning tokens by 14 % to 22 % with marginal gains. A file nobody can read in one sitting is a file nobody checks for contradictions.

## The pattern

### The first ten lines say what the system is

An agent that does not know what it is working on makes plausible changes to the wrong thing. One paragraph: what it does, for whom, the stack, where it runs, what it talks to.

### The sections, in this order

1. **Commands**: the quick check, the full check, how to run and install. Exact commands, not descriptions.
2. **Done means**: the full check, what a person must check by hand, and the rule that "not verified" must be listed. See [Verify what you ship](../part-2-control/05-verify-what-you-ship.md).
3. **Hard rules**: a two-column table, rule and enforcer. Each row names the lint rule, test file, script, hook or CI gate that enforces it, or says "prose, no enforcer yet". The honest "prose" rows are your backlog for [Enforcement over prose](../part-2-control/04-enforcement-over-prose.md).
4. **Layout**: one line per folder that matters.
5. **Detail by topic**: one line per file in `docs/agent/`, which is where the encyclopedia went.
6. **Known sharp edges**, each with the date you checked it.

The [template](../../templates/AGENTS.md) has the skeleton. The two field maps below are what it looks like filled in, shapes only:

```text
What this is (8 lines) · Commands (6) · Done means (7) · Architecture overview (6)
Feature guides index (27 lines, one per topic file) · Hard rules (16 rows)  = 95 lines
```

```text
What this is (5) · Stack (9) · Commands (9) · Done means (12) · Hard rules (12 rows)
Layout (8) · Detail by topic (9 one-line pointers)                          = 87 lines
```

### Pointers, not copies

Never paste code or schemas into the map. Point at `file:line`, at the test that enforces a rule, at the topic file. Copies drift the day after they are made; pointers are checked by the link checker and by the agent that follows them.

### Move, never delete

When a file gets split, every line of the old file must still exist somewhere. The receiving topic file starts with its original heading and one line saying when it moved. Verify the move mechanically:

```sh
git show HEAD:AGENTS.md | grep -v '^[[:space:]]*$' | sort -u > /tmp/old.txt
cat AGENTS.md docs/agent/*.md | grep -v '^[[:space:]]*$' | sort -u > /tmp/new.txt
comm -23 /tmp/old.txt /tmp/new.txt      # must print only the headings you retitled
```

### Guard against regrowth

A file that was split once will grow back. Add a test that fails when the map exceeds its budget and when a topic file is not indexed:

```text
AGENTS.md has at most 150 lines and 1,500 words
every file in docs/agent/ is linked from AGENTS.md
every docs/agent/ link in AGENTS.md points at a file that exists
```

Ten lines in your test framework of choice; the field version runs in the normal unit test suite. The three numbers agree on purpose: the map's target is under 100 lines, the test tolerates 150 so one added bullet does not break the build, and the audit warns above 100 and fails above 200.

### Freshness is part of the fact

"204 tests as of 2026-09-22" is more useful than "all tests pass", because the next reader can see when it was last true. Mark stale documents as stale in the map ("`docs/README.md` is an old ancestor of this repo: don't trust it") rather than deleting them, and give every workaround its end date ("drop after the next toolchain upgrade").

### Ship instruction edits with the code

An instruction change in the same pull request as the code it describes means every branch and worktree carries instructions that match its own code. An instruction change made later, on `main`, leaves every open branch describing the past.

### What never goes in the map

- Style rules: a formatter or a lint rule does that job without spending attention.
- Secrets, hosts, device identifiers, personal names: a topic file at most, and preferably a secret store.
- Task-specific instructions: those belong in the brief for that task.
- Anything auto-generated: the map is the highest-leverage file in the harness; write every line by hand.

### One file, many tools

`AGENTS.md` is the cross-tool file: Codex, Cursor, GitHub Copilot, Gemini CLI and others read it ([matrix](../tool-support-matrix.md)). Claude Code reads `CLAUDE.md`; make that file one line, `@AGENTS.md`, and the two never drift. Nested instruction files in subfolders apply to work in that folder, which is the right place for a monorepo's per-package rules. Some frameworks' dev servers now append their own block of agent rules to these files; keep the block byte-identical, since the tool re-adds it, and treat it as part of the map's budget.

## Do this today

1. Count the lines and words of your instruction file. Over 100 lines or 1,500 words: split it this week.
2. Add the Hard rules table. Every row names an enforcer or says "prose, no enforcer yet".
3. Add the regrowth test.
4. Date every fact that can go stale.

## Sources

OpenAI, *Harness engineering* (the ~100-line directory); HumanLayer, *Writing a good CLAUDE.md* (instruction limits, pointers over copies); Galster et al. (context files dominate; `AGENTS.md` as the standard); Marmelab (token cost of instructions; keep the main file under ~100 lines); field notes. Links in [references](../references.md).
