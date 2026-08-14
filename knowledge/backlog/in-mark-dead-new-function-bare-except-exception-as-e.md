---
title: "In mark_dead (new function), bare `except Exception as e:` catches everything af…"
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:41:41Z
updated_at: 2026-08-13T02:41:41Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/cf9314f8-11.md
    file: commands/plant_tracking_cli.py
    lines: 843-846
    date: 2026-08-13
---

# In mark_dead (new function), bare `except Exception as e:` catches everything af…

## Problem

The review identifies a genuine concern: bare `except Exception` catches unexpected errors, `traceback.print_exc()` dumps raw stack traces to stdout, and `sys.exit(1)` swallows root causes. However, this 3-tier exception pattern (ValidationException → PlantTrackingServiceException → Exception) is NOT new — it already exists in the plant creation handler at commands/plant_tracking_cli.py:658-670. The only delta in mark_dead is `traceback.print_exc()`. Multiple other functions (log_humidity, log_f

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/cf9314f8-11.md` (`commands/plant_tracking_cli.py`) lines 843-846
  The review identifies a genuine concern: bare `except Exception` catches unexpected errors, `traceback.print_exc()` dumps raw stack traces to stdout, and `sys.exit(1)` swallows root causes. However, t…

