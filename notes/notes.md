Results: 51/52 tests passing (1 pre-existing test_label_dimensions failure unrelated to these changes)
Phase	Status	Details
1: Seed Packet Model	Done	commands/seed_packet_model.py + 13 tests in tests/test_seed_packet.py
2: Plant Model Reference	Done	Added seed_packet_id to ALL_FIELDS, get_seed_packet(), load_seed_packet()
3: CLI Standalone Commands	Done	create-seed-packet, list-seed-packets, show-seed-packet + 6 tests
4: Create-Plant Flow	Done	Three-phase prompt with packet lookup + 4 tests
5: Migration Script	Done	scripts/migrate_seed_packets.py with --dry-run; 4 packets created, 15 plants updated
6: Integration Tests	Done	TestEndToEnd class with 4 e2e tests
7: Documentation	Done	Updated docs/user.md (seed packet concepts, 3 new commands, revised flow) and knowledge/specs/database.md (seed packet schema, relationship docs, examples)



Summary of the implementation approach:
1. Format Abstraction Layer: Created a new label_format.py module to define label specifications and handle format conversions
2. Label Generator Updates: Modified label_generator.py to accept format parameters and generate appropriate dimensions for both 40x30mm (landscape) and 50x70mm (portrait) formats
3. Print Command Updates: Enhanced printer.py to:
   - Accept format and --no-print parameters
   - Pass correct CUPS media options based on format (w40h30 for 40x30mm, w50h70 for 50x70mm)
   - Support image-only generation when --no-print is specified
4. CLI Consolidation: Updated plant_tracking_cli.py to:
   - Remove the separate create-label command
   - Enhance the print-label command with --format and --no-print options
   - Maintain backward compatibility with 40x30mm as default format
5. Test Updates: Added comprehensive tests for the new functionality while preserving existing test coverage
Key Features Implemented:
- Support for both 40x30mm (existing) and 50x70mm (new) label formats
- Proper orientation handling for 50x70mm (longer dimension along roll direction)
- Consolidation of create-label and print-label into a single command
- --no-print flag for image-only generation
- Backward compatibility - existing 40x30mm workflow unchanged
- Future-proof design for easy addition of more formats
Please review the implementation plan and let me know if you have any questions, need adjustments, or if you'd like me to proceed with implementation. The plan follows the established structure with clear phases, success criteria, and testing strategy.
