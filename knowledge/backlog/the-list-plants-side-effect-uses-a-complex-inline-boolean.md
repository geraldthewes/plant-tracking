---
title: The list_plants side_effect uses a complex inline boolean condition that is hard…
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:09:07Z
updated_at: 2026-08-13T02:41:41Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/e76ef807-0.md
    file: backend/fastapi/tests/conftest.py
    lines: 30-35
    date: 2026-08-13
  - feedback: feedback-proj-0013-r4/e76ef807-0.md
    file: backend/fastapi/tests/conftest.py
    lines: 30-35
    date: 2026-08-13
  - feedback: feedback-proj-0013-r4/e76ef807-2.md
    file: backend/fastapi/tests/conftest.py
    lines: 37-50
    date: 2026-08-13
  - feedback: feedback-proj-0013-r4/cf9314f8-14.md
    file: commands/plant_tracking_cli.py
    lines: 785-786
    date: 2026-08-13
---

# The list_plants side_effect uses a complex inline boolean condition that is hard…

## Problem

Could not parse structured JSON from LLM response: **Verdict: VALID**

1. **Confirmed bug**: With `alive_only=True, dead_only=True`, the lambda returns **all plants** — the condition `(alive_only and not p.is_dead) or (dead_only and p.is_dead)` becomes a tautology since every plant is either dead or alive. The production route at `plants.py:50-54` b

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/e76ef807-0.md` (`backend/fastapi/tests/conftest.py`) lines 30-35
  Could not parse structured JSON from LLM response: **Verdict: VALID**  1. **Confirmed bug**: With `alive_only=True, dead_only=True`, the lambda returns **all plants** — the condition `(alive_only and …


- **2026-08-13** — `feedback-proj-0013-r4/e76ef807-0.md` (`backend/fastapi/tests/conftest.py`) lines 30-35
  Could not parse structured JSON from LLM response: **Verdict: BACKLOG** — exact match to existing backlog entry.  The bug is real and the suggested fix is sound, but this was already identified, class…

- **2026-08-13** — `feedback-proj-0013-r4/e76ef807-2.md` (`backend/fastapi/tests/conftest.py`) lines 37-50
  Two concerns raised: (1) `setattr` bypasses domain validation, (2) missing type hints. The validation bypass is technically real — `Plant.__post_init__` calls `validate_death_fields()` (plant.py:50-52…

- **2026-08-13** — `feedback-proj-0013-r4/cf9314f8-14.md` (`commands/plant_tracking_cli.py`) lines 785-786
  The review correctly identifies an inconsistency: `_prompt_death_details` at line 734 has a return type hint (`-> tuple[str, str, str]`) while `mark_dead` at line 785 and `list_plants` at line 1780 la…
