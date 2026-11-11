# Review Findings Index

## VALID (21)

| # | File | Lines | Report | Analysis Preview |
|---|------|-------|--------|------------------|
| 1 | `alembic/versions/a1b2c3d4e5f6_add_death_fields_to_plant.py` | `:23-26` | [1ff5ce22-0.md](1ff5ce22-0.md) | 1) CONFIRMED: This is a genuine data integrity issue. Storing dates as `String(length=10)` is an anti-pattern.  2) WHY I… |
| 2 | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:34-39` | [82911b41-2.md](82911b41-2.md) | 1. ISSUE CONFIRMED: The current code at plants.py:34 does `list(uow.plants.list_plants())` which materializes ALL plants… |
| 3 | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:36-39` | [82911b41-3.md](82911b41-3.md) | 1. **Issue Confirmed**: Yes, this is a real bug. If a client sends `?alive_only=true&dead_only=true`, the `if` branch ex… |
| 4 | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:112-123` | [82911b41-5.md](82911b41-5.md) | Confirmed real problem. `PlantDomain.create_from_dict` validates REQUIRED_FIELDS [variety_name, latin_name, planting_dat… |
| 5 | `commands/plant_tracking_cli.py` | `:797-805` | [cf9314f8-7.md](cf9314f8-7.md) | Confirmed real bug at line 805. When death_reason=='Other', the required comment captured in the while loop (lines 800-8… |
| 6 | `commands/plant_tracking_cli.py` | `:1868-1874` | [cf9314f8-8.md](cf9314f8-8.md) | The existing code places `:<22` outside f-string braces, so it renders as literal text (e.g., 'Death Date:<22    2024-01… |
| 7 | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:41-55` | [82911b41-6.md](82911b41-6.md) | The review identifies a legitimate architectural concern. Three findings:  1. **Current state**: Zero Pydantic schemas e… |
| 8 | `commands/plant_tracking_cli.py` | `:826-831` | [cf9314f8-10.md](cf9314f8-10.md) | The concern is legitimate: the broad `except Exception` swallows stack traces, leaving only the exception message. If an… |
| 9 | `commands/plant_tracking_cli.py` | `:763-772` | [cf9314f8-11.md](cf9314f8-11.md) | Confirmed: `from datetime import datetime` at line 764 is nested inside a while loop within the `mark-dead` command hand… |
| 10 | `backend/fastapi/tests/test_plants.py` | `:78-92` | [401b3a5f-12.md](401b3a5f-12.md) | The review is correct. 10 test functions (lines 76-266) each repeat identical 6-line boilerplate: imports, `_mock_uow_wi… |
| 11 | `backend/fastapi/tests/test_plants.py` | `:78-82` | [401b3a5f-14.md](401b3a5f-14.md) | The review comment is technically correct but superficial. The imports on lines 78-79 are duplicated across 10 test func… |
| 12 | `backend/fastapi/tests/test_plants.py` | `:76-92` | [401b3a5f-16.md](401b3a5f-16.md) | The review is correct: 8 out of 10 tests duplicate TestClient creation and dependency override management. However, the … |
| 13 | `frontend/src/api/plantTrackingAPI.ts` | `:557-558` | [79c21f84-19.md](79c21f84-19.md) | The reviewer correctly identified an inconsistency but mischaracterized the root cause. The trailing slash is NOT condit… |
| 14 | `frontend/src/api/plantTrackingAPI.ts` | `:665-681` | [79c21f84-20.md](79c21f84-20.md) | Two issues raised, one strong and one weak.  **Issue 1 — Missing required field validation: REAL PROBLEM.** If `body.dea… |
| 15 | `frontend/src/api/plantTrackingAPI.ts` | `:665-677` | [79c21f84-21.md](79c21f84-21.md) | CONFIRMED BUG — format mismatch between frontend and backend.  **Evidence:**  1. **Backend signature** (`backend/fastapi… |
| 16 | `packages/plant_service/src/plant_service/domain/plant.py` | `:127-149` | [d30f3ff2-22.md](d30f3ff2-22.md) | 1. CONFIRMED ISSUE: The gap is real. `is_dead` (plant.py:51-53) returns `bool(self.death_date)`, so a plant with death_d… |
| 17 | `packages/plant_service/src/plant_service/domain/plant.py` | `:127-149` | [d30f3ff2-23.md](d30f3ff2-23.md) | 1. ISSUE CONFIRMED: Yes, this is a real data integrity problem. `is_dead` derives solely from `death_date` (plant.py:53:… |
| 18 | `packages/plant_service/tests/unit/test_plant_model.py` | `:180-198` | [01205db9-24.md](01205db9-24.md) | The review identifies a real gap: `Plant` is a dataclass with NO constructor validation — all validation lives exclusive… |
| 19 | `packages/plant_service/tests/integration/test_repository.py` | `:388-395` | [0ccd4f32-26.md](0ccd4f32-26.md) | 1. CONFIRMED: This is a real gap. The `is_dead` property (plant.py:53) is derived solely from `death_date`: `return bool… |
| 20 | `packages/plant_service/tests/integration/test_repository.py` | `:338-343` | [0ccd4f32-27.md](0ccd4f32-27.md) | The test names `test_filter_alive_plants` and `test_filter_dead_plants` (lines 318, 345) promise repository-level filter… |
| 21 | `packages/plant_service/tests/integration/test_repository.py` | `:242-248` | [0ccd4f32-28.md](0ccd4f32-28.md) | 1. CONFIRMED: Real duplication across 6 methods in TestPlantDeathFields (lines 241-394). Every test repeats the pattern … |

## REJECTED (2)

| # | File | Lines | Report | Analysis Preview |
|---|------|-------|--------|------------------|
| 1 | `backend/fastapi/tests/test_plants.py` | `:76-77` | [401b3a5f-15.md](401b3a5f-15.md) | The review raises a superficially valid point but the recommendation is misguided. The test function names (e.g., `test_… |
| 2 | `frontend/src/api/plantTrackingAPI.ts` | `:550-559` | [79c21f84-18.md](79c21f84-18.md) | This review comment is well-intentioned but targets the wrong layer. The file `frontend/src/api/plantTrackingAPI.ts` is … |

## BACKLOG (6)

| # | File | Lines | Report | Analysis Preview |
|---|------|-------|--------|------------------|
| 1 | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:91-98` | [82911b41-1.md](82911b41-1.md) | opencode execution timed out (>120s) |
| 2 | `backend/fastapi/src/plant_tracking_api/routes/plants.py` | `:25-30` | [82911b41-4.md](82911b41-4.md) | opencode execution timed out (>120s) |
| 3 | `commands/plant_tracking_cli.py` | `:730-733` | [cf9314f8-9.md](cf9314f8-9.md) | Two complaints in one review: type hints and cyclomatic complexity.  **Type hints (Partial)**: The suggestion is technic… |
| 4 | `backend/fastapi/tests/test_plants.py` | `:6-10` | [401b3a5f-13.md](401b3a5f-13.md) | No text content in opencode output ({"type":"step_start","timestamp":1786211088589,"sessionID":"ses_01d85fa86ffe5UWYEEIF… |
| 5 | `backend/fastapi/tests/test_plants.py` | `:29-29` | [401b3a5f-17.md](401b3a5f-17.md) | opencode execution timed out (>120s) |
| 6 | `packages/plant_service/tests/unit/test_plant_model.py` | `:212-227` | [01205db9-25.md](01205db9-25.md) | opencode execution timed out (>120s) |

