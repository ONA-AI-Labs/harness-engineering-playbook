# Definition of done

A change is done when every line below is true. "Done" without this list is not done.

1. `scripts/quick-check.sh` ends `quick-check: OK`.
2. `scripts/check.sh` ends `check: OK` (tests, build, and the built artifact boots).
3. The change has a test that would fail without it, or the pull request says why none is possible.
4. Hard rules in `AGENTS.md` still hold; a new rule names its enforcer or says "prose, no enforcer yet".
5. By hand: <what a person must look at or click, e.g. the screen you changed at phone and desktop width, light and dark>.
6. `docs/PROGRESS.md` is updated: current state, done, next.
7. The pull request lists what was **not** verified.
