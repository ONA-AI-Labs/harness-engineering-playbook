# Architecture

<!-- One screen. Where a request goes, where data lives, what runs in the background. Pointers, not prose. -->

## Request path

`<entry>` → `<auth>` → `<validation>` → `<handler>` → `<service>` → `<store>`

## Data

- `<database>`: migrations in `<folder>`; applied by a person, never by an agent.
- `<cache / queue>`: <one line>

## Background work

- `<worker or job>`: <what it does, what triggers it>

## Boundaries that tests enforce

- `<rule>`: `<test file>`
