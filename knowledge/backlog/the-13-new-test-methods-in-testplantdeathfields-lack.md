---
title: The 13 new test methods in TestPlantDeathFields lack docstrings (fixtures have b…
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:43:53Z
updated_at: 2026-08-21T07:27:25Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/0ccd4f32-33.md
    file: packages/plant_service/tests/integration/test_repository.py
    lines: 281-295
    date: 2026-08-13
  - feedback: .review-runs/feedback-r1/0ccd4f32-10.md
    file: packages/plant_service/tests/integration/test_repository.py
    lines: 280-295
    date: 2026-08-18
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r3/0ccd4f32-7.md
    file: packages/plant_service/tests/integration/test_repository.py
    lines: 281-295
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r3/0ccd4f32-12.md
    file: packages/plant_service/tests/integration/test_repository.py
    lines: 281-295
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r5/0ccd4f32-6.md
    file: packages/plant_service/tests/integration/test_repository.py
    lines: 280-280
    date: 2026-08-21
---

# The 13 new test methods in TestPlantDeathFields lack docstrings (fixtures have b…

## Problem

This is a documentation/style campaign, not a concrete defect. The review flags 13 test methods lacking docstrings but only provides a fix for 1. Project context shows 21 of 22 test classes have no method docstrings — only `TestGenusGenerateId` is an outlier with docstrings. The test method names in `TestPlantDeathFields` are already descriptive (e.g., `test_update_plant_death_fields`, `test_list_plants_alive_only_filter`), communicating intent without docstrings. The suggestion is well-intentio

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/0ccd4f32-33.md` (`packages/plant_service/tests/integration/test_repository.py`) lines 281-295
  This is a documentation/style campaign, not a concrete defect. The review flags 13 test methods lacking docstrings but only provides a fix for 1. Project context shows 21 of 22 test classes have no me…


- **2026-08-18** — `.review-runs/feedback-r1/0ccd4f32-10.md` (`packages/plant_service/tests/integration/test_repository.py`) lines 280-295
  This is a documentation/style finding — adding a class-level docstring to TestPlantDeathFields. It's the same deferred theme as the existing backlog entry tracking missing docstrings in this exact cla…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r3/0ccd4f32-7.md` (`packages/plant_service/tests/integration/test_repository.py`) lines 281-295
  This is a style/maintainability nit, not a functional defect: adding a one-line docstring to a self-explanatory test. Two compounding problems make this a clear BACKLOG rather than VALID. (1) The comm…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r3/0ccd4f32-12.md` (`packages/plant_service/tests/integration/test_repository.py`) lines 281-295
  The suggested change is a docstring addition, part of the broader '13 test methods lack docstrings' campaign already in backlog. The date-type inconsistency (sa.Date() in migration vs String(10) in mo…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r5/0ccd4f32-6.md` (`packages/plant_service/tests/integration/test_repository.py`) lines 280-280
  Missing class-level docstring on TestPlantDeathFields is the same deferred documentation/style campaign already tracked in the backlog (4 prior occurrences, including an r1 finding on this exact line …
