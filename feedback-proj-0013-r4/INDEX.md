# Review Findings Index

## VALID (22)

| # | Severity | File | Lines | Report | Analysis Preview |
|---|----------|------|-------|--------|------------------|
| 1 | `high` | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:108-115` | [82911b41-6.md](82911b41-6.md) | This is a real, concrete defect. In FastAPI, undecorated function parameters that aren't path variables are resolved as … |
| 2 | `high` | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:56-72` | [82911b41-7.md](82911b41-7.md) | CONFIRMED: Critical runtime bug. The `get_uow()` dependency at `backend/fastapi/src/plant_tracking_api/dependencies.py:7… |
| 3 | `high` | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:119-142` | [82911b41-8.md](82911b41-8.md) | The concurrency concern is real and concrete. Three layered issues exist:  1. **Race condition (review finding)**: Lines… |
| 4 | `high` | `backend/fastapi/tests/test_plants.py` | `:70-82` | [401b3a5f-5.md](401b3a5f-5.md) | The review is correct. Tracing the execution: (1) `is_dead` is a computed property returning `bool(self.death_date)` (pl… |
| 5 | `high` | `commands/plant_tracking_cli.py` | `:1809-1813` | [cf9314f8-12.md](cf9314f8-12.md) | Confirmed real bug. Three code paths return different Plant types:  1. Service path (line 1791): Returns `plant_service.… |
| 6 | `high` | `commands/plant_tracking_cli.py` | `:796-812` | [cf9314f8-13.md](cf9314f8-13.md) | The issue is real and verifiable. Phase 1 (lines 796-812) catches only `PlantNotFoundException`, but `PlantNotFoundExcep… |
| 7 | `high` | `commands/plant_tracking_cli.py` | `:1809-1813` | [cf9314f8-19.md](cf9314f8-19.md) | Confirmed bug. Three code paths feed into the filter at lines 1810-1813:  1. **Service path** (SERVICE_AVAILABLE): Plant… |
| 8 | `high` | `commands/plant_tracking_cli.py` | `:1824-1836` | [cf9314f8-20.md](cf9314f8-20.md) | Confirmed real bug. Three compounding defects:  1. **SERVICE_AVAILABLE is a module-level constant** (line 47-49) set at … |
| 9 | `high` | `commands/plant_tracking_cli.py` | `:843-846` | [cf9314f8-21.md](cf9314f8-21.md) | This is a concrete, fixable defect in a single location (commands/plant_tracking_cli.py:843-846). The bare `except Excep… |
| 10 | `high` | `frontend/src/api/plantTrackingAPI.ts` | `:666-675` | [79c21f84-16.md](79c21f84-16.md) | Confirmed: this is a real pattern-breaking defect. The file is Orval-generated (`plantTrackingAPI.ts:2-3`), and the `thr… |
| 11 | `medium` | `backend/fastapi/tests/conftest.py` | `:74-79` | [e76ef807-1.md](e76ef807-1.md) | Confirmed bug: `app.dependency_overrides` is a module-level singleton dict on the shared FastAPI `app` instance. The `pl… |
| 12 | `medium` | `backend/fastapi/tests/conftest.py` | `:1-11` | [e76ef807-3.md](e76ef807-3.md) | Import order violation (PEP 8 stdlib→third-party→local) and missing return type hint on `_mock_uow_with_plants` are conc… |
| 13 | `medium` | `commands/plant_tracking_cli.py` | `:734-743` | [cf9314f8-15.md](cf9314f8-15.md) | This is a concrete, auto-fixable defect in `commands/plant_tracking_cli.py`. Two distinct bugs in `_prompt_death_details… |
| 14 | `medium` | `commands/plant_tracking_cli.py` | `:796-812` | [cf9314f8-23.md](cf9314f8-23.md) | **1. Confirmed real issue**: Phase 1 (lines 796-812) catches only `PlantNotFoundException`, while Phase 3 (lines 821-844… |
| 15 | `medium` | `frontend/src/api/plantTrackingAPI.ts` | `:539-548` | [79c21f84-17.md](79c21f84-17.md) | Confirmed real defect. The backend at `plants.py:50-54` returns HTTP 400 when both `alive_only` and `dead_only` are true… |
| 16 | `medium` | `packages/plant_service/src/plant_service/domain/plant.py` | `:132-138` | [d30f3ff2-27.md](d30f3ff2-27.md) | 1. **Issue confirmed: YES — real bug.** Tracing `create_from_dict` line 133: `any(k in data for k in ...)` fires when `d… |
| 17 | `medium` | `packages/plant_service/src/plant_service/domain/plant.py` | `:168-176` | [d30f3ff2-28.md](d30f3ff2-28.md) | Two distinct concrete defects, both auto-fixable with unit tests.  **Defect 1 — Whitespace-only death_comment slips thro… |
| 18 | `medium` | `packages/plant_service/tests/unit/test_plant_model.py` | `:237-246` | [01205db9-34.md](01205db9-34.md) | Confirmed: the `death_reason is not None and not death_date` branch at plant.py:175-176 raises `ValueError("death_date i… |
| 19 | `medium` | `packages/plant_service/tests/unit/test_plant_model.py` | `:315-345` | [01205db9-35.md](01205db9-35.md) | Confirmed real issue. 6 tests in test_plant_model.py:307-344 use bare `pytest.raises(ValueError)` while 21 other tests a… |
| 20 | `low` | `packages/plant_service/src/plant_service/domain/plant.py` | `:37-48` | [d30f3ff2-30.md](d30f3ff2-30.md) | 1. **Issue confirmed**: `ClassVar[list[str]]` at plant.py:37 is a mutable class-level list. Any module importing `Plant`… |
| 21 | `low` | `packages/plant_service/src/plant_service/service_layer/plant_service.py` | `:21-23` | [1568adac-25.md](1568adac-25.md) | 1) **Confirmed**: The docstring at line 22 is a single-line summary that omits parameter documentation for `alive_only` … |
| 22 | `low` | `packages/plant_service/tests/unit/test_plant_model.py` | `:252-259` | [01205db9-36.md](01205db9-36.md) | The review identifies a genuine test coverage gap. At plant.py:158, `datetime.strptime(death_date, "%Y-%m-%d")` does rej… |

## REJECTED (3)

| # | Severity | File | Lines | Report | Analysis Preview |
|---|----------|------|-------|--------|------------------|
| 1 | `high` | `backend/fastapi/tests/test_plants.py` | `:101-116` | [401b3a5f-10.md](401b3a5f-10.md) | The review premise is incorrect. The `plants_client` fixture in conftest.py:64-79 is function-scoped (default), creating… |
| 2 | `medium` | `frontend/src/api/plantTrackingAPI.ts` | `:550-559` | [79c21f84-18.md](79c21f84-18.md) | This review comment critiques auto-generated code. `plantTrackingAPI.ts` is generated by Orval v8.15.0 (see line 2: `Gen… |
| 3 | `medium` | `packages/plant_service/tests/integration/test_repository.py` | `:390-392` | [0ccd4f32-31.md](0ccd4f32-31.md) | This review is misguided for validation tests. pytest.raises(match=...) does regex substring matching (not exact), so it… |

## BACKLOG (13)

| # | Severity | File | Lines | Report | Analysis Preview |
|---|----------|------|-------|--------|------------------|
| 1 | `high` | `backend/fastapi/tests/conftest.py` | `:30-35` | [e76ef807-0.md](e76ef807-0.md) | Could not parse structured JSON from LLM response: **Verdict: BACKLOG** — exact match to existing backlog entry.  The bu… |
| 2 | `high` | `commands/plant_tracking_cli.py` | `:843-846` | [cf9314f8-11.md](cf9314f8-11.md) | The review identifies a genuine concern: bare `except Exception` catches unexpected errors, `traceback.print_exc()` dump… |
| 3 | `high` | `packages/plant_service/src/plant_service/domain/plant.py` | `:50-52` | [d30f3ff2-26.md](d30f3ff2-26.md) | Confirmed: `Plant` is `frozen=False` (line 12), and `validate_death_fields` runs only in `__post_init__` (line 50-52) an… |
| 4 | `medium` | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:76-83` | [82911b41-9.md](82911b41-9.md) | This is a documentation consistency campaign spanning multiple endpoints, not a concrete defect. The request to standard… |
| 5 | `medium` | `backend/fastapi/tests/conftest.py` | `:37-50` | [e76ef807-2.md](e76ef807-2.md) | Two concerns raised: (1) `setattr` bypasses domain validation, (2) missing type hints. The validation bypass is technica… |
| 6 | `medium` | `commands/plant_tracking_cli.py` | `:785-786` | [cf9314f8-14.md](cf9314f8-14.md) | The review correctly identifies an inconsistency: `_prompt_death_details` at line 734 has a return type hint (`-> tuple[… |
| 7 | `medium` | `commands/plant_tracking_cli.py` | `:785-786` | [cf9314f8-22.md](cf9314f8-22.md) | The finding is real: `_prompt_death_details` (line 734) has type hints (`-> tuple[str, str, str]`) while `mark_dead` (li… |
| 8 | `medium` | `commands/plant_tracking_cli.py` | `:737-743` | [cf9314f8-24.md](cf9314f8-24.md) | Could not parse structured JSON from LLM response: **Verdict: VALID**  Confirmed two concrete defects in `_prompt_death_… |
| 9 | `medium` | `packages/plant_service/src/plant_service/domain/plant.py` | `:33-35` | [d30f3ff2-29.md](d30f3ff2-29.md) | Could not parse structured JSON from LLM response: **Verdict: BACKLOG**  **1. Confirmed**: Yes, `death_date` and `planti… |
| 10 | `medium` | `packages/plant_service/tests/integration/test_repository.py` | `:298-304` | [0ccd4f32-32.md](0ccd4f32-32.md) | Could not parse structured JSON from LLM response: ACK. The verdict is **BACKLOG** — valid observation but a low-priorit… |
| 11 | `low` | `backend/fastapi/tests/conftest.py` | `:11-18` | [e76ef807-4.md](e76ef807-4.md) | No text content in opencode output ({"type":"step_start","timestamp":1786587130825,"sessionID":"ses_0071bf778ffe1p63YnMu… |
| 12 | `low` | `packages/plant_service/tests/integration/test_repository.py` | `:281-295` | [0ccd4f32-33.md](0ccd4f32-33.md) | This is a documentation/style campaign, not a concrete defect. The review flags 13 test methods lacking docstrings but o… |
| 13 | `low` | `packages/plant_service/tests/unit/test_plant_model.py` | `:186-198` | [01205db9-37.md](01205db9-37.md) | The review comment is factually correct: `variety_name="Tomato"` appears 11 times in this file. The `base_plant_dict` fi… |

