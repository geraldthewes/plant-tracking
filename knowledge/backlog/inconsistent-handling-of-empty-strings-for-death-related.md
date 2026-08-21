---
title: Inconsistent handling of empty strings for death-related fields across endpoints…
source_report: .review-runs/PROJ-0013/20260821T021224Z/code-review-r2.json
source_severity: n/a
created_at: 2026-08-21T04:11:44Z
updated_at: 2026-08-21T07:27:25Z
source: review-analyzer
occurrences:
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r2/82911b41-2.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 109-152
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r3/82911b41-8.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 76-106
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r5/82911b41-7.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 102-104
    date: 2026-08-21
---

# Inconsistent handling of empty strings for death-related fields across endpoints…

## Problem

Could not parse structured JSON from LLM response: Let me verify the model defaults and existing route tests to ground the analysis.

I've verified the code, schema, domain validation, and existing tests. Here's my analysis.

**Verification of the claim:**
- `mark_plant_dead` runs `validate_death_fields` before updating. `death_date=""` → `strptime`

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r2/82911b41-2.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 109-152
  Could not parse structured JSON from LLM response: Let me verify the model defaults and existing route tests to ground the analysis.  I've verified the code, schema, domain validation, and existing te…


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r3/82911b41-8.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 76-106
  Confirmed real but not standalone-fixable. Verified facts: (1) All death fields are typed str|None / date|None in PlantResponse and PlantDeadResponse (schemas.py:45-47, 55-57) and in the domain Plant …

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r5/82911b41-7.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 102-104
  The reviewer's claim that `or None` is redundant is partially correct but the fix is not safe in isolation. The domain model types these fields as `str | None = None` (plant.py:33-35), but `PlantDeath…
