<!-- review-action-run: 2026-08-09 16:10:20 UTC -->
# Review Action Summary

Run started:  2026-08-09 16:10:20 UTC
Coding agent: opencode (opus)

Restored:   0
Processed:  36
Committed:  14
Skipped:    22
Errors:     0
Total cost: $0.0000 across 0 agent call(s)
Interrupted: no
Progress: 36 out of 36 findings processed

## Findings

| Finding | File | Outcome | Commit | What was done |
|---------|------|---------|--------|---------------|
| [01205db9-28](./01205db9-28.md) | packages/plant_service/tests/unit/test_plant_model.py | Fixed | `6bd563be` | Fix applied and committed: fix: Significant duplication between tests using direct... [01205db9-28] |
| [01205db9-29](./01205db9-29.md) | packages/plant_service/tests/unit/test_plant_model.py | Fixed | `a0c51955` | Fix applied and committed: fix: Repeated boilerplate in create_from_dict calls acr... [01205db9-29] |
| [01205db9-30](./01205db9-30.md) | packages/plant_service/tests/unit/test_plant_model.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [01205db9-31](./01205db9-31.md) | packages/plant_service/tests/unit/test_plant_model.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [01205db9-32](./01205db9-32.md) | packages/plant_service/tests/unit/test_plant_model.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [0ccd4f32-33](./0ccd4f32-33.md) | packages/plant_service/tests/integration/test_repository.py | Fixed | `fa1ed393` | Fix applied and committed: fix: The new filter tests only cover happy-path mutuall... [0ccd4f32-33] |
| [0ccd4f32-34](./0ccd4f32-34.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [0ccd4f32-35](./0ccd4f32-35.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [401b3a5f-0](./401b3a5f-0.md) | backend/fastapi/tests/test_plants.py | Fixed | `52b620a4` | Fix applied and committed: fix: Multiple test functions contain duplicated code fo... [401b3a5f-0] |
| [401b3a5f-1](./401b3a5f-1.md) | backend/fastapi/tests/test_plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [401b3a5f-2](./401b3a5f-2.md) | backend/fastapi/tests/test_plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [401b3a5f-3](./401b3a5f-3.md) | backend/fastapi/tests/test_plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [79c21f84-22](./79c21f84-22.md) | frontend/src/api/plantTrackingAPI.ts | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [79c21f84-23](./79c21f84-23.md) | frontend/src/api/plantTrackingAPI.ts | Fixed | `a9be9ac0` | Fix applied and committed: fix: In markPlantDeadApiPlantsPlantIdDeadPatch, the cli... [79c21f84-23] |
| [79c21f84-24](./79c21f84-24.md) | frontend/src/api/plantTrackingAPI.ts | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [82911b41-4](./82911b41-4.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Fixed | `301266e1` | Fix applied and committed: fix: In list_plants, the implementation does not valida... [82911b41-4] |
| [82911b41-5](./82911b41-5.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Fixed | `2254e046` | Fix applied and committed: fix: The three new public route handlers (list_plants, ... [82911b41-5] |
| [82911b41-6](./82911b41-6.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [82911b41-7](./82911b41-7.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Skipped | — | Already applied — file already reflects the suggested code |
| [cbea0de4-19](./cbea0de4-19.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Fixed | `4c763ea6` | Fix applied and committed: fix: The 'or None' expressions are redundant for the de... [cbea0de4-19] |
| [cbea0de4-20](./cbea0de4-20.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Fixed | `11276b74` | Fix applied and committed: fix: The updated docstring for this public method (part... [cbea0de4-20] |
| [cbea0de4-21](./cbea0de4-21.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [cf9314f8-12](./cf9314f8-12.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-13](./cf9314f8-13.md) | commands/plant_tracking_cli.py | Fixed | `a98e4679` | Fix applied and committed: fix: Interactive input() loops (for death_date, reason,... [cf9314f8-13] |
| [cf9314f8-14](./cf9314f8-14.md) | commands/plant_tracking_cli.py | Fixed | `40ba0a3b` | Fix applied and committed: fix: In list_plants, post-fetch filter uses 'if alive_o... [cf9314f8-14] |
| [cf9314f8-15](./cf9314f8-15.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-16](./cf9314f8-16.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-17](./cf9314f8-17.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-18](./cf9314f8-18.md) | commands/plant_tracking_cli.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [d30f3ff2-25](./d30f3ff2-25.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `56b2bfab` | Fix applied and committed: fix: Edge case validation is insufficient in validate_d... [d30f3ff2-25] |
| [d30f3ff2-26](./d30f3ff2-26.md) | packages/plant_service/src/plant_service/domain/plant.py | Skipped | — | Already applied — file already reflects the suggested code |
| [d30f3ff2-27](./d30f3ff2-27.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `9447c87a` | Fix applied and committed: fix: validate_death_fields docstring is one-line and in... [d30f3ff2-27] |
| [e76ef807-10](./e76ef807-10.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-11](./e76ef807-11.md) | backend/fastapi/tests/conftest.py | Fixed | `b0fc2752` | Fix applied and committed: fix: Using return_value with a one-time iterator for li... [e76ef807-11] |
| [e76ef807-8](./e76ef807-8.md) | backend/fastapi/tests/conftest.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [e76ef807-9](./e76ef807-9.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
