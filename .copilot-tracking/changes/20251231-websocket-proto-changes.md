<!-- markdownlint-disable-file -->
# Release Changes: websocket protobuf helpers

**Related Plan**: none
**Implementation Date**: 2025-12-31

## Summary

Added generated Python protobuf bindings for MEXC websocket payloads, exposed a shared decoder for PushData envelopes, documented how to consume the compiled messages in the websocket client flow and docs, and defaulted websocket helpers to the shared decoder.

## Changes

### Added

- src/app/infrastructure/external/proto/__init__.py - Declares external proto package and exports websocket bindings
- src/app/infrastructure/external/proto/websocket_pb/__init__.py - Exposes compiled websocket protobuf modules
- src/app/infrastructure/external/proto/websocket_pb/*.py - Generated protobuf bindings for websocket streams (all files < 4KB, includes PushData wrapper and channel-specific messages)

### Modified

- src/app/infrastructure/external/mexc/websocket/market_streams.py - Added decode_push_data helper using generated PushData message
- src/app/infrastructure/external/mexc/ws/ws_client.py - Re-exported decode_push_data for websocket clients and defaulted binary decoding to PushData wrapper
- tests/test_ws_client.py - Covered decoding with generated PushData protobuf bindings and default decoder usage
- docs/Websocket Market Streams.md - Documented python import path, shared decoder usage, and default decoder behaviour

### Removed

- None

## Release Summary

**Total Files Affected**: 22

### Files Created (18)

- src/app/infrastructure/external/proto/__init__.py - Proto package entry point
- src/app/infrastructure/external/proto/websocket_pb/__init__.py - Websocket protobuf package
- src/app/infrastructure/external/proto/websocket_pb/PrivateAccountV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PrivateDealsV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PrivateOrdersV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicAggreBookTickerV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicAggreDealsV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicAggreDepthsV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicBookTickerBatchV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicBookTickerV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicDealsV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicIncreaseDepthsBatchV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicIncreaseDepthsV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicLimitDepthsV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicMiniTickerV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicMiniTickersV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PublicSpotKlineV3Api_pb2.py - Compiled websocket message
- src/app/infrastructure/external/proto/websocket_pb/PushDataV3ApiWrapper_pb2.py - Compiled PushData envelope (size reduced <4KB)

### Files Modified (4)

- src/app/infrastructure/external/mexc/websocket/market_streams.py - Added push-data decoder
- src/app/infrastructure/external/mexc/ws/ws_client.py - Re-exported decoder helper and defaulted binary decoding to PushData wrapper
- tests/test_ws_client.py - Added protobuf decoding test and coverage for default decoder usage
- docs/Websocket Market Streams.md - Updated usage instructions and default decoder note

### Files Removed (0)

- None

### Dependencies & Infrastructure

- **New Dependencies**: none (used system protoc for generation)
- **Updated Dependencies**: none
- **Infrastructure Changes**: Added generated protobuf bindings to codebase
- **Configuration Updates**: none

### Deployment Notes

No runtime configuration changes required; websocket clients can rely on the default `decode_push_data` binary decoder to parse protobuf frames.
