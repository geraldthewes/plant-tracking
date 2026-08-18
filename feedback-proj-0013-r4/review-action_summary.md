<!-- review-action-run: 2026-08-14 01:36:57 UTC -->
# Review Action Summary

Run started:  2026-08-14 01:36:57 UTC
Coding agent: opencode (opus)

Restored:   0
Processed:  22
Committed:  17
Skipped:    4
Errors:     1
Not actioned (non-VALID): 16
Total cost: $0.0000 across 0 agent call(s)
Interrupted: no
Progress: 22 out of 22 findings processed

## Findings

| Finding | File | Outcome | Commit | What was done |
|---------|------|---------|--------|---------------|
| [01205db9-34](./01205db9-34.md) | packages/plant_service/tests/unit/test_plant_model.py | Fixed | `1dccbb89` | Fix applied and committed: fix: Missing test coverage for providing death_reason (... [01205db9-34] |
| [01205db9-35](./01205db9-35.md) | packages/plant_service/tests/unit/test_plant_model.py | Fixed | `61af32d4` | Fix applied and committed: fix: Several tests use bare `pytest.raises(ValueError)`... [01205db9-35] |
| [01205db9-36](./01205db9-36.md) | packages/plant_service/tests/unit/test_plant_model.py | Fixed | `221139ac` | Fix applied and committed: fix: No coverage for calendar-invalid but format-matchi... [01205db9-36] |
| [01205db9-37](./01205db9-37.md) | packages/plant_service/tests/unit/test_plant_model.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [0ccd4f32-31](./0ccd4f32-31.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [0ccd4f32-32](./0ccd4f32-32.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [0ccd4f32-33](./0ccd4f32-33.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [1568adac-25](./1568adac-25.md) | packages/plant_service/src/plant_service/service_layer/plant_service.py | Fixed | `41bae14a` | Fix applied and committed: fix: The updated docstring for list_plants is brief and... [1568adac-25] |
| [401b3a5f-10](./401b3a5f-10.md) | backend/fastapi/tests/test_plants.py | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [401b3a5f-5](./401b3a5f-5.md) | backend/fastapi/tests/test_plants.py | Fixed | `4786db6b` | Fix applied and committed: fix: The parametrized test_mark_plant_dead reuses the e... [401b3a5f-5] |
| [79c21f84-16](./79c21f84-16.md) | frontend/src/api/plantTrackingAPI.ts | Fixed | `8eff98dc` | Fix applied and committed: fix: Client-side validation in markPlantDeadApiPlantsPl... [79c21f84-16] |
| [79c21f84-17](./79c21f84-17.md) | frontend/src/api/plantTrackingAPI.ts | Fixed | `2c99a0ef` | Fix applied and committed: fix: listPlantsApiPlantsGetResponse only defines succes... [79c21f84-17] |
| [79c21f84-18](./79c21f84-18.md) | frontend/src/api/plantTrackingAPI.ts | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [82911b41-6](./82911b41-6.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Fixed | `091add59` | Fix applied and committed: fix: mark_plant_dead uses bare function parameters (dea... [82911b41-6] |
| [82911b41-7](./82911b41-7.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Skipped | — | Already addressed — agent completed with no file changes |
| [82911b41-8](./82911b41-8.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [82911b41-9](./82911b41-9.md) | backend/fastapi/src/plant_tracking_api/routes/plants.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-11](./cf9314f8-11.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-12](./cf9314f8-12.md) | commands/plant_tracking_cli.py | Error | — | Quality checks failed after 3 iteration(s): Quality checks failed after 3 iteration(s) for commands/plant_tracking_cli.py: ## Programmatic check failures |
| [cf9314f8-13](./cf9314f8-13.md) | commands/plant_tracking_cli.py | Fixed | `fbd9cda7` | Fix applied and committed: fix: In mark_dead, the initial plant validation try blo... [cf9314f8-13] |
| [cf9314f8-14](./cf9314f8-14.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-15](./cf9314f8-15.md) | commands/plant_tracking_cli.py | Fixed | `5f78d9d3` | Fix applied and committed: fix: _prompt_death_details uses raw input() in loops wi... [cf9314f8-15] |
| [cf9314f8-19](./cf9314f8-19.md) | commands/plant_tracking_cli.py | Skipped | — | Stale finding — target code not found in file (already changed or removed elsewhere) |
| [cf9314f8-20](./cf9314f8-20.md) | commands/plant_tracking_cli.py | Fixed | `8773cf26` | Fix applied and committed: fix: In list_plants display loop, status extraction doe... [cf9314f8-20] |
| [cf9314f8-21](./cf9314f8-21.md) | commands/plant_tracking_cli.py | Fixed | `974ab9cd` | Fix applied and committed: fix: mark_dead uses bare `except Exception as e:` (with... [cf9314f8-21] |
| [cf9314f8-22](./cf9314f8-22.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [cf9314f8-23](./cf9314f8-23.md) | commands/plant_tracking_cli.py | Skipped | — | Already addressed — agent completed with no file changes |
| [cf9314f8-24](./cf9314f8-24.md) | commands/plant_tracking_cli.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [d30f3ff2-26](./d30f3ff2-26.md) | packages/plant_service/src/plant_service/domain/plant.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [d30f3ff2-27](./d30f3ff2-27.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `f4a8512b` | Fix applied and committed: fix: The from_dict/create_from_dict condition triggers ... [d30f3ff2-27] |
| [d30f3ff2-28](./d30f3ff2-28.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `f34eaf27` | Fix applied and committed: fix: validate_death_fields permits death_comment to be ... [d30f3ff2-28] |
| [d30f3ff2-29](./d30f3ff2-29.md) | packages/plant_service/src/plant_service/domain/plant.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [d30f3ff2-30](./d30f3ff2-30.md) | packages/plant_service/src/plant_service/domain/plant.py | Fixed | `e1c80726` | Fix applied and committed: fix: DEATH_REASONS is a public mutable ClassVar[list[st... [d30f3ff2-30] |
| [e76ef807-0](./e76ef807-0.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-1](./e76ef807-1.md) | backend/fastapi/tests/conftest.py | Fixed | `d2d6d049` | Fix applied and committed: fix: plants_client fixture mutates the global app.depen... [e76ef807-1] |
| [e76ef807-2](./e76ef807-2.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [e76ef807-3](./e76ef807-3.md) | backend/fastapi/tests/conftest.py | Fixed | `9983146d` | Fix applied and committed: fix: Imports are not in standard order (stdlib before t... [e76ef807-3] |
| [e76ef807-4](./e76ef807-4.md) | backend/fastapi/tests/conftest.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
