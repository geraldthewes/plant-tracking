<!-- review-action-run: 2026-08-09 14:33:55 UTC -->
# Review Action Summary

Run started:  2026-08-09 14:33:55 UTC
Coding agent: opencode (opus)

Restored:   0
Processed:  31
Committed:  11
Skipped:    20
Errors:     0
Total cost: $0.0000 across 0 agent call(s)
Interrupted: no
Progress: 31 out of 31 findings processed

## Findings

| Finding | File | Outcome | Commit | What was done |
|---------|------|---------|--------|---------------|
| [01205db9-29](./01205db9-29.md) | packages/plant_service/tests/unit/test_plant_model.py | Fixed | `bfe742df` | Fix applied and committed: fix: Duplication: test_death_reasons_list hardcodes the... [01205db9-29] |
| [01205db9-30](./01205db9-30.md) | packages/plant_service/tests/unit/test_plant_model.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [0ccd4f32-27](./0ccd4f32-27.md) | packages/plant_service/tests/integration/test_repository.py | Fixed | `6fab01ff` | Fix applied and committed: fix: Heavy code duplication: the setup for creating an ... [0ccd4f32-27] |
| [0ccd4f32-28](./0ccd4f32-28.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [401b3a5f-10](./401b3a5f-10.md) | backend/fastapi/tests/test_plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [401b3a5f-11](./401b3a5f-11.md) | backend/fastapi/tests/test_plants.py | Fixed | `58571601` | Fix applied and committed: fix: In test_mark_plant_dead, death_comment is passed b... [401b3a5f-11] |
| [401b3a5f-9](./401b3a5f-9.md) | backend/fastapi/tests/test_plants.py | Fixed | `633211df` | Fix applied and committed: fix: Manual construction of query strings in PATCH requ... [401b3a5f-9] |
| [79c21f84-14](./79c21f84-14.md) | frontend/src/api/plantTrackingAPI.ts | Fixed | `ff03d1cb` | Fix applied and committed: fix: Uses loose equality '==' in validation (prohibited... [79c21f84-14] |
| [79c21f84-15](./79c21f84-15.md) | frontend/src/api/plantTrackingAPI.ts | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [79c21f84-16](./79c21f84-16.md) | frontend/src/api/plantTrackingAPI.ts | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [79c21f84-17](./79c21f84-17.md) | frontend/src/api/plantTrackingAPI.ts | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [82911b41-0](./82911b41-0.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [82911b41-1](./82911b41-1.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [82911b41-2](./82911b41-2.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [82911b41-3](./82911b41-3.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Fixed | `67db6805` | Fix applied and committed: fix: Docstrings for endpoints are minimal (one-liners).... [82911b41-3] |
| [cbea0de4-20](./cbea0de4-20.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Fixed | `90193b6c` | Fix applied and committed: fix: The alive_only and dead_only parameters are not mu... [cbea0de4-20] |
| [cf9314f8-18](./cf9314f8-18.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-19](./cf9314f8-19.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-21](./cf9314f8-21.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-22](./cf9314f8-22.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [d30f3ff2-23](./d30f3ff2-23.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `bd29339f` | Fix applied and committed: fix: Validation logic for death_date, death_reason, and... [d30f3ff2-23] |
| [d30f3ff2-24](./d30f3ff2-24.md) | packages/plant_service/src/plant_service/domain/plant.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [d30f3ff2-25](./d30f3ff2-25.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `d78b304f` | Fix applied and committed: fix: validate_death_fields hardcodes 'Plant.DEATH_REASO... [d30f3ff2-25] |
| [d30f3ff2-26](./d30f3ff2-26.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `e58ab027` | Fix applied and committed: fix: Death fields use bare 'str = ""' as sentinel for a... [d30f3ff2-26] |
| [e76ef807-12](./e76ef807-12.md) | backend/fastapi/tests/conftest.py | Skipped | — | Already applied — suggested symbols already present in file (`list_plants`) |
| [e76ef807-13](./e76ef807-13.md) | backend/fastapi/tests/conftest.py | Fixed | `8e93fb66` | Fix applied and committed: fix: Function 'test_get_uow_mock' has 'test_' prefix (p... [e76ef807-13] |
| [e76ef807-4](./e76ef807-4.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-5](./e76ef807-5.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-6](./e76ef807-6.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-7](./e76ef807-7.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-8](./e76ef807-8.md) | backend/fastapi/tests/conftest.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
