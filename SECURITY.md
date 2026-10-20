# Security

## What this repository is

Documentation, templates and small scripts. The scripts run with the permissions of the agent session that invokes them. Review a hook before you install it; the guard in particular decides which commands an agent may run in your repository.

## Reporting a vulnerability

If a template or script here could let an agent do something destructive that the documentation says it prevents, or leaks data (for example the metrics log recording something it should not), please report it privately through GitHub's "Report a vulnerability" on this repository rather than a public issue. You will get an acknowledgement within five working days.

## What the hooks log

The guard and the stop check append one JSON line per decision to `~/.claude/metrics/harness.jsonl` (override with `HARNESS_METRICS_FILE`). The file is created private (mode 0600) and rotates at 5 MB. For an allowed command only the program name and a short hash are written; the command text is written only for ask and deny decisions, after known secret shapes (bearer tokens, `PASSWORD=`-style assignments, URL credentials, common API key formats) are replaced with `[redacted]`. The stop check redacts the last line of a failing check the same way. `HARNESS_LOG_COMMANDS=none` logs decisions only; `full` keeps command text verbatim and belongs only on a machine where that file is as protected as your shell history. Treat the file as an audit log: keep it with your other audit logs and do not commit it.

## What is not a vulnerability

- A command the guard does not recognise: the guard allows what it cannot parse by design (fail open) and says so. Propose a rule through a pattern issue.
- Behaviour of the agent tools themselves (Claude Code, Codex, Cursor, Copilot, Gemini CLI). Report those to their vendors.
