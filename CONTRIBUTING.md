# Contributing

Thanks for helping. This playbook is maintained by a small team that uses it every day; contributions that fit the rules below get merged quickly.

## What belongs here

- A **pattern** that prevents a named failure, with the enforcement that backs it (a hook, a script, a lint rule, a test, a CI gate). Prose-only rules are welcome when they say "prose, no enforcer yet".
- A **template** people can copy into a repo and use the same day.
- A **lesson** in the Rule → Why → How to apply form, with a generic incident. No company internals.
- A **correction** to a fact, with a source.

## Rules every change follows

1. **Sources.** Every number or claim about a tool, paper or company links to its source in the same section. Observed tool behaviours carry "observed on <tool> <version>, <month>".
2. **Nothing private.** No product names, hosts, people, emails, prices, credentials or customer details, yours or anyone else's. Generic stack words only ("the API", "the web app", "the mobile app").
3. **Plain English.** Short sentences. Headings as questions or verbs. One idea per paragraph. Code, commands and file trees go in fences.
4. **Enforcement over prose.** If a rule can be a script or a test, ship the script or the test. The repo follows its own advice: `make quick` runs from the Stop hook, `make check` is the definition of done.
5. **Templates are tested.** A script template gets a bats test in `tools/tests/`; a JSON template must parse; placeholders look like `<THIS>`.
6. **Expiry.** A pattern that exists because a model or tool cannot do something yet says so, with the condition that retires it.

## Working on the repo

```sh
brew install bats-core shellcheck lychee      # macOS; CI installs its own
npm i -g markdownlint-cli2
make quick     # markdownlint, shellcheck, JSON parse: seconds
make check     # quick + offline link check + bats + the repo's own audit
```

Open a pull request with the template filled in, including the "Not verified" section. CODEOWNERS routes harness files (`AGENTS.md`, `.claude/`, `templates/hooks/`, `tools/`) to a maintainer.

## Licence

By contributing you agree that your contribution is licensed under the MIT licence of this repository.
