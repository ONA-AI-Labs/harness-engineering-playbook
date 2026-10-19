# quick: seconds, runs from the Stop hook. check: everything CI runs.
SHELL := /usr/bin/env bash

.PHONY: quick check lint links shellcheck test json audit

quick: lint shellcheck json

check: quick links test audit

lint:
	@markdownlint-cli2 "**/*.md" "#node_modules"

links:
	@lychee --offline --no-progress --root-dir "$(CURDIR)" "**/*.md"

shellcheck:
	@shellcheck -x $$(git ls-files '*.sh' 'templates/**/*.sh' 'scripts/*.sh' | sort -u)

test:
	@bats tools/tests/

json:
	@for f in $$(git ls-files '*.json'); do python3 -m json.tool "$$f" >/dev/null || { echo "invalid JSON: $$f"; exit 1; }; done; echo "json ok"

audit:
	@python3 tools/audit-harness.py . --min-level 2
