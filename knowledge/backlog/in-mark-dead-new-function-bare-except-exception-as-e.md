---
title: "In mark_dead (new function), bare `except Exception as e:` catches everything af…"
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:41:41Z
updated_at: 2026-08-21T13:48:44Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/cf9314f8-11.md
    file: commands/plant_tracking_cli.py
    lines: 843-846
    date: 2026-08-13
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r2/cf9314f8-6.md
    file: commands/plant_tracking_cli.py
    lines: 823-826
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r2/cf9314f8-7.md
    file: commands/plant_tracking_cli.py
    lines: 857-859
    date: 2026-08-21
---

# In mark_dead (new function), bare `except Exception as e:` catches everything af…

## Problem

The review identifies a genuine concern: bare `except Exception` catches unexpected errors, `traceback.print_exc()` dumps raw stack traces to stdout, and `sys.exit(1)` swallows root causes. However, this 3-tier exception pattern (ValidationException → PlantTrackingServiceException → Exception) is NOT new — it already exists in the plant creation handler at commands/plant_tracking_cli.py:658-670. The only delta in mark_dead is `traceback.print_exc()`. Multiple other functions (log_humidity, log_f

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/cf9314f8-11.md` (`commands/plant_tracking_cli.py`) lines 843-846
  The review identifies a genuine concern: bare `except Exception` catches unexpected errors, `traceback.print_exc()` dumps raw stack traces to stdout, and `sys.exit(1)` swallows root causes. However, t…


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r2/cf9314f8-6.md` (`commands/plant_tracking_cli.py`) lines 823-826
  This is the same deferred theme already tracked. The existing backlog entry `knowledge/backlog/in-mark-dead-new-function-bare-except-exception-as-e.md` documents the identical concern: bare `except Ex…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r2/cf9314f8-7.md` (`commands/plant_tracking_cli.py`) lines 857-859
  This finding targets the broad `except Exception` in the `mark_dead` function in `commands/plant_tracking_cli.py:857-859`. This is the same deferred theme already tracked in the knowledge catalog unde…
