---
date: 2026-04-27T00:00:00Z
researcher: opencode
git_commit: 7935f1714440744f4f12afff49604625fd01da70
branch: main
repository: plant-tracking
topic: "Handle different print formats"
tags: [research, codebase, label-generation, printing, PROJ-0004]
status: complete
last_updated: 2026-04-27
last_updated_by: opencode

# Research: Handle different print formats

**Date**: 2026-04-27T00:00:00Z
**Researcher**: opencode
**Git Commit**: 7935f1714440744f4f12afff49604625fd01da70
**Branch**: main
**Repository**: plant-tracking

## Research Question
Based on @knowledge/tickets/PROJ-0004.md: How to implement support for different print formats (specifically 50x70mm) while preserving existing 40x30mm behavior, consolidating create-label and print-label commands, and adding a --no-print flag?

## Summary
The current implementation hardcodes label dimensions at 40x30mm across multiple locations in the codebase. To support 50x70mm labels with different orientation (longer dimension along roll direction), we need to parameterize the format handling while preserving existing functionality. The research reveals that format is hardcoded in label generation (pixel dimensions, layout), print command (CUPS media option), tests, and CUPS drivers. The solution involves creating a format abstraction that can be passed through the call chain while maintaining backward compatibility.

## Detailed Findings

### Label Generation Analysis
From `commands/label_generator.py`:
- Dimensions defined as constants: `LABEL_WIDTH_MM=40`, `LABEL_HEIGHT_MM=30`, `DPI=203`
- Pixel calculations: `LABEL_WIDTH_PX=320`, `LABEL_HEIGHT_PX=236`
- Layout assumes landscape orientation with text on left (100px column) and QR on right
- Image saved with DPI metadata for physical size interpretation

### Printing Pipeline Analysis
From `commands/printer.py`:
- Discovers USB Phomemo printers and selects model
- For plant ID input: generates label then prints; for file path: prints directly
- Format passed to printer via CUPS `lp` command: `-o media=w40h30`
- Queue name derived from printer model (M02, M110, M120/M220)

### Hardcoded Format Locations
1. **Label generation** (`commands/label_generator.py:9-14`): Width/height/DPI constants
2. **Print command** (`commands/printer.py:147`): `media=w40h30` CUPS option
3. **Test assertions** (`tests/test_plant_tracking.py:387-388`): Expected dimensions
4. **CUPS drivers**: Already define `w50h70` media types but app doesn't use them
5. **Print filter** (`phomemo-tools/tools/phomemo-filter.py:69`): Fixed 384-dot width

## Code References
- `commands/label_generator.py:9-14` - Label dimension constants
- `commands/label_generator.py:80` - Canvas creation using constants
- `commands/label_generator.py:90-108` - Layout logic assuming landscape orientation
- `commands/printer.py:147` - CUPS media option passed to lp command
- `tests/test_plant_tracking.py:387-388` - Test assertions for 40x30mm dimensions
- `phomemo-tools/cups/drv/phomemo-m110.drv:22,56` - CUPS media definitions
- `phomemo-tools/cups/drv/phomemo-m421.drv:13,65` - CUPS media definitions
- `phomemo-tools/tools/phomemo-filter.py:69` - Fixed width in print filter

## Architecture Insights
- **Single source of truth**: Label dimensions originate from three constants in label_generator.py
- **Implicit orientation**: Layout assumes landscape (width > height) with no runtime configuration
- **CUPS integration**: Format communicated via `media=` option matching PPD definitions
- **Test mismatch**: Tests use 300 DPI expectation vs actual 203 DPI implementation
- **Forward compatibility**: CUPS drivers already support w50h70 media types

## Historical Context (from knowledge/)
- `knowledge/plans/2026-04-22-PROJ-0001-create-plant-and-print-label.md`: Documents original 40x30mm implementation
- `knowledge/tickets/PROJ-0001.md`: Original label implementation specifications
- `knowledge/tickets/PROJ-0004.md`: Current requirements for format handling

## Related Research
- No existing research documents found for multi-format label support

## Open Questions
1. How should format selection be exposed to users? (CLI flag, config, environment)
2. Should the layout be swapped for portrait orientation (50x70mm) or keep same orientation?
3. How to handle the print filter's fixed width for different label sizes?
4. Should we maintain separate create-label/print-label commands or fully consolidate?
5. What default format should be used when none specified (preserve 40x30mm for backward compatibility)?