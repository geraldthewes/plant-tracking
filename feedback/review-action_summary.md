# Review Action Summary

Restored:   13
Processed:  27
Committed:  1
Skipped:    24
Errors:     2
Interrupted: no
Progress: 27 out of 69 findings processed

## Findings

| Finding | File | Outcome | Commit | What was done |
|---------|------|---------|--------|---------------|
| [01205db9-176](./01205db9-176.md) | (unparseable) | Skipped | — | Cannot parse action from 01205db9-176.md (no code blocks) |
| [01205db9-179](./01205db9-179.md) | (unparseable) | Skipped | — | Cannot parse action from 01205db9-179.md (no code blocks) |
| [01205db9-180](./01205db9-180.md) | (unparseable) | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [076b557b-161](./076b557b-161.md) | packages/plant_service/src/plant_service/service_layer/unit_of_work.py | Fixed | `5b4b49b8` | Fix applied and committed: fix: The `__exit__` method is missing type hints for it... [076b557b-161] |
| [076b557b-162](./076b557b-162.md) | packages/plant_service/src/plant_service/service_layer/unit_of_work.py | Error | — | Fix failed after 6 attempts: Failed to apply fix for packages/plant_service/src/plant_service/service_layer/unit_of_work.py after 6 attempts: Agent.apply_fix returned False |
| [0ccd4f32-165](./0ccd4f32-165.md) | packages/plant_service/tests/integration/test_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [0ccd4f32-168](./0ccd4f32-168.md) | packages/plant_service/tests/integration/test_repository.py | Fixed | `458ee92f` | Fix applied and committed: fix: The test uses a hardcoded plant_id 'YEHA-2026-001'... [0ccd4f32-168] |
| [2b44b4db-153](./2b44b4db-153.md) | (unparseable) | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [2b44b4db-154](./2b44b4db-154.md) | packages/plant_service/src/plant_service/service_layer/genus_service.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [30551c57-121](./30551c57-121.md) | packages/plant_service/src/plant_service/adapters/repository/genus_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [30551c57-122](./30551c57-122.md) | packages/plant_service/src/plant_service/adapters/repository/genus_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [30551c57-124](./30551c57-124.md) | packages/plant_service/src/plant_service/adapters/repository/genus_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [4a9a5fe7-171](./4a9a5fe7-171.md) | packages/plant_service/tests/unit/test_genus_model.py | Error | — | Fix failed after 6 attempts: Failed to apply fix for packages/plant_service/tests/unit/test_genus_model.py after 6 attempts: Agent.apply_fix returned False |
| [4a9a5fe7-22](./4a9a5fe7-22.md) | (unparseable) | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [4c6ddee4-144](./4c6ddee4-144.md) | packages/plant_service/src/plant_service/domain/genus.py | Fixed | `95628505` | Fix applied and committed: fix: Consider moving the regex pattern to a class-level... [4c6ddee4-144] |
| [4c6ddee4-145](./4c6ddee4-145.md) | packages/plant_service/src/plant_service/domain/genus.py | Fixed | `e7894ba8` | Fix applied and committed: fix: Consider making generate_id a static method since ... [4c6ddee4-145] |
| [4c6ddee4-147](./4c6ddee4-147.md) | packages/plant_service/src/plant_service/domain/genus.py | Fixed | `241c4416` | Fix applied and committed: fix: The docstring claims to preserve the logic from co... [4c6ddee4-147] |
| [4c6ddee4-19](./4c6ddee4-19.md) | (unparseable) | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [79e7c26c-151](./79e7c26c-151.md) | packages/plant_service/src/plant_service/domain/utils.py | Fixed | `0e2360d1` | Fix applied and committed: fix: The unit string may contain multiple spaces (e.g.,... [79e7c26c-151] |
| [79e7c26c-152](./79e7c26c-152.md) | packages/plant_service/src/plant_service/domain/utils.py | Fixed | `0e2360d1` | Duplicate of finding 79e7c26c-151 (same unit-whitespace-normalization bug) — already fixed by commit 0e2360d1. No separate action needed. |
| [801ba076-20](./801ba076-20.md) | (unparseable) | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [80dfb20a-148](./80dfb20a-148.md) | packages/plant_service/src/plant_service/domain/seed_packet.py | Fixed | `1b09ad95` | Fix applied and committed: fix: The create_from_dict method validates required fie... [80dfb20a-148] |
| [80dfb20a-149](./80dfb20a-149.md) | packages/plant_service/src/plant_service/domain/seed_packet.py | Fixed | `b654465b` | Fix applied and committed: fix: The regex pattern in find_next_sequence is compile... [80dfb20a-149] |
| [80dfb20a-150](./80dfb20a-150.md) | packages/plant_service/src/plant_service/domain/seed_packet.py | Fixed | `725ce9cf` | Fix applied and committed: fix: The generate_id method uses format 'SPKT-{seq:03d}... [80dfb20a-150] |
| [82214597-127](./82214597-127.md) | packages/plant_service/src/plant_service/adapters/repository/log_repository.py | Fixed | `503ac022` | Fix applied and committed: fix: The list_entries method orders log entries by time... [82214597-127] |
| [8adf07ee-142](./8adf07ee-142.md) | (unparseable) | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [8adf07ee-143](./8adf07ee-143.md) | packages/plant_service/src/plant_service/bootstrap.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [8bff246e-130](./8bff246e-130.md) | packages/plant_service/src/plant_service/adapters/repository/models/media_attachment_model.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [9cefd6bc-141](./9cefd6bc-141.md) | (unparseable) | Skipped | — | Cannot parse action from 9cefd6bc-141.md (no code blocks) |
| [9de7f0c6-181](./9de7f0c6-181.md) | packages/plant_service/tests/unit/test_utils.py | Fixed | `5dda62ce` | Fix applied and committed: fix: The test for liters only checks the value_ml field... [9de7f0c6-181] |
| [9de7f0c6-182](./9de7f0c6-182.md) | packages/plant_service/tests/unit/test_utils.py | Fixed | `5dda62ce` | Duplicate of finding 9de7f0c6-181 (same test_utils.py display_value/display_unit assertion gap) — already fixed by commit 5dda62ce. No separate action needed. |
| [9de7f0c6-183](./9de7f0c6-183.md) | packages/plant_service/tests/unit/test_utils.py | Fixed | `5dda62ce` | Same display_value/display_unit assertion gap as finding 9de7f0c6-181/182 (cups vs liters) — already fixed by commit 5dda62ce. No separate action needed. |
| [a1d1cbba-170](./a1d1cbba-170.md) | (unparseable) | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [a1d1cbba-172](./a1d1cbba-172.md) | (unparseable) | Skipped | — | Cannot parse action from a1d1cbba-172.md (no code blocks) |
| [a1d1cbba-173](./a1d1cbba-173.md) | (unparseable) | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [a1d1cbba-174](./a1d1cbba-174.md) | (unparseable) | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [c26a6622-128](./c26a6622-128.md) | packages/plant_service/src/plant_service/adapters/repository/media_attachment_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [c26a6622-129](./c26a6622-129.md) | packages/plant_service/src/plant_service/adapters/repository/media_attachment_repository.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [c60317e7-18](./c60317e7-18.md) | (unparseable) | Rejected (REJECTED) | — | Verdict REJECTED — not actioned |
| [c67eab30-123](./c67eab30-123.md) | packages/plant_service/src/plant_service/adapters/repository/base.py | Rejected (BACKLOG) | — | Verdict BACKLOG — not actioned |
| [c67eab30-125](./c67eab30-125.md) | packages/plant_service/src/plant_service/adapters/repository/base.py | Not processed | — | — |
| [c67eab30-126](./c67eab30-126.md) | packages/plant_service/src/plant_service/adapters/repository/base.py | Error | — | Quality checks failed after 3 iteration(s): Quality checks failed after 3 iteration(s) for packages/plant_service/src/plant_service/adapters/repository/base.py: ## Style rule violations |
| [cbea0de4-131](./cbea0de4-131.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Fixed | `a0384964` | Fix applied and committed: fix: In create_plant method, direct access to plant_dat... [cbea0de4-131] |
| [cbea0de4-132](./cbea0de4-132.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Not processed | — | — |
| [cbea0de4-133](./cbea0de4-133.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Not processed | — | — |
| [cbea0de4-134](./cbea0de4-134.md) | packages/plant_service/src/plant_service/adapters/repository/plant_repository.py | Not processed | — | — |
| [cc25be50-175](./cc25be50-175.md) | packages/plant_service/tests/unit/test_seed_packet_model.py | Fixed | `85bba1d7` | Fix applied and committed: fix: In the test for valid data, we should also assert ... [cc25be50-175] |
| [cc25be50-177](./cc25be50-177.md) | packages/plant_service/tests/unit/test_seed_packet_model.py | Fixed | `2ae20a32` | Fix applied and committed: fix: In the test for valid data, we should also assert ... [cc25be50-177] |
| [cc25be50-178](./cc25be50-178.md) | packages/plant_service/tests/unit/test_seed_packet_model.py | Fixed | `4a0e0245` | Fix applied and committed: fix: We should also test that a missing 'variety_name' ... [cc25be50-178] |
| [cddec94d-155](./cddec94d-155.md) | packages/plant_service/src/plant_service/service_layer/export_service.py | Not processed | — | — |
| [cddec94d-156](./cddec94d-156.md) | packages/plant_service/src/plant_service/service_layer/export_service.py | Fixed | `7d47eecc` | Fix applied and committed: fix: The export_to_markdown method claims to export 'al... [cddec94d-156] |
| [cddec94d-157](./cddec94d-157.md) | packages/plant_service/src/plant_service/service_layer/export_service.py | Fixed | `5cd6b221` | Fix applied and committed: fix: The _write_markdown_file method writes field value... [cddec94d-157] |
| [d30f3ff2-146](./d30f3ff2-146.md) | (unparseable) | Skipped | — | Cannot parse action from d30f3ff2-146.md (no code blocks) |
| [e53b81c9-163](./e53b81c9-163.md) | (unparseable) | Not processed | — | — |
| [e53b81c9-164](./e53b81c9-164.md) | packages/plant_service/tests/unit/test_exceptions.py | Not processed | — | — |
| [e53b81c9-166](./e53b81c9-166.md) | packages/plant_service/tests/unit/test_exceptions.py | Not processed | — | — |
| [e53b81c9-167](./e53b81c9-167.md) | packages/plant_service/tests/unit/test_exceptions.py | Not processed | — | — |
| [e53b81c9-169](./e53b81c9-169.md) | packages/plant_service/tests/unit/test_exceptions.py | Not processed | — | — |
| [eedcebe3-158](./eedcebe3-158.md) | packages/plant_service/src/plant_service/service_layer/s3_service.py | Fixed | `63cddae0` | Fix applied and committed: fix: The S3Service class directly instantiates a boto3 ... [eedcebe3-158] |
| [eedcebe3-159](./eedcebe3-159.md) | packages/plant_service/src/plant_service/service_layer/s3_service.py | Error | — | Fix failed after 6 attempts: Failed to apply fix for packages/plant_service/src/plant_service/service_layer/s3_service.py after 6 attempts: Agent.apply_fix returned False |
| [eedcebe3-160](./eedcebe3-160.md) | packages/plant_service/src/plant_service/service_layer/s3_service.py | Fixed | `85ef21e1` | Fix applied and committed: fix: Missing type hint for fileobj parameter in upload_... [eedcebe3-160] |
| [f6e1b676-135](./f6e1b676-135.md) | (unparseable) | Not processed | — | — |
| [f6e1b676-136](./f6e1b676-136.md) | (unparseable) | Not processed | — | — |
| [f6e1b676-137](./f6e1b676-137.md) | (unparseable) | Not processed | — | — |
| [f7b438c7-21](./f7b438c7-21.md) | (unparseable) | Not processed | — | — |
| [fe2c3ff6-138](./fe2c3ff6-138.md) | (unparseable) | Skipped | — | Cannot parse action from fe2c3ff6-138.md (no code blocks) |
| [fe2c3ff6-139](./fe2c3ff6-139.md) | (unparseable) | Not processed | — | — |
| [fe2c3ff6-140](./fe2c3ff6-140.md) | (unparseable) | Not processed | — | — |
| [test_simple](./test_simple.md) | test.py | Fixed | `0409f009` | Fix applied and committed: fix: The `__exit__` method is missing type hints for it... [test_simple] |
