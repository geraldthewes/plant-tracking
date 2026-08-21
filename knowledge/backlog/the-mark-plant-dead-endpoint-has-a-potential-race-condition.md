---
title: The mark_plant_dead endpoint has a potential race condition between checking if…
source_report: .review-runs/PROJ-0013/20260821T115106Z/code-review-r6.json
source_severity: n/a
created_at: 2026-08-21T17:39:04Z
updated_at: 2026-08-21T17:39:04Z
source: review-analyzer
occurrences:
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r6/82911b41-1.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 122-143
    date: 2026-08-21
---

# The mark_plant_dead endpoint has a potential race condition between checking if…

## Problem

opencode exited with code 1: [91m[1mError: [0mUnexpected error

database is locked

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r6/82911b41-1.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 122-143
  opencode exited with code 1: [91m[1mError: [0mUnexpected error  database is locked

