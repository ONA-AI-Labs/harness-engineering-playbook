# Starter kit

Eleven files that take a repository from nothing to level 2 of the harness maturity model in one sitting. They live in [`templates/starter/`](starter/).

```sh
cp -Rn path/to/harness-engineering-playbook/templates/starter/. your-repo/   # -n: never overwrite a file you already have
```

If a file already existed (an `AGENTS.md`, a `.claude/settings.json`), merge by hand: keep every rule and allow-list entry you had.

Then, in `your-repo/`:

1. Fill `AGENTS.md`: what the system is in the first ten lines, the real commands, the hard rules you already have.
2. Fill the two commands at the top of `scripts/quick-check.sh` and the two at the top of `scripts/check.sh`; run them until they end `quick-check: OK` and `check: OK`.
3. Replace `<TEST_COMMAND>` and `<BUILD_COMMAND>` in `.claude/settings.json`.
4. Start a new Claude Code session (hooks load at start). The guard now asks before destructive commands, the quick check runs before the agent stops, and the session opens with the branch and the progress file. Codex: copy `templates/hooks/codex/hooks.json` to `.codex/hooks.json` and the four scripts from `.claude/hooks/` to `.codex/hooks/`.
5. Run the audit: `python3 path/to/harness-engineering-playbook/tools/audit-harness.py .` and expect level 2.

The remaining templates (memory, evals, ratchet, architecture check, CI gates, owners) take you to levels 3 and 4; the audit tells you which are missing.
