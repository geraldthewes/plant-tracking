---
title: _prompt_death_details uses raw input() in while loops without catching EOFError/…
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:42:45Z
updated_at: 2026-08-21T15:48:49Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/cf9314f8-24.md
    file: commands/plant_tracking_cli.py
    lines: 737-743
    date: 2026-08-13
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r1/cf9314f8-3.md
    file: commands/plant_tracking_cli.py
    lines: 734-789
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r2/cf9314f8-10.md
    file: commands/plant_tracking_cli.py
    lines: 740-742
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r4/cf9314f8-10.md
    file: commands/plant_tracking_cli.py
    lines: 734-789
    date: 2026-08-21
---

# _prompt_death_details uses raw input() in while loops without catching EOFError/…

## Problem

Could not parse structured JSON from LLM response: **Verdict: VALID**

Confirmed two concrete defects in `_prompt_death_details()` at `commands/plant_tracking_cli.py:734-782`:

1. **Missing signal handling**: Five `input()` calls across three loops with zero `EOFError`/`KeyboardInterrupt` handling — verified no such handling exists anywhere in the f

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/cf9314f8-24.md` (`commands/plant_tracking_cli.py`) lines 737-743
  Could not parse structured JSON from LLM response: **Verdict: VALID**  Confirmed two concrete defects in `_prompt_death_details()` at `commands/plant_tracking_cli.py:734-782`:  1. **Missing signal han…


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r1/cf9314f8-3.md` (`commands/plant_tracking_cli.py`) lines 734-789
  The finding is legitimate but not a concrete defect. In the most common non-interactive case (stdin=/dev/null or closed), the first input() call raises EOFError immediately, which is already caught (l…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r2/cf9314f8-10.md` (`commands/plant_tracking_cli.py`) lines 740-742
  Design preference, not a defect: Phase 2 has no DB access or open transaction, so sys.exit(0) on EOFError/KeyboardInterrupt has no side effects and the caller (mark_dead:833) has nothing to do but exi…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r4/cf9314f8-10.md` (`commands/plant_tracking_cli.py`) lines 734-789
  The observation is factually correct: in `_prompt_death_details()` (commands/plant_tracking_cli.py:734-789), only the death-date loop wraps `input()` in `try/except (EOFError, KeyboardInterrupt)`. The…
