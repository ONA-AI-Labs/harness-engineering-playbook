---
name: verify-what-ships
description: Green unit tests do not prove the built artifact boots; run the boot check after any new runtime dependency, before claiming done
metadata:
  type: feedback
---

Run the boot check on the built artifact after any new runtime dependency or new direct import.

**Why:** Tests ran the sources while the bundled output failed to load a dependency in production (2026-09).

**How to apply:**

- After adding a dependency: build, then `scripts/boot-check.sh`.
- Enforced by `scripts/check.sh` in CI; the quick check does not cover it.

**Scope:** services that ship a bundle or an image. Libraries without a runtime declare the check not applicable.

**Expiry:** when the test suite runs against the built artifact.
