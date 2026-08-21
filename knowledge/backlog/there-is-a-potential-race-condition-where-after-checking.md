---
title: There is a potential race condition where after checking the plant is not dead (…
source_report: .review-runs/PROJ-0013/20260821T021224Z/code-review-r2.json
source_severity: n/a
created_at: 2026-08-21T04:12:09Z
updated_at: 2026-08-21T04:12:09Z
source: review-analyzer
occurrences:
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r2/cf9314f8-11.md
    file: commands/plant_tracking_cli.py
    lines: 835-859
    date: 2026-08-21
---

# There is a potential race condition where after checking the plant is not dead (…

## Problem

The TOCTOU pattern is real: Phase 1's `is_dead` check (line 811) is in a transaction that commits and closes before Phase 2 (user interaction), and Phase 3 (line 837) performs no re-check. Under PostgreSQL READ COMMITTED with no row-level locking, a concurrent writer can commit between phases. However, this is a low-priority hardening concern for a personal single-user CLI tool: (1) the practical probability of two concurrent processes marking the same plant dead is near-zero, (2) the worst-case

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r2/cf9314f8-11.md` (`commands/plant_tracking_cli.py`) lines 835-859
  The TOCTOU pattern is real: Phase 1's `is_dead` check (line 811) is in a transaction that commits and closes before Phase 2 (user interaction), and Phase 3 (line 837) performs no re-check. Under Postg…

