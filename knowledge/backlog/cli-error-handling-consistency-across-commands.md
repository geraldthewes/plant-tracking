# CLI Error Handling Consistency

- severity: medium
- created: 2026-08-12
- source: code review, commands/plant_tracking_cli.py:843-846

## Problem

The `mark_dead` handler introduces `traceback.print_exc()` into its broad `except Exception` catch-all, which dumps raw stack traces to stdout. The 3-tier exception pattern (ValidationException → PlantTrackingServiceException → Exception) already exists in the plant creation handler but other functions (log_humidity, log_fertilizer) use inconsistent 2-tier patterns without sys.exit. No single error handling convention is enforced across the CLI.

## Recommendation

Standardize error handling across all CLI commands: remove `traceback.print_exc()` from mark_dead for consistency with the creation handler, and establish a single pattern for the broad `except Exception` fallback across all command handlers.

## Related

- commands/plant_tracking_cli.py:843-846 (mark_dead)
- commands/plant_tracking_cli.py:658-670 (plant creation handler)
