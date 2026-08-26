# Standardize CLI error handling and logging per ADR-0009 Implementation Plan

## Overview

This plan implements the CLI error handling and logging standardization as defined in ADR-0009. The changes address four specific gaps in the current CLI implementation:
1. Configure stdlib logging infrastructure in main()
2. Standardize exit codes across all command handlers
3. Eliminate silent exception swallowing by replacing bare `except Exception: pass` with logged warnings
4. Ensure unexpected errors are logged with full detail while showing concise messages to users

## Current State Analysis

The CLI currently has inconsistent error handling:
- Some commands (mark_dead, show_*, create_*) properly call `sys.exit(1)` on failure
- Others (log_*, media_*) print errors but return normally (exit code 0)
- Eleven silent exception swallowing locations exist where failures are ignored completely
- No logging infrastructure is configured, so unexpected errors leave no trace beyond user-facing messages
- Unexpected error handlers print concise messages but don't log full tracebacks for debugging

## Desired End State

After implementation, the CLI will:
- Configure stdlib logging once in main() with logger name `plant_tracking.cli`, StreamHandler to stderr, format `%(asctime)s %(levelname)s %(name)s: %(message)s`, level from PLANT_TRACKING_LOG_LEVEL env (default INFO)
- All command handlers will use `sys.exit(1)` on failure paths (including log_* and media_* commands)
- All eleven `except Exception: pass` blocks will be replaced with appropriate logging warnings
- Final `except Exception` handlers will call `logging.exception(...)` to log full tracebacks while still showing concise `✗` messages to users
- User-visible success output remains unchanged
- Stdout remains for command output only; all logs go to stderr

### Key Discoveries:
- The eleven silent exception swallowing sites are at lines: 439, 486, 605, 1276, 1573, 2042, 2111, 2187, 2292, 2357, 2514 (as noted in ticket)
- ADR-0009 already establishes the patterns to follow (mark_dead command as reference)
- Tests exist for mark_dead unexpected error handling that can be extended as patterns
- The main() function is the single point for logging configuration

## What We're NOT Doing

- Creating shared error-handling utility/decorator module (rejected in ADR-0009)
- Modifying FastAPI entrypoint (has its own exception handling and logging)
- Addressing pre-existing ruff/mypy/black findings in commands/ (separate cleanup ticket)
- Changing the user-visible success output format
- Altering the core business logic or data models

## Implementation Approach

We'll implement changes in four phases corresponding to the four gaps identified:
1. Add logging configuration to main()
2. Standardize exit codes for log_* and media_* commands
3. Replace silent exception swallowing with logged warnings
4. Add logging.exception() to final except handlers

Each phase includes both automated and manual verification steps to ensure correctness before proceeding.

---

## Phase 1: Configure Logging Infrastructure

### Overview
Configure stdlib logging once in main() function according to ADR-0009 specifications.

### Changes Required:

#### 1. commands/plant_tracking_cli.py - main() function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging configuration after `_get_db()` call and before argument parsing

```python
import logging
import os

def main():
    # Ensure directories exist for Markdown backup
    _ensure_dirs()

    # Initialize PostgreSQL if available
    db = _get_db()

    # Configure logging per ADR-0009
    logger_name = "plant_tracking.cli"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.getLevelName(os.environ.get("PLANT_TRACKING_LOG_LEVEL", "INFO")))
    
    # Only add handler if none exists to avoid duplicate logs
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
```

### Success Criteria:

#### Automated Verification:
- [x] New test passes: with PLANT_TRACKING_LOG_LEVEL unset, an unexpected exception logs to stderr via the configured handler (caplog)
- [x] No new linting errors introduced
- [x] Existing tests still pass

#### Manual Verification:
- [ ] Verify logging output format matches specification when PLANT_TRACKING_LOG_LEVEL is set
- [ ] Verify logs go to stderr, not stdout
- [ ] Verify default log level is INFO
- [ ] Verify PLANT_TRACKING_LOG_LEVEL=debug produces debug-level logs

**Implementation Notes (completed)**:
- The configuration is implemented as a `_configure_logging()` helper called from `main()` immediately after `db = _get_db()`, keeping `main()` as the single configuration point (ADR-0009) while making the setup directly testable.
- Level resolution uses `getattr(logging, level_name, logging.INFO)` instead of `logging.getLevelName(...)`, because `getLevelName` returns the input string unchanged for unrecognized values, which would make `setLevel` raise `TypeError` and crash the CLI at startup on a typo'd env value.
- A module-level `logger = logging.getLogger("plant_tracking.cli")` was added so command handlers (Phases 3-4) can log without reconfiguring.
- Red/Green verified: the 4 new `TestCLILoggingConfig` tests fail without the change and pass with it (104 total tests green; ruff 25 / mypy 12 unchanged vs baseline).

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Standardize Exit Codes for log_* and media_* Commands

### Overview
Change log_* and media_* command failure paths from `return` to `sys.exit(1)` after printing error messages, matching the behavior of other commands like mark_dead.

### Changes Required:

#### 1. commands/plant_tracking_cli.py - log_humidity function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        sys.exit(1)
```

#### 2. commands/plant_tracking_cli.py - log_water function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        sys.exit(1)
```

#### 3. commands/plant_tracking_cli.py - log_fertilizer function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        sys.exit(1)
```

#### 4. commands/plant_tracking_cli.py - log_note function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        sys.exit(1)
```

#### 5. commands/plant_tracking_cli.py - log_list function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not plant_exists:
        print(f"✗ Error: Plant ID '{args.plant_id}' not found")
        sys.exit(1)
```

#### 6. commands/plant_tracking_cli.py - media_add_attachment function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not plant_exists:
        print(f"Error: Plant ID '{args.plant_id}' not found")
        sys.exit(1)
```

#### 7. commands/plant_tracking_cli.py - media_list_attachments function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        sys.exit(1)
```

#### 8. commands/plant_tracking_cli.py - media_show_attachment function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        sys.exit(1)
```

#### 9. commands/plant_tracking_cli.py - media_delete_attachment function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        sys.exit(1)
```

#### 10. commands/plant_tracking_cli.py - media_get_url function
**File**: `commands/plant_tracking_cli.py`
**Changes**: Replace `return` with `sys.exit(1)` after error printing

```python
    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        sys.exit(1)
```

### Success Criteria:

#### Automated Verification:
- [x] New tests assert SystemExit(1) on each simulated failure path for log_* and media_* commands
- [x] No new linting errors introduced
- [x] Existing tests still pass

#### Manual Verification:
- [ ] `plant-tracking log humidity <nonexistent> --level 5; echo $?` prints the error and exits 1
- [ ] Similar verification for all log_* and media_* commands with invalid plant IDs
- [ ] User-initiated cancellations (like "Create anyway? N" in create_seed_packet) still exit 0

**Implementation Notes (completed)**:
- The 10 listed changes were applied, plus the remaining operational-error paths in the same commands that ADR-0009 §5 covers ("missing entity, validation failure, service error, or unexpected exception" → exit 1): log_water invalid amount, log_note missing file / no text / empty text, media_add file-not-found and its ValueError/except handlers, and the media show/delete/url "attachment not found" + "failed" paths. Empty-result informational messages (e.g., "No media attachments found") intentionally stay exit 0, matching list-command behavior.
- Pre-existing bug flagged (NOT fixed, out of scope): `log_water`'s Markdown fallback (commands/plant_tracking_cli.py) assigns `plant_file` but never calls `.exists()`, so in no-database mode `log water` always reports "Plant ID not found".
- Red/Green verified: 29 new tests across `TestLogCommandExitCodes`, `TestMediaCommandExitCodes`, `TestUserCancellationExitCode` — 27 fail without the change (the 2 exit-0 behavior tests pass by design), all green with it. 133 total tests pass; ruff 25 / mypy 12 unchanged vs baseline; black clean on new lines.
- Smoke-verified on the live CLI: all failure paths exit 1 (with and without DATABASE_URL), cancelled `create-seed-packet` exits 0.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Replace Silent Exception Swallowing with Logged Warnings

### Overview
Replace the eleven `except Exception: pass` blocks with appropriate logging warnings that include context about the failed operation.

### Changes Required:

#### 1. commands/plant_tracking_cli.py - create_plant function (genus lookup)
**File**: `commands/plant_tracking_cli.py`
**Line**: 439
**Changes**: Replace `except Exception: pass` with logging warning

```python
        except Exception:
            logger.warning("Genus lookup failed for variety_name=%s", plant_data.get("variety_name", "unknown"))
```

#### 2. commands/plant_tracking_cli.py - create_plant function (fuzzy genus search)
**File**: `commands/plant_tracking_cli.py`
**Line**: 486
**Changes**: Replace `except Exception: pass` with logging warning

```python
                 except Exception:
                     logger.warning("Fuzzy genus search failed for variety_name=%s", plant_data.get("variety_name", "unknown"))
```

#### 3. commands/plant_tracking_cli.py - create_plant function (seed packet lookup)
**File**: `commands/plant_tracking_cli.py`
**Line**: 605
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Seed packet lookup failed for variety_name=%s, latin_name=%s", 
                          plant_data.get("variety_name", "unknown"), 
                          plant_data.get("latin_name", "unknown"))
```

#### 4. commands/plant_tracking_cli.py - create_genus function (duplicate check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 1276
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Duplicate genus check failed for variety_name=%s, latin_name=%s", 
                          genus_data.get("variety_name", "unknown"), 
                          genus_data.get("latin_name", "unknown"))
```

#### 5. commands/plant_tracking_cli.py - create_seed_packet function (duplicate check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 1573
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Duplicate seed packet check failed for variety_name=%s, latin_name=%s", 
                          packet_data.get("variety_name", "unknown"), 
                          packet_data.get("latin_name", "unknown"))
```

#### 6. commands/plant_tracking_cli.py - log_humidity function (plant exists check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 2042
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Plant existence check failed for plant_id=%s", args.plant_id)
```

#### 7. commands/plant_tracking_cli.py - log_water function (plant exists check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 2111
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Plant existence check failed for plant_id=%s", args.plant_id)
```

#### 8. commands/plant_tracking_cli.py - log_fertilizer function (plant exists check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 2187
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Plant existence check failed for plant_id=%s", args.plant_id)
```

#### 9. commands/plant_tracking_cli.py - log_note function (plant exists check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 2292
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Plant existence check failed for plant_id=%s", args.plant_id)
```

#### 10. commands/plant_tracking_cli.py - log_list function (plant exists check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 2357
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Plant existence check failed for plant_id=%s", args.plant_id)
```

#### 11. commands/plant_tracking_cli.py - media_add_attachment function (plant exists check)
**File**: `commands/plant_tracking_cli.py`
**Line**: 2514
**Changes**: Replace `except Exception: pass` with logging warning

```python
         except Exception:
             logger.warning("Plant existence check failed for plant_id=%s", args.plant_id)
```

### Success Criteria:

#### Automated Verification:
- [x] New tests verify a warning is logged for one representative silent path per command family and that the fallback still executes
- [x] No new linting errors introduced
- [x] Existing tests still pass

#### Manual Verification:
- [ ] Verify warning logs appear when database service is unavailable but fallback paths still work
- [ ] Verify that the specific operation context is included in warning messages
- [ ] Verify that fallback behaviors (manual entry, etc.) still function correctly

**Implementation Notes (completed)**:
- All eleven `except Exception: pass` blocks replaced with `logger.warning(<operation context>, exc_info=True)` using the module-level `plant_tracking.cli` logger from Phase 1. `exc_info=True` was added beyond the plan snippets because ticket item 4 requires the warning to include the *exception context* (the actual failure), not just the operation name.
- Post-change line numbers of the eleven sites: 464 (create_plant genus lookup), 516 (create_plant fuzzy genus search), 639 (create_plant seed packet lookup), 1315 (create_seed_packet duplicate check), 1617 (create_genus duplicate check), 2091 (log_humidity), 2166 (log_water), 2248 (log_fertilizer), 2359 (log_note), 2430 (log_list), 2591 (media_add_attachment) — `except Exception: pass` count is now 0.
- Other pre-existing silent fallbacks (`_fuzzy_search_genus`, `_select_existing_packet`, `_select_existing_genus` `except Exception: return None`, and the list-command model fallbacks) were deliberately left untouched — the ticket scopes item 4 to the eleven `pass` blocks; revisit if desired.
- 6 new tests in `TestSilentPathWarnings`: one representative silent path per command family (create_plant genus lookup, create_seed_packet/create_genus duplicate checks, log_humidity, media_add) asserting warning + fallback, plus an end-to-end test proving the warning reaches stderr via the configured ADR-0009 handler. Red/Green verified (all 6 fail without the change). 139 total tests pass; ruff 25 / mypy 12 unchanged; black clean on new lines.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 4: Add Logging for Unexpected Errors

### Overview
Add `logging.exception(...)` calls to all final `except Exception` handlers to log full tracebacks while still showing concise error messages to users.

### Changes Required:

#### 1. commands/plant_tracking_cli.py - create_plant function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Error creating plant record: %s", e, exc_info=True)
         print(f"\n✗ Error creating plant record: {e}")
         sys.exit(1)
```

#### 2. commands/plant_tracking_cli.py - mark_dead function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Unexpected error marking plant as dead: %s", e, exc_info=True)
         print(f"✗ Unexpected error marking plant as dead: {e}")
         sys.exit(1)
```

#### 3. commands/plant_tracking_cli.py - create_seed_packet function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Error creating seed packet: %s", e, exc_info=True)
         print(f"\n✗ Error creating seed packet: {e}")
         sys.exit(1)
```

#### 4. commands/plant_tracking_cli.py - create_genus function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Error creating genus: %s", e, exc_info=True)
         print(f"\n✗ Error creating genus: {e}")
         sys.exit(1)
```

#### 5. commands/plant_tracking_cli.py - show_seed_packet function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Error showing seed packet: %s", e, exc_info=True)
         print(f"✗ Error showing seed packet: {e}")
         sys.exit(1)
```

#### 6. commands/plant_tracking_cli.py - show_genus function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Error showing genus: %s", e, exc_info=True)
         print(f"✗ Error showing genus: {e}")
         sys.exit(1)
```

#### 7. commands/plant_tracking_cli.py - show_plant function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before sys.exit(1) in final except block

```python
     except Exception as e:
         logger.error("Error showing plant: %s", e, exc_info=True)
         print(f"✗ Error showing plant: {e}")
         sys.exit(1)
```

#### 8. commands/plant_tracking_cli.py - log_humidity function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error: %s", e, exc_info=True)
         print(f"✗ Error: {e}")
```

#### 9. commands/plant_tracking_cli.py - log_water function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error: %s", e, exc_info=True)
         print(f"✗ Error: {e}")
```

#### 10. commands/plant_tracking_cli.py - log_fertilizer function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error: %s", e, exc_info=True)
         print(f"✗ Error: {e}")
```

#### 11. commands/plant_tracking_cli.py - log_note function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error: %s", e, exc_info=True)
         print(f"✗ Error: {e}")
```

#### 12. commands/plant_tracking_cli.py - media_add_attachment function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error creating %s attachment: %s", media_type, e, exc_info=True)
         print(f"Error creating {media_type} attachment: {e}")
```

#### 13. commands/plant_tracking_cli.py - media_list_attachments function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error listing media attachments: %s", e, exc_info=True)
         print(f"Error listing media attachments: {e}")
```

#### 14. commands/plant_tracking_cli.py - media_show_attachment function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error showing media attachment: %s", e, exc_info=True)
         print(f"Error showing media attachment: {e}")
```

#### 15. commands/plant_tracking_cli.py - media_delete_attachment function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error deleting media attachment: %s", e, exc_info=True)
         print(f"Error deleting media attachment: {e}")
```

#### 16. commands/plant_tracking_cli.py - media_get_url function (final exception handler)
**File**: `commands/plant_tracking_cli.py`
**Changes**: Add logging before printing error in final except block

```python
     except Exception as e:
         logger.error("Error getting media attachment URL: %s", e, exc_info=True)
         print(f"Error getting media attachment URL: {e}")
```

### Success Criteria:

#### Automated Verification:
- [x] Extend existing `TestMarkDeadCLI.test_unexpected_error_from_update` pattern to assert a log record with traceback for each command handler
- [x] No new linting errors introduced
- [x] Existing tests still pass
- [x] `traceback.print_exc` count remains 0 in the codebase

#### Manual Verification:
- [ ] `PLANT_TRACKING_LOG_LEVEL=debug plant-tracking mark-dead <id>` logs with traceback to stderr on a forced failure; user sees only the `✗` line
- [ ] Similar verification for other commands with forced failures
- [ ] Verify that tracebacks appear in logs but not on user's terminal

**Implementation Notes (completed)**:
- Used `logger.exception("...: %s", e)` (the ADR-0009 wording; equivalent to the plan's `logger.error(..., exc_info=True)`).
- 19 handlers instrumented: the 16 in the plan plus three additional final `except Exception` handlers the plan's list omitted but the ticket's "every final `except Exception` handler of command handlers" requires: `create_plant`'s inner uow-path handler, `mark_dead`'s check-phase handler, and `print_label`.
- Deliberately NOT logged (expected domain errors per ADR-0009 §1, or non-final fallback paths): `ValidationException`/`PlantTrackingServiceException` handlers, `_get_db`, the mid-flow create_plant fallbacks, `_create_packet_inline`/`_create_genus_inline` (re-raise to the final handler), and list-command model fallbacks.
- 18 new tests in `TestUnexpectedErrorLogging` (one per command handler, extending the `TestMarkDeadCLI` pattern): each asserts the formatted `ERROR plant_tracking.cli:` line AND `Traceback (most recent call last)` on stderr, and that stdout contains neither. Red/Green verified (18 fail without the change).
- Final counts: 157 tests pass (baseline 100); ruff 25 / mypy 12 unchanged vs baseline; black clean on new lines; bandit High issues IMPROVED 24 → 13 (Phase 3 removed the 11 B110 try/except/pass findings); `traceback.print_exc` count is 0.

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before considering the plan complete.

---

## Testing Strategy

### Unit Tests:
- Test logging configuration in main() with various PLANT_TRACKING_LOG_LEVEL values
- Test that each command handler properly logs warnings for the silent exception paths
- Test that each command handler logs full tracebacks for unexpected errors
- Test exit codes for all command handlers

### Integration Tests:
- Test end-to-end error scenarios with logging verification
- Test that logging output goes to stderr while command output goes to stdout
- Test that log levels are respected

### Manual Testing Steps:
1. Verify logging configuration works correctly with different log levels
2. Verify all command failure paths now exit with code 1
3. Verify silent exception paths now produce appropriate warning logs
4. Verify unexpected errors produce detailed logs while showing concise user messages
5. Verify user-initiated cancellations still exit with code 0
6. Verify normal successful operations still work correctly

## Performance Considerations

- Logging overhead is minimal as it's only active when errors occur or when debug logging is enabled
- No significant performance impact expected from these changes
- Logging to stderr has negligible performance impact

## Migration Notes

- No data migration required as this only affects error handling and logging
- Backward compatible for successful operations
- Behavior change for failure paths in log_* and media_* commands (now exit 1 instead of 0)
- This change is intentional and documented; users relying on exit 0 from failing commands will need to update their scripts

## References

- Original ticket: `knowledge/tickets/PROJ-0015.md`
- ADR-0009: `knowledge/architecture/decisions/ADR-0009-CLI-error-handling-and-logging-conventions.md`
- CLI implementation: `commands/plant_tracking_cli.py`
- CLI tests pattern: `tests/test_plant_tracking.py` (TestMarkDeadCLI)
- Related commits: `7fc01a2`, `805b52f`, `f4ac42e`