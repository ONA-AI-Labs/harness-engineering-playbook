# 8. Memory and lessons

**How does the harness learn?**

One lesson at a time, written down the moment it is learned, in a form that says what to do, why, and when it stops applying. Then the lesson becomes a guard, so the harness remembers even when the model does not.

## The short answer

Keep a memory folder: one small file per lesson with a rule, the incident behind it, how to apply it, its scope and its expiry; an index file of one line per lesson that loads every session; and a workflow that turns a repeated correction into a rule, the rule into a guard, and gives the guard an owner.

## How it fails without this

A correction given in chat is gone with the session. A correction written into the instruction file makes the file longer and the correction no more enforceable. A memory that records a rule without the incident gets over-applied, because nobody can tell its limits. A memory with no expiry outlives the model limitation it worked around and keeps costing attention. Marmelab names the last one harness rot and found that expiry conditions are rarely documented.

## The pattern

### The file

```markdown
---
name: verify-what-ships
description: Green unit tests do not prove the built artifact boots; run the boot check after any new runtime dependency
metadata:
  type: feedback
---

Run the boot check on the built artifact after any new runtime dependency or new direct import.

**Why:** Tests ran the sources while the bundled output failed to load a dependency in production (2026-09).

**How to apply:**
- After adding a dependency: build, then `scripts/boot-check.sh`.
- Enforced by `scripts/check.sh` in CI; the quick check does not cover it.

**Scope:** services that ship a bundle or an image.

**Expiry:** when the test suite runs against the built artifact.
```

The description line is the only line most sessions ever read: it must state the rule and when it applies, because that is what decides whether the memory is recalled. The [template](../../templates/memory/_template.md) has the frontmatter.

### Four kinds

- **feedback**: a correction, or a mistake the agent caught, turned into a standing rule. Always rule, incident, how to apply.
- **project**: the state of a piece of work that outlives a session and is not in the code: what shipped where, decisions, open items.
- **reference**: where things are and how to reach them, measured facts about a platform.
- **user**: who the person is and how they like to work.

Classify by how long the rule lasts, not by where it came up. A durable rule learned during a feature is feedback, not a line in the project log where nobody will find it again.

### The index is a table of contents

One line per memory, loaded at every session start. It is a list of hooks, never content: when it grows past a screen, move detail into the files and shorten the lines. A field index that had grown to twenty kilobytes of multi-clause lines was cut back by moving the details into seventy-nine file bodies; recall got better, not worse.

### Hygiene rules that keep memory true

- **Update, do not duplicate.** A fact that changed is corrected in place, with a note ("an earlier version of this said X; that is no longer true"). Two versions of one fact are worse than none.
- **Absolute dates.** "As of 2026-10-19", never "last week".
- **Attribution.** The person's own words are quoted; the agent's inferences are marked as its own.
- **Verification state inside the fact.** "Live and verified", "never run", "untested on the device". A memory that cannot say how it knows is a rumour.
- **Scope.** The last line says where the rule applies and where it does not, so a rule about one platform is not applied to all of them.

### Incident to rule to guard

Hashimoto's definition of harness engineering is a loop: anytime an agent makes a mistake, engineer a solution so it never makes that mistake again. The loop has four steps, and most teams stop after the first:

1. **Incident**: what happened, in one sentence generic enough to publish.
2. **Rule**: one imperative sentence; into the map's Hard rules table and into memory.
3. **Guard**: the hook, lint rule, test or CI step that makes the rule impossible to break; named in the table's second column. Until it exists, the row says "prose, no enforcer yet".
4. **Owner and expiry**: who keeps the guard, and the condition under which it is no longer needed.

The [incident-to-rule template](../../templates/docs/incident-to-rule.md) is one file per incident. Over a year it becomes the most honest architecture document the team has.

### Memory is not a substitute for enforcement

A memory tells the model; a guard tells the tool. The chapters before this one are about guards for a reason. Memory is for everything that cannot be a guard yet: taste, consent rules, which account the person means, what is parked and must not be touched.

## Do this today

1. Create `memory/` with the [index](../../templates/memory/MEMORY.md) and the [template](../../templates/memory/_template.md); have the agent load the index at session start (Claude Code reads a memory folder per project automatically; other tools get a line in the map).
2. Take the last three corrections you gave an agent. Write each as a memory with an expiry.
3. Pick the one that can be a guard. Make it one, and move its row in the Hard rules table from prose to enforced.

## Sources

Hashimoto (*My AI Adoption Journey*); Marmelab (harness rot, the incident and expiry behind each control); field notes (the memory format, the index compaction, the hygiene rules). Links in [references](../references.md).
