---
title: "death_date (and planting_date) are typed as str | None (or str) and validated wi…"
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:43:05Z
updated_at: 2026-08-21T07:27:25Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/d30f3ff2-29.md
    file: packages/plant_service/src/plant_service/domain/plant.py
    lines: 33-35
    date: 2026-08-13
  - feedback: .review-runs/feedback-r1/c0c9fd17-0.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 8-8
    date: 2026-08-18
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r1/c0c9fd17-1.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 6-10
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r1/c0c9fd17-9.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 6-10
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r2/c0c9fd17-4.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 8-8
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r3/c0c9fd17-0.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 6-10
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r4/c0c9fd17-5.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 8-8
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r5/c0c9fd17-0.md
    file: backend/fastapi/src/plant_tracking_api/schemas.py
    lines: 8-8
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r5/82911b41-4.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 128-140
    date: 2026-08-21
---

# death_date (and planting_date) are typed as str | None (or str) and validated wi…

## Problem

Could not parse structured JSON from LLM response: **Verdict: BACKLOG**

**1. Confirmed**: Yes, `death_date` and `planting_date` are `str | None` with manual `strptime` (`plant.py:156-160`), while `created_at`/`updated_at` use proper `datetime` types (`plant.py:31-32`).

**2. Why problematic**: String dates lack compile-time type safety, require for

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/d30f3ff2-29.md` (`packages/plant_service/src/plant_service/domain/plant.py`) lines 33-35
  Could not parse structured JSON from LLM response: **Verdict: BACKLOG**  **1. Confirmed**: Yes, `death_date` and `planting_date` are `str | None` with manual `strptime` (`plant.py:156-160`), while `cr…


- **2026-08-18** — `.review-runs/feedback-r1/c0c9fd17-0.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 8-8
  The finding correctly identifies a type inconsistency: `PlantDeathRequest.death_date: str` (schemas.py:8) vs `date | None` in all response models. However, this is NOT an auto-fixable one-line defect.…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r1/c0c9fd17-1.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 6-10
  The type inconsistency is real (death_date: str vs date|None in responses), but this is the same deferred theme already tracked in the backlog. The prior occurrence (2026-08-18) on this exact file not…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r1/c0c9fd17-9.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 6-10
  Confirmed real-but-deferred, not a fixable defect. (1) The reviewer's premise that a date-format validation is missing is wrong: routes/plants.py:128-134 already calls PlantDomain.validate_death_field…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r2/c0c9fd17-4.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 8-8
  The type inconsistency is real: PlantDeathRequest.death_date is str (line 8) while all response schemas use date | None. However, this is the same deferred theme already tracked in the backlog (create…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r3/c0c9fd17-0.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 6-10
  The type inconsistency is real: PlantDeathRequest.death_date is `str` (line 8) while all response schemas (PlantSummary, PlantResponse, PlantDeadResponse) use `date | None`. However, this is the exact…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r4/c0c9fd17-5.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 8-8
  The observation is correct: PlantDeathRequest.death_date uses `str` while response models (PlantSummary, PlantResponse) use `date | None`, creating an inconsistent API contract and missing Pydantic's …

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r5/c0c9fd17-0.md` (`backend/fastapi/src/plant_tracking_api/schemas.py`) lines 8-8
  Confirmed real type inconsistency (death_date: str vs date | None in response models), but this is the exact same deferred theme already tracked in the backlog with 7 prior occurrences on this same fi…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r5/82911b41-4.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 128-140
  The future-date check is a valid concern but the suggested fix is in the wrong layer. It should be added to Plant.validate_death_fields (domain) rather than the route handler, so all callers (API, CLI…
