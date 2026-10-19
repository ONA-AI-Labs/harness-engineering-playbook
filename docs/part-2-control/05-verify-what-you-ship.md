# 5. Verify what you ship

**Why do agents declare victory early?**

Because the check they ran passed, and the check did not test what ships. "Done" meant "my tests are green", and nobody had written down what done means.

## The short answer

Define done as a list the agent cannot shorten: a quick check, a full check that boots the built artifact, the things a person must look at, and the rule that whatever was not verified is said out loud.

## How it fails without this

Each of these happened to a team running agents across a service, a web app and two mobile apps:

- Unit tests ran the TypeScript sources; the bundled output could not load a dependency, and production went down. The tests were green.
- CI was green; the deploy failed, because the deploy built from a filtered directory that CI never saw.
- A failing run's last thirty lines listed passing tests, and the agent read the tail as success. The exit code was 1.
- A test suite failed to load on an older runtime and sat broken and unnoticed, because the failure looked like a configuration issue nobody owned.
- A component rendered in a browser harness and never appeared in the packaged app, because a runtime permission was missing.
- Only the free-account click path crashed, while type checks, unit tests and a privileged smoke test all passed.

## The pattern

### Done means

The [definition of done](../../templates/docs/definition-of-done.md) is seven lines. The agent runs the quick check and the full check, has a test that would fail without the change, keeps the hard rules, lists what a person must check by hand, updates the progress file, and says what was not verified. The map carries the same list under "Done means" so it is read at every session start.

### Layered checks, cheapest first

| Layer | Catches | Who runs it |
|---|---|---|
| quick check: lint and types, under 90 s | the obvious | the agent, from the Stop hook |
| tests for the touched code | logic | the agent, during the work |
| full suite, build | regressions, build config | the agent before done; CI |
| boot check on the built artifact | what tests cannot see: bundling, native modules, missing assets | `scripts/check.sh`; CI |
| image build when dependencies change | what the CI runner has and the image lacks | CI, path-filtered |
| end-to-end in a browser, as a person would | stubs, broken flows, untrue claims | the agent when asked; CI on dispatch |
| deploy that waits for every replica to be healthy | a service that starts and then dies | the deploy pipeline |

### Boot what you ship

The [boot check](../../templates/scripts/boot-check.sh) starts the built artifact with placeholder credentials, waits for a health signal, and stops it. Thirty lines of shell, and it catches the class of failure that unit tests structurally cannot: the bundle that does not load. Run it after any new runtime dependency, and in CI on every pull request.

### Read the exit code, not the tail

A test runner's last lines are the last tests, and the last tests usually pass. Capture the exit code and grep the failure count:

```sh
npm test > /tmp/test.log 2>&1; echo "exit=$?"; grep -cE 'failed|FAIL' /tmp/test.log
```

Put the rule in the map and in every agent brief. It is the single most common way an agent is honestly wrong about "done".

### Write each trap next to the check that misses it

Where the map says "run the tests", say in the same breath what the tests miss and which extra step covers it: "vitest runs the sources, never the bundle, so green tests do not prove the server boots: after a new dependency, build and run the boot check". A trap in a separate document is a trap nobody reads at the right moment.

### Let the agent run the app

Anthropic's long-running agent needed to be told to use browser automation and test as a human user would; curl against an API does not find a button that does nothing. Give the agent a way to start the app and a browser it can drive, and put "open the screen you changed" in the definition of done. Then ask for one thing more: open gated features as a non-privileged account, because the privileged path is the one every smoke test takes.

### Leftover verification hacks

A temporary stub that made a flow testable is a bug if it ships. Mark every such hack with one token (`TEMP-VERIFY`) and make its absence a check: the [clean-state check](../../templates/scripts/clean-state-check.sh) greps for it, and a five-line test in the suite fails on it.

### Pin the runtime

A suite that needs a newer runtime than the shell's default fails with a message that looks like a flag error. Pin the version in CI and say in the map which version the suite needs and how to select it locally.

### "Not verified" is mandatory

The last section of every report and pull request lists what was not run or seen: a device, a browser, production data, a slow suite. A report without that section is incomplete. The habit does more for trust than any amount of passing output, because it tells the reviewer where to look.

## Do this today

1. Copy the [definition of done](../../templates/docs/definition-of-done.md) and fill in the by-hand line.
2. Add the [boot check](../../templates/scripts/boot-check.sh) to `scripts/check.sh` and to CI.
3. Add "read the exit code, not the tail" to the map, and the trap your tests miss next to the test command.
4. Add the "Not verified" section to your pull request template.

## Sources

Anthropic, *Effective harnesses for long-running agents* (browser testing as a human would; premature completion); field notes (bundle boot, image build, exit codes, runtime pin, gated controls). Links in [references](../references.md).
