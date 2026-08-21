---
title: "Inconsistent exception handling: first try block prints traceback for unexpected…"
source_report: .review-runs/PROJ-0013/20260821T021224Z/code-review-r1.json
source_severity: n/a
created_at: 2026-08-21T03:09:07Z
updated_at: 2026-08-21T12:51:57Z
source: review-analyzer
occurrences:
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r1/cf9314f8-0.md
    file: commands/plant_tracking_cli.py
    lines: 823-826
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r2/cf9314f8-10.md
    file: commands/plant_tracking_cli.py
    lines: 823-826
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r5/cf9314f8-12.md
    file: commands/plant_tracking_cli.py
    lines: 823-826
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T115106Z/feedback-r1/cf9314f8-1.md
    file: commands/plant_tracking_cli.py
    lines: 823-826
    date: 2026-08-21
---

# Inconsistent exception handling: first try block prints traceback for unexpected…

## Problem

opencode exited with code 1: [91m[1mError: [0mUnexpected error

database is locked

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r1/cf9314f8-0.md` (`commands/plant_tracking_cli.py`) lines 823-826
  opencode exited with code 1: [91m[1mError: [0mUnexpected error  database is locked


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r2/cf9314f8-10.md` (`commands/plant_tracking_cli.py`) lines 823-826
  Confirmed: at commands/plant_tracking_cli.py:823-826, the first transaction's generic handler calls traceback.print_exc(), while the second handler (lines 857-859) does not. The inconsistency is real …

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r5/cf9314f8-12.md` (`commands/plant_tracking_cli.py`) lines 823-826
  Same deferred theme as previously triaged: the broad except at plant_tracking_cli.py:823-826 calling traceback.print_exc() was already BACKLOGed in r1 (cf9314f8-0) and r2 (cf9314f8-10) for the same li…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T115106Z/feedback-r1/cf9314f8-1.md` (`commands/plant_tracking_cli.py`) lines 823-826
  The concern about 'leaking sensitive internal details' is weak for a local CLI tool — the person running the CLI is the operator/developer themselves. Traceback printing in CLI tools is idiomatic and …
