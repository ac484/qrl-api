<!-- markdownlint-disable-file -->
# Release Changes: Supabase infrastructure verification

**Related Plan**: (none)
**Implementation Date**: 2025-12-31

## Summary
Aligned Supabase settings schema configuration with environment expectations and expanded Supabase infrastructure tests to confirm optional, usable behavior.

## Changes

### Added

- tests/test_supabase_infra.py - Covered schema env mapping and EventLogger fallback behavior.

### Modified

- src/app/infrastructure/supabase/config.py - Added legacy SUPABASE_SCHEMA support while preserving default and existing configuration handling, now cached via shared constants.

### Removed

- None

## Release Summary

**Total Files Affected**: 2

### Files Created (1)

- .copilot-tracking/changes/20251231-supabase-infra-changes.md - Change log for Supabase infra verification.

### Files Modified (2)

- src/app/infrastructure/supabase/config.py - Supabase settings schema handling adjusted for legacy env support with cached dotenv lookup.
- tests/test_supabase_infra.py - Tests extended for schema env mapping and EventLogger fallback.

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: None
- **Updated Dependencies**: None
- **Infrastructure Changes**: None
- **Configuration Updates**: Added backward-compatible support for SUPABASE_SCHEMA env variable.

### Deployment Notes

Run targeted Supabase tests with `pytest tests/test_supabase_infra.py` to verify configuration behavior.
