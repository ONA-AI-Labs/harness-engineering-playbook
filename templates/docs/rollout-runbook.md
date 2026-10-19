# Rollout runbook: <CHANGE>

Every step marked **GO** needs a person's go-ahead at that moment. An earlier yes does not carry over.

## Before

- [ ] `main` is green; the deploy run of the previous change finished.
- [ ] Dry checks: <the query or command that shows what the change will touch, with the expected count>.
- [ ] Rollback is written below and the person running this has read it.

## Steps

1. **GO** <step one, e.g. apply migration `<file>` with `BEGIN; ...; ROLLBACK` first and show the output>.
2. **GO** <step two, e.g. deploy and watch the deploy run to the end, not just CI>.
3. **GO** <step three, e.g. flip one flag with the queues idle; verify one real item and the log lines `<...>`>.

## After

- [ ] <the metric or log that proves it works>, checked at <time>.
- [ ] `docs/PROGRESS.md` and the memory updated.

## Rollback

- <exact commands, in order; what data they cannot restore>
