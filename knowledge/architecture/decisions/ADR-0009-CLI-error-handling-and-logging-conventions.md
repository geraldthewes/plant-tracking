# ADR-0009 - CLI Error Handling and Logging Conventions

## Status

Accepted — The CLI surfaces concise, user-friendly messages for all failures, exits non-zero on every error path, and records full details of unexpected errors via the stdlib `logging` module instead of printing stack traces to the terminal.

### Relationships

Relates to: ADR-0008 (Ports & Adapters entrypoint responsibilities), ADR-0005 (Backend Technology Stack)

## Context

The `mark-dead` command previously printed raw stack traces to the terminal via `traceback.print_exc()` on unexpected errors. This was an information leak — internal implementation details (file paths, library frames) are not useful to a user running the CLI in the garden, and it looked inconsistent with the other commands, which already printed one-line messages.

History of the `print_exc` calls in `mark_dead`:

- `7fc01a2` added a `print_exc` call to the unexpected-error handler
- `805b52f` split `mark_dead` into a check phase and a write phase, each with its own `print_exc` call
- `f4ac42e` removed the write-phase call ("info leak" fix)
- the check-phase call remained in `mark_dead`'s plant-exists handler until this ADR's accompanying cleanup removed it

A review triggered by this cleanup also evaluated a feedback item claiming that other commands (e.g., `create_plant`) "still use" `print_exc`. That claim was incorrect — `create_plant` never contained a `print_exc` call; after the check-phase removal, zero `print_exc` calls remain anywhere in the codebase. The review did surface genuine residual gaps:

1. **Dead import** — `import traceback` in `commands/plant_tracking_cli.py` remained after the last `print_exc` call was removed.
2. **Inconsistent exit codes** — `mark_dead`, `show_*`, and `create_*` commands call `sys.exit(1)` on failure, but `log_*` and `media_*` commands print an error message and return normally (exit code 0), so scripts and cron jobs cannot detect their failure.
3. **Silent exception swallowing** — eleven lookup/verification paths use bare `except Exception: pass` (e.g., the genus and seed-packet lookups in `create_plant`, the duplicate checks in `create_seed_packet`/`create_genus`, and the plant-exists checks in the `log_*` commands), leaving no trace when they fail. This makes debugging hard and violates the project guideline to never swallow exceptions without logging.
4. **No logging infrastructure** — the CLI used no `logging` configuration at all; an unexpected error left no record beyond the one-line message shown to the user.

## Decision

We adopt the following conventions for all CLI entrypoint code (`commands/plant_tracking_cli.py`), matching the pattern already established by `mark_dead`:

### 1. Expected (domain) exceptions → friendly message, exit 1

Domain exceptions from `plant_service.domain.exceptions` (`ValidationException`, `PlantNotFoundException`, `PlantTrackingServiceException`, etc.) are caught at the command boundary and converted to a concise `✗ ...` message on stdout, followed by `sys.exit(1)`. No stack trace, no internal identifiers.

### 2. Unexpected exceptions → log the detail, show the user a short message, exit 1

Any exception not covered by (1) is caught by a final `except Exception` handler that:

- logs the full exception (including traceback) via `logging.exception(...)` at ERROR level, and
- prints a single concise line (e.g., `✗ Unexpected error: <message>`) to the user, then calls `sys.exit(1)`.

Full tracebacks never appear on the user's terminal by default. The log record is the debugging surface.

### 3. Logging configuration

The CLI configures the stdlib `logging` module once at startup in `main()`:

- Logger name: `plant_tracking.cli`
- Handler: `StreamHandler` writing to **stderr** (stdout is reserved for command output, so piped output stays clean)
- Format: `%(asctime)s %(levelname)s %(name)s: %(message)s`, with `exc_info` attached for unexpected errors
- Level: `INFO` by default, overridable via the `PLANT_TRACKING_LOG_LEVEL` environment variable (e.g., `PLANT_TRACKING_LOG_LEVEL=debug`)

No third-party logging dependency is added.

### 4. No silent exception swallowing

Bare `except Exception: pass` blocks are not permitted. Any intentionally-tolerated failure (e.g., a genus lookup that falls back to manual entry) must at minimum `logging.getLogger(__name__).warning(...)` with enough context to diagnose the failure later.

### 5. Exit codes

- `0` — success (including user-initiated cancellation of an interactive prompt)
- `1` — any operational error: missing entity, validation failure, service error, or unexpected exception

All command handlers must use `sys.exit(1)` on failure; returning normally after printing an error is not allowed.

## Alternatives Considered

- **Keep printing tracebacks to the terminal**: rejected — information leak, poor UX, inconsistent across commands; the debugging value is better served by a log with timestamps.
- **Shared error-handling utility module (decorator/context manager wrapping every command)**: rejected at this time — the CLI is a single ~2,700-line file where the catch → message → `sys.exit(1)` pattern is already uniform in the write-path commands; an abstraction layer adds indirection without reducing duplication. Revisit if the CLI splits into multiple modules.
- **`click` with its built-in error handling**: rejected — the CLI already uses `argparse` (ADR-0005 stack), and `click`'s defaults still print tracebacks on unhandled exceptions, so we would need the same logging setup on top.

## Consequences

### Positive

- Users always see exactly one actionable line per failure; internal details stay out of the terminal
- Full diagnostic detail is preserved in the stderr log for debugging
- Scripts/cron can rely on the exit code to detect CLI failures
- Future CLI commands have a single documented pattern to copy

### Negative

- `log_*` and `media_*` commands currently return exit 0 on failure; bringing them to exit 1 is a behavior change that could break callers relying on the old (buggy) semantics — tracked as a follow-up
- stderr logging means error details are invisible if a user discards stderr; acceptable because the one-line message still conveys the failure

### Neutral

- FastAPI entrypoint is unaffected (it has its own exception handling and structured logging)
- No schema, migration, or domain-layer changes

## Follow-up Work (not covered by this ADR)

1. Wire `logging.basicConfig(...)` into `main()` and add `logging.exception` calls in the generic `except` handlers of all command handlers
2. Change `log_*` and `media_*` failure paths from `return` to `sys.exit(1)` (covered by new tests first)
3. Replace the remaining `except Exception: pass` blocks (eleven occurrences: genus/packet lookups in `create_plant`, duplicate checks in `create_seed_packet`/`create_genus`, plant-exists checks in `log_*`/`media_*` commands) with logged warnings

## Related NFRs

- NFR-RELI-01: Data integrity with zero lost or corrupted plant records (failure visibility supports this)
- NFR-MAINT-01: System maintainability through clear separation of concerns (uniform error-handling pattern)
