---
title: There is a potential race condition where after checking the plant is not dead (…
source_report: .review-runs/PROJ-0013/20260821T021224Z/code-review-r2.json
source_severity: n/a
created_at: 2026-08-21T04:12:09Z
updated_at: 2026-08-21T12:51:57Z
source: review-analyzer
occurrences:
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r2/cf9314f8-11.md
    file: commands/plant_tracking_cli.py
    lines: 835-859
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r4/cf9314f8-12.md
    file: commands/plant_tracking_cli.py
    lines: 792-859
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r5/cf9314f8-2.md
    file: commands/plant_tracking_cli.py
    lines: 792-859
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r1/82911b41-4.md
    file: backend/fastapi/src/plant_tracking_api/routes/plants.py
    lines: 122-140
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


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r4/cf9314f8-12.md` (`commands/plant_tracking_cli.py`) lines 792-859
  The TOCTOU race condition is real but this is a repeat of an already-triaged deferred theme. The exact same issue in the same file (commands/plant_tracking_cli.py) was previously triaged as BACKLOG (d…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r5/cf9314f8-2.md` (`commands/plant_tracking_cli.py`) lines 792-859
  The TOCTOU observation is technically valid — there is a gap between Phase 1 (check) and Phase 3 (update) where a concurrent process could modify the plant. However, this is a CLI tool where two concu…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r1/82911b41-4.md` (`backend/fastapi/src/plant_tracking_api/routes/plants.py`) lines 122-140
  Real TOCTOU pattern but same deferred theme as the existing backlog entry (race condition on death check). The original triage noted near-zero probability and minimal impact for a personal plant-track…
