# Security

## What this repository is

Documentation, templates and small scripts. The scripts run with the permissions of the agent session that invokes them. Review a hook before you install it; the guard in particular decides which commands an agent may run in your repository.

## Reporting a vulnerability

If a template or script here could let an agent do something destructive that the documentation says it prevents, or leaks data (for example the metrics log recording something it should not), please report it privately through GitHub's "Report a vulnerability" on this repository rather than a public issue. You will get an acknowledgement within five working days.

## What is not a vulnerability

- A command the guard does not recognise: the guard allows what it cannot parse by design (fail open) and says so. Propose a rule through a pattern issue.
- Behaviour of the agent tools themselves (Claude Code, Codex, Cursor, Copilot, Gemini CLI). Report those to their vendors.
