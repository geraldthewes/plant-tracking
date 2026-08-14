---
title: "death_date (and planting_date) are typed as str | None (or str) and validated wi…"
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:43:05Z
updated_at: 2026-08-13T02:43:05Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/d30f3ff2-29.md
    file: packages/plant_service/src/plant_service/domain/plant.py
    lines: 33-35
    date: 2026-08-13
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

