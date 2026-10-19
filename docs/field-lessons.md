# Field lessons

Rules learned while running coding agents across one product: an API, a web app with a desktop shell, an admin panel, a marketing site and two mobile apps, over about three months. Each rule carries the generic failure behind it and how to apply it. Where a guard exists, it is named; where one does not, the rule is prose and says so. Nothing here identifies the product, its people or its hosts.

Use them as a checklist, as material for your own memory files, and as the seed of your Hard rules tables.

## Verification before claiming done

**Green unit tests do not prove the built artifact boots.** The tests ran the sources while the bundled output could not load a dependency in production. Add a boot check on the built artifact and run it before merging any new runtime dependency. Guard: [`boot-check.sh`](../templates/scripts/boot-check.sh) in the full check and in CI.

**Green pull-request checks do not prove the deploy builds.** The deploy built from a filtered directory that CI never saw; the image was missing a native extension for weeks. Build the real image in CI when dependencies or the build change, and watch the deploy run to its end. Guard: a path-filtered image-build job; a deploy script that waits for every replica to be healthy.

**Read the exit code, not the tail.** A failing run's last lines listed passing tests and read like success. `cmd > log; echo $?`, then grep the failure count. Prose rule; put it in every brief.

**Let the test runner own the build.** Building by hand just before an end-to-end suite mixed two builds' asset hashes into dozens of fake failures. Re-run failing specs on their own before blaming the change.

**Changes to chrome shown on every page need the full suite.** A navigation change broke an unrelated page's spec for a day.

**Merge only after CI reports completed and successful for the head commit.** Watch commands return at once when checks have not registered yet; another session can merge while your run is in flight, so re-check mergeability before merging.

**Open every gated control as a non-privileged account before shipping.** Only the free-account click path crashed; type checks, unit tests and a privileged smoke test all passed. Prose; put it in the definition of done.

**Run the real packaged app before cutting a release.** A component that rendered in a browser harness never appeared in the app: a runtime permission was missing. Release checklists end with "unverified on real hardware" lists, and those lists are read.

**Server tests cannot see browser rules.** A new request header passed every API test, then the browser's cross-origin policy blocked it. One real-browser pass for any new header or origin.

**Before treating an eval drop as a regression, compare against the baseline on the same day and data.** Judges drift and inputs change; the comparison, not the number, is the evidence.

**Say exactly what was not verified.** "Untested on the device", "not seen in dark mode", "no run on the older OS". A report without this list is incomplete. Prose, enforced socially: the pull request template has the section.

**A temporary verification hack ships unless its absence is checked.** Mark every hack with one token and fail on it. Guard: [`clean-state-check.sh`](../templates/scripts/clean-state-check.sh) and a five-line test.

**Pin the runtime the suite needs.** A suite failed to load on the shell's default runtime with a message that looked like a flag error, and sat broken for weeks. CI pins the version; the map says how to select it locally.

## Environment and deployment truth

**Check the data before the code.** Three fixes shipped for a bug that was data filed under another account. Order of inquiry: does the data exist and whose is it; is the deployed container on the merged commit; do production environment and credentials match local.

**Production configuration drifts from the repository.** A credential could list integrations but not run them. Inspect the production environment (values masked) before theorising about code.

**Find out which account the person means.** Never assume it is the git identity.

**Dry-run a scheduled or recovery job's first selection before enabling it in production.** Its first pass reprocessed every stuck item ever recorded, and the spend could not be undone. Require a look-back bound and show the count.

**Irreversible operations need a go-ahead at the moment you run them.** Dry run, show the numbers, ask. Approving the design is not approving the purge.

**Debug constraint errors inside a rolled-back transaction.** `BEGIN; ...; ROLLBACK` shows the real error and changes nothing.

**Tell infrastructure failures from code failures.** A CI job that fails in seconds with no steps is a billing problem; a job cancelled after a long queue is a runner outage; a flaky remote fetch needs a rerun. Read the annotations; status pages lag reality.

**Read every public claim from the live source of truth before writing copy.** Never advertise a feature production has no credentials for. Guard: an end-to-end spec that fails on claims the product does not meet.

**Never hardcode identities that rotate.** Signing-certificate hashes, device identifiers: look them up when you use them.

**Caches keyed by URL keep serving old assets.** Put a content hash in the file name of every changed image or icon.

**Check free disk space before heavy runs.** A starved run fails, writes traces, and fills the disk further.

**Keep development and test runs off production's capped shared services.** A connection-limited cache shared between test and production throttled production.

**Keep production names stable across a rename.** Image, compose project and container names stay what the server knows until the server is migrated; the map says so.

## Working with the person

**Never change a dimension the person did not ask about.** A tap-target fix made shared chrome taller and they noticed at once. Enlarge hit areas without moving anything; measure shared chrome against the previous build.

**No "while I'm here" changes.** Offer them.

**When the person asks for a behaviour the platform provides, they mean the platform's own behaviour.** A scripted imitation was rejected on sight. Turn on the native feature; if it does not exist, say so once and offer the native alternative. "Fix it" after that is not permission to emulate.

**Take the person's words literally.** A one-word instruction was misread as a typo. Check the current state first; for ambiguous wording, ask with three or four concrete options.

**When the person names a format, deliver that format first.** A detour backed by evidence read as ignoring the ask.

**Respect parked and settled decisions.** Known-parked issues are not bugs to fix on sight; switched-off features stay off; do not re-ask settled choices.

**Scope removal requests.** Hiding a feature in one client is not deleting its data; destructive follow-ups need their own confirmation.

**The person's running apps and dev servers are theirs.** Ask before restarting or quitting them; do not take focus or screenshots while they work.

## Debugging discipline

**After one failed guess at a bug you cannot reproduce, stop guessing.** Three stacked fixes each caused a new symptom. Remove the dependency so the behaviour can be tested locally, or get one observation from the device; label the fix as unverified.

**Find what changes the state by instrumenting the code that changes it.** Wrap the setter, log stack traces, instead of hunting through code.

**Never notify shared state from teardown hooks.** It froze rendering, but only in release builds. Reset state in the event handler; add a test that navigates away from every screen.

**Map a minified production stack trace** by fetching the live bundle and reading the text around the line and column.

**Know the baseline.** Do not dismiss an oddity in one browser engine as pre-existing, and do not mistake old lint errors or timezone-dependent test failures for regressions.

**Trust the bytes you observe over vendor documentation.** The documented file format turned out to be a different one.

**Never delete the source until the copy is verified complete.** An "end" marker meant the end of one window, not of the file; source files were lost.

**For a visual bug on one platform only, get the OS or engine version first.** An embedded web view differs between OS releases.

## Instruction files and knowledge

**One instruction file grew sixteen-fold in ten weeks** because every feature appended to it, until each agent start cost about 66,000 tokens. Split it into a map and topic files; add a test that fails above a line and word budget. Guard: the regrowth test in [chapter 2](part-1-foundations/02-instruction-files.md).

**Write each "passes but broken" trap next to the check that misses it.** Tests versus a bundle that will not boot; CI versus the image build; a run's tail versus its exit code; failures that only happen in release builds.

**Mark freshness.** "Stale, don't trust", "N tests as of a date", "not verified live", and an end date on every workaround.

**Ship instruction edits in the same pull request as the code they describe.** Every branch then carries instructions that match its own code.

**Name the enforcer next to the rule.** A rule with a named lint rule, test or hook is trusted; one without says "prose, no enforcer yet" and goes on the list.

**Ratchet, do not demand zero.** Gating on zero errors in a repository with debt gets the gate switched off within a day. Guard: [`ratchet.sh`](../templates/scripts/ratchet.sh) at today's count; an unexpected checker exit is a failure, never zero findings.

**Documentation drifts from CI.** A contributing guide claimed the end-to-end suite ran on every push when it ran on manual dispatch. The map carries CI cost decisions with their reversal conditions.

## Tooling and dependencies

**Never install into a worktree whose dependency folder is a symlink.** The package manager follows the link and wipes the target. Check with `ls -ld` first; give each worktree real dependencies.

**Format only the files you touched, at the project's real line width.** A formatter with no width configured re-wrapped the whole tree. Set the width in the project's config so the tool and the people agree.

**The shell does not always split unquoted variables.** A wait loop never matched and ran to its timeout under one shell. Compare one printed field, or the whole string, and quote paths that may contain spaces.

**Removing a tracked file stages the removal at once.** A later partial commit swept the deletions in. Check the status before a partial commit; stage explicit paths.

**Kill only the process listening on a port**, not everything connected to it; that list included the browser.

**Record the runtime versions a repository needs.** The shell's default was older than the tests needed.

## Delegation and cost

**Stacked agent contexts cost more than the work.** One sample turn: about a million cached re-read tokens against about twenty-four thousand output. Delegate once, to the agent that does the work; never triage through a chain.

**Never "just in case" agents.** Dispatch only the agents the task touches.

**Read or dispatch, never both.** Reading a repository yourself before dispatching its agent pays twice.

**Resume the same agent to answer its question.** A fresh one re-reads everything.

**Rate limits are normal under big fan-outs.** Four or five parallel agents reading large inputs died together. Resume them in small batches instead of relaunching; spawn three or four at a time.

**Use a cheaper model for boilerplate-heavy fan-outs**; keep the frontier model for the main session.

**Background agents can stall silently.** One sat idle for over an hour while listed as running. A watcher that exits after fifteen minutes with no file changes, then a nudge.

**Check "I built X" against git.** Parallel builders re-implemented shared components that already existed; tell builders to grep before building.

**Check installed skills and plugins before building any deliverable by hand**, then follow the skill's own gates.

**Other sessions use the same shared checkouts.** Check branch and status before any pull, switch or write; build into a scratch folder and publish from a fresh worktree; remove it afterwards. Agents sharing a worktree stage by explicit path; nobody runs a bare stash.

**A permission denial closes that route.** Say so up front; do not look for another way round; redesign if needed (a test suite that holds no admin credentials).

**Test builds can inherit the real person's session** when the credential-store entry has a fixed name. Isolate test copies before running them.

**Keep shared blocks identical across per-repository agent definitions**; verify with a hash.

**A workspace accumulated dozens of one-off allows**, including unrestricted database and remote-shell access. Audit allow lists; name only the checks; let the guard ask for the rest.

## Memory and process hygiene

**Write the incident into the Why**: what was done, what broke, the person's words, an absolute date. Tag your own inferences as yours.

**Turn corrections into guards**: a spec that asserts fixed sizes, a scan of build output for forbidden strings, an import-boundary test, a lint rule that forces one helper.

**Give each rule a scope** so it is not over-applied.

**Keep the index a list of hooks**; move details into the bodies when it grows.

**Correct in place and mark the status in the description**; never leave two versions of one fact.

**Hooks inject at session start and at subagent start**, because session-start context never reaches subagents; every hook fails open with a short timeout and emits one output field.

**A text-based guard judges heredoc bodies as commands** unless told otherwise: documentation that mentions a dangerous command got blocked while being written. Strip heredoc bodies before judging. Guard: fixed in [`guard-destructive.py`](../templates/hooks/scripts/guard-destructive.py), with a test.

**A guard that cannot see shell variables asks about paths it could resolve.** Three false positives on scratch-folder cleanups in the first hour; the metrics log showed them. Resolve assignments made in the same command; ask only on unknown variables.
