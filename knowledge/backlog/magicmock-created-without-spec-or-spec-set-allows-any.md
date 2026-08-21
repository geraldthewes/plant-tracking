---
title: MagicMock created without spec= or spec_set= (allows any attribute silently). Te…
source_report: code-review-proj-0013-r4.json
source_severity: n/a
created_at: 2026-08-13T02:40:44Z
updated_at: 2026-08-21T06:25:04Z
source: review-analyzer
occurrences:
  - feedback: feedback-proj-0013-r4/e76ef807-4.md
    file: backend/fastapi/tests/conftest.py
    lines: 11-18
    date: 2026-08-13
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r4/e76ef807-8.md
    file: backend/fastapi/tests/conftest.py
    lines: 38-43
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r4/e76ef807-9.md
    file: backend/fastapi/tests/conftest.py
    lines: 62-64
    date: 2026-08-21
  - feedback: .review-runs/PROJ-0013/20260821T021224Z/feedback-r4/e76ef807-11.md
    file: backend/fastapi/tests/conftest.py
    lines: 72-73
    date: 2026-08-21
---

# MagicMock created without spec= or spec_set= (allows any attribute silently). Te…

## Problem

No text content in opencode output ({"type":"step_start","timestamp":1786587130825,"sessionID":"ses_0071bf778ffe1p63YnMuLRTjo4","part":{"id":"prt_ff8e42bb8001d8K4MkUSeJdQyU","messageID":"msg_ff8e40c89001KJ2oVyRdpJdrnQ","sessionID":"ses_)

## Recommendation

Revisit this deferred review finding when capacity allows.

## Occurrences

- **2026-08-13** — `feedback-proj-0013-r4/e76ef807-4.md` (`backend/fastapi/tests/conftest.py`) lines 11-18
  No text content in opencode output ({"type":"step_start","timestamp":1786587130825,"sessionID":"ses_0071bf778ffe1p63YnMuLRTjo4","part":{"id":"prt_ff8e42bb8001d8K4MkUSeJdQyU","messageID":"msg_ff8e40c89…


- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r4/e76ef807-8.md` (`backend/fastapi/tests/conftest.py`) lines 38-43
  The review correctly identifies that the mock's boolean logic is wrong for the both-True case (returns all plants). However, the suggested fix (returning empty list) is incorrect — the real repository…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r4/e76ef807-9.md` (`backend/fastapi/tests/conftest.py`) lines 62-64
  The comment raises a general concern about MagicMock not being fully specified — calling unconfigured methods returns auto-generated MagicMock objects rather than raising errors or returning meaningfu…

- **2026-08-21** — `.review-runs/PROJ-0013/20260821T021224Z/feedback-r4/e76ef807-11.md` (`backend/fastapi/tests/conftest.py`) lines 72-73
  This is the same deferred theme already tracked in the knowledge catalog. The loose MagicMock in `mock_get_uow` (line 73) is a common, intentional pattern for test fixtures that stub out a unit-of-wor…
