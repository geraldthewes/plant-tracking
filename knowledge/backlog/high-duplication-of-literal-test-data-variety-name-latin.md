---
title: High duplication of literal test data (variety_name, latin_name, planting_date)…
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:44:21Z
updated_at: 2026-08-13T02:44:21Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/01205db9-37.md
    file: packages/plant_service/tests/unit/test_plant_model.py
    lines: 186-198
    date: 2026-08-13
---

# High duplication of literal test data (variety_name, latin_name, planting_date)…

## Problem

The review comment is factually correct: `variety_name="Tomato"` appears 11 times in this file. The `base_plant_dict` fixture (line 132) is used by only 2 of ~12 tests in `TestPlantDeathFields`; the remaining tests repeat the same 3 literal fields. However, this is not a defect — the tests pass and the code is correct. It's a maintenance/refactoring theme: extracting a shared helper or adapting the fixture for the parametrized `constructor` pattern (which takes kwargs, not a dict). No existing b

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/01205db9-37.md` (`packages/plant_service/tests/unit/test_plant_model.py`) lines 186-198
  The review comment is factually correct: `variety_name="Tomato"` appears 11 times in this file. The `base_plant_dict` fixture (line 132) is used by only 2 of ~12 tests in `TestPlantDeathFields`; the r…

