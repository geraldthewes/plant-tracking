
**Phase 1 — Analysis**

Review the feedback below: confirm the issue, explain it, critique the feedback, and suggest alternatives if appropriate. Present your findings clearly.

Then assess what testing approach is most appropriate for the fix and propose one of these strategies:

- **Red/Green TDD** — a new failing test drives the implementation (best when the fix requires new behavior to be specified)
- **New test only** — add a test that verifies a correction to existing code (best when the production code is fine but test coverage is missing or weak, as in the example below)
- **No new test** — implement the fix directly without touching tests (best when the change is cosmetic, documentation, or already covered by existing tests)

Pick a strategy


**Phase 2 — Implementation **

Apply the fix using the approved testing strategy:
- **Red/Green TDD**: write a failing test first (red), implement the fix to make it pass (green), confirm the test passes.
- **New test only**: add the test, confirm it passes against the existing implementation.
- **No new test**: implement the fix directly, confirm existing tests still pass.
