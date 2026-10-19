# Contract: <FEATURE>

<!-- For a change that crosses repositories. Twenty lines or fewer. Pasted into every repo agent's brief; it is the
     source of truth, and a needed deviation is reported, never made silently. -->

- **Repos:** <api>, <web>, <mobile>
- **Endpoint:** `<METHOD> /v1/<path>` (new | changed; if changed, stays backward compatible for installed clients)
- **Request:** `{ "<field>": <type> }` (casing exactly as written, per endpoint)
- **Response:** `{ "<field>": <type> }`
- **Auth:** <session | API key | both>
- **Errors:** `<status>` when <condition>; clients show `<message>`
- **Tasks:**
  - <api>: <one line>
  - <web>: <one line>
  - <mobile>: <one line>
- **Owner decisions:** <things only the owner may change, e.g. plan limits>
- **Not in scope:** <what each agent must not touch>
