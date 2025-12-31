<!-- markdownlint-disable-file -->
# Release Changes: MEXC websocket docs refresh

**Related Plan**: N/A  
**Implementation Date**: 2025-12-31

## Summary

- Updated market and user data websocket docs with connection limits, heartbeat guidance, and protobuf decoding instructions aligned to in-repo helpers and official schema sources.

## Changes

### Added

- None

### Modified

- docs/Websocket Market Streams.md - Added connection basics and refreshed protobuf integration steps with default decoder guidance.
- docs/Websocket User Data Streams.md - Clarified listenKey lifecycle, heartbeat limits, default private channels, and protobuf decoder usage.

### Removed

- None

## Release Summary

**Total Files Affected**: 2

### Files Created (0)

- None

### Files Modified (2)

- docs/Websocket Market Streams.md - Documented connection rules and protobuf decoder usage.
- docs/Websocket User Data Streams.md - Documented listenKey limits, heartbeat expectations, and protobuf decoder usage.

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: None
- **Updated Dependencies**: None
- **Infrastructure Changes**: Installed test deps locally to run pytest.
- **Configuration Updates**: None

### Deployment Notes

- Docs-only change; no runtime deployment required. Targeted test: `python -m pytest tests/test_ws_client.py`.
