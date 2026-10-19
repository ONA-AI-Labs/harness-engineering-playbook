# Changelog

All notable changes to this playbook. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-10-19

### Added

- Fourteen chapters in five parts, from what a harness is to an enterprise rollout plan.
- Field lessons: product-free rules distilled from running coding agents across an API, a web app with a desktop shell, an admin panel, a marketing site and two mobile apps.
- Templates: an 8-file starter kit, instruction maps, scripts (quick check, full check, boot check, ratchet, architecture check, feature verification, clean-state check, init), Claude Code and Codex hooks (destructive-command guard, touched-files tracker, stop-time check, session context), per-repo agent and contract reviewer definitions, memory files, an eval runner with a judge rubric and schema, a CI gates workflow, a pull request template.
- `tools/audit-harness.py`: scores a repository on the maturity model (levels 0 to 4) by checking enforcement, not file presence.
- A Claude Code and Codex skill that audits a repo and installs the missing pieces.
- Tool support matrix for Claude Code, Codex, Cursor, GitHub Copilot and Gemini CLI.
