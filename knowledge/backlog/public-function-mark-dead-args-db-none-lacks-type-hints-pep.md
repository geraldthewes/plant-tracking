---
title: Public function mark_dead(args, db=None) lacks type hints (PEP 484/PEP 8). _prom…
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:42:08Z
updated_at: 2026-08-18T22:15:13Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/cf9314f8-22.md
    file: commands/plant_tracking_cli.py
    lines: 785-786
    date: 2026-08-13
  - feedback: .review-runs/feedback-r1/0ccd4f32-11.md
    file: packages/plant_service/tests/integration/test_repository.py
    lines: 32-39
    date: 2026-08-18
---

# Public function mark_dead(args, db=None) lacks type hints (PEP 484/PEP 8). _prom…

## Problem

The finding is real: `_prompt_death_details` (line 734) has type hints (`-> tuple[str, str, str]`) while `mark_dead` (line 785) and `list_plants` (line 1780) do not. However, this isn't an isolated defect — all 21 public command handler functions in this 2636-line file lack parameter type hints (create_plant, print_label, log_humidity, log_water, etc.). Adding type hints is a style campaign across the entire file, not a single-file fix. Per classification rule 2, style campaigns should be BACKLO

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/cf9314f8-22.md` (`commands/plant_tracking_cli.py`) lines 785-786
  The finding is real: `_prompt_death_details` (line 734) has type hints (`-> tuple[str, str, str]`) while `mark_dead` (line 785) and `list_plants` (line 1780) do not. However, this isn't an isolated de…


- **2026-08-18** — `.review-runs/feedback-r1/0ccd4f32-11.md` (`packages/plant_service/tests/integration/test_repository.py`) lines 32-39
  This is the same deferred theme as the existing backlog entry: adding type hints per PEP 484 is a style campaign, not a concrete defect. The existing backlog entry (knowledge/backlog/public-function-m…
