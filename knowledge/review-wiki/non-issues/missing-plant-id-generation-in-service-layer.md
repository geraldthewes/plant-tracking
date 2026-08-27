---
topic: Missing Plant ID Generation in Service Layer
category: non-issue
first_seen: 2026-08-27
last_updated: 2026-08-27
occurrences:
  - report: knowledge/reviews/2026-08-26-review-PROJ-0013.md
    severity: critical
    reason: "False positive — the repository IS the service-layer adapter and it does call the domain's generate_id() before persisting, matching the documented PROJ-0008 design."
    ticket: PROJ-0013
---

# Missing Plant ID Generation in Service Layer

## Pattern

```
**Severity**: CRITICAL

**Problem**:
The repository's `create_plant` method is generating the plant ID, but according to the plan and existing code review comments, ID generation should happen in the domain layer. The Plant.domain.generate_id method exists but isn't being used consistently.

**Why it matters**:
(n/a — finding is a false positive; see Resolution)

**Evidence**:
- packages/plant_service/src/plant_service/adapters/repository/plant_repository.py:27-38 (cited as 51-64 in the report, which is actually the ORM death-field mapping)
```

## Recommendation

Report recommendation:
```
Move ID generation back to the domain layer by having the service layer call `plant.generate_id()` before persisting, or ensure the repository uses the domain object's ID if it's already set.
```

## Resolution (2026-08-27)

The premise is incorrect. Facts established during analysis:

1. **The repository IS the service layer.** `PlantRepository` is the only implementor of the `PlantService` protocol (`plant_repository.py:15`); there is no separate service implementation class. The report's "service layer" and "repository layer" refer to the same code.
2. **The domain owns ID generation.** Format logic lives in `Plant.generate_id` / `Plant.find_next_sequence` (`domain/plant.py:75-102`) as pure functions with no DB access. The adapter calls the domain method (`plant_repository.py:35`) before persisting — exactly what the report's fix option (a) asks for.
3. **This is the documented design.** The PROJ-0008 plan that created the service package states: *"domain layer doesn't have DB access — Sequence generation will be handled in application layer"* and its repository sketch says *"ID generation logic moved to application/service layer"*. The `generate_id` docstring repeats: *"seq is passed in from the service layer which queries existing records."*
4. **Factual errors in the report**: cited plan section (PROJ-0013 Phase 2) contains no ID-generation requirement; the cited line range (51-64) is wrong; `generate_id` IS used consistently across all three repositories (plant:35, genus:25, seed_packet:25); no prior "code review comments" supporting the claim exist in `knowledge/`.

**Genuine minor defect found and fixed**: `create_plant` unconditionally overwrote a caller-provided `plant_data["id"]`. Fixed by only generating an ID when none was provided (fix option (b)). Covered by `test_create_plant_preserves_caller_provided_id` in `packages/plant_service/tests/integration/test_repository.py`.

## References
- [PROJ-0008 plan (service package design)](../../plans/2026-05-20-PROJ-0008-create-python-service-package.md)
- [ADR-0008 ports & adapters](../../architecture/decisions/ADR-0008-architecture-refinement-ports-and-adapters.md)
- [Domain Plant model](../../../../packages/plant_service/src/plant_service/domain/plant.py)
- Related ticket: PROJ-0013

## Occurrences
- **2026-08-27** — `knowledge/reviews/2026-08-26-review-PROJ-0013.md` (critical)
  Reason: False positive — conflates the service-layer adapter with the repository and misreads the documented PROJ-0008 ID-generation design; only the ID-overwrite sub-issue was real and has been fixed.
