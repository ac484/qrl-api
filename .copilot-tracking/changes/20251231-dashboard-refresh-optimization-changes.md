<!-- markdownlint-disable-file -->
# Release Changes: dashboard refresh optimization

**Related Plan**: N/A  
**Implementation Date**: 2025-12-31

## Summary

Removed the dashboard's 30-second auto-refresh loop to cut down repeated REST calls, relying on manual refresh and WebSocket-driven updates instead.

## Changes

### Added

- None

### Modified

- src/app/interfaces/templates/static/js/refresh.js - removed interval-based auto-refresh helper
- src/app/interfaces/templates/static/js/pages/dashboard/handlers.js - stopped initializing auto refresh on dashboard load
- src/app/interfaces/templates/static/js/pages/dashboard/refresh.js - dropped unused startAutoRefresh re-export
- src/app/interfaces/templates/dashboard.html - updated copy to describe manual/WebSocket updates

### Removed

- None

## Release Summary

**Total Files Affected**: 4

### Files Created (0)

- None

### Files Modified (4)

- src/app/interfaces/templates/static/js/refresh.js - removed polling interval helper
- src/app/interfaces/templates/static/js/pages/dashboard/handlers.js - no longer starts auto refresh
- src/app/interfaces/templates/static/js/pages/dashboard/refresh.js - streamlined exports to refreshAll only
- src/app/interfaces/templates/dashboard.html - revised hint to reflect manual refresh + WebSocket updates

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: None
- **Updated Dependencies**: None
- **Infrastructure Changes**: None
- **Configuration Updates**: None

### Deployment Notes

No special deployment steps; deploy updated static assets with the service.
