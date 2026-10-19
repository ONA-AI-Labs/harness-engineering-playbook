# 1. Record architecture decisions

Date: <YYYY-MM-DD>

## Status

Accepted

## Context

Agents and people both need to know why things are the way they are, and the reason rarely survives in code.

## Decision

Every decision that constrains future work gets a numbered file in `docs/DECISIONS/`, in this format: context, decision, consequences. Instruction files point at decisions instead of restating them.

## Consequences

An agent that wants to change a constrained thing reads the decision first and proposes a new decision instead of a silent change.
