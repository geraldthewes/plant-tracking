---
title: The get_plant and mark_plant_dead endpoints incorrectly convert empty strings to…
source_report: .review-runs/PROJ-0013/20260821T021224Z/code-review-r3.json
source_severity: n/a
created_at: 2026-08-21T05:26:30Z
updated_at: 2026-08-21T06:25:04Z
source: review-analyzer
occurrences:
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r3/82911b41-6.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 109-152
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r4/82911b41-4.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 88-106
    date: 2026-08-21
---

# The get_plant and mark_plant_dead endpoints incorrectly convert empty strings to…

## Problem

Could not parse structured JSON from LLM response: ```json
{
  "verdict": "VALID",
  "analysis": "The `or None` pattern (e.g., `updated.death_comment or None`) is a real data-integrity bug: Python treats empty string `\"\"` as falsy, so it silently converts `\"\"` to `None`. If a user explicitly sets death_comment to `\"\"`, it's stored as `\"\"` in

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r3/82911b41-6.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 109-152
  Could not parse structured JSON from LLM response: ```json {   "verdict": "VALID",   "analysis": "The `or None` pattern (e.g., `updated.death_comment or None`) is a real data-integrity bug: Python tre…


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r4/82911b41-4.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 88-106
  The 'or None' pattern at plants.py:102-104 (and 148-150) is a consistency/cleanliness concern, not a concrete defect. Validation (plant.py:142-178) rejects empty-string death_date and death_reason at …
