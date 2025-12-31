<!-- markdownlint-disable-file -->
# Release Changes: Copilot config optimization

**Related Plan**: Software-Planning-Tool session 2025-12-31  
**Implementation Date**: 2025-12-31

## Summary

Aligned Copilot agent configuration with documented instruction and prompt precedence, removing unused manual artifacts and clarifying supported context locations.

## Changes

### Added

- None

### Modified

- .github/copilot-instructions.md - Added context on supported Copilot instruction and prompt locations to guide agents and avoid legacy folders.

### Removed

- .github/.copilot/copilot-instructions.md - Removed unused legacy Copilot instruction file not consumed by agent tasks.
- .github/copilot-instructions.png - Removed manual image asset not read by Copilot agents.

## Release Summary

**Total Files Affected**: 3

### Files Created (0)

- None

### Files Modified (1)

- .github/copilot-instructions.md - Clarified official Copilot context sources.

### Files Removed (2)

- .github/.copilot/copilot-instructions.md - Legacy manual instruction file.
- .github/copilot-instructions.png - Manual image asset.

### Dependencies & Infrastructure

- **New Dependencies**: None
- **Updated Dependencies**: None
- **Infrastructure Changes**: None
- **Configuration Updates**: None

### Deployment Notes

No deployment actions required; repository-only Copilot configuration cleanup.
