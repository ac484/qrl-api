# Code Duplication Analysis Report

## Summary

- **Total Files Analyzed**: 226
- **Total Lines of Code**: 7,131
- **Duplicate Lines**: 406
- **Duplication Percentage**: 5.7%
- **Duplicate Blocks Found**: 132
- **Duplicate Function Signatures**: 8

## Duplicate Code Blocks

### Block 1 - 12 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 16-27)
- **File 2**: `app/application/market/sync_price.py` (lines 16-27)
- **Similarity**: 100%

### Block 2 - 12 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 16-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 19-30)
- **Similarity**: 100%

### Block 3 - 12 lines

- **File 1**: `app/application/market/sync_price.py` (lines 16-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 19-30)
- **Similarity**: 100%

### Block 4 - 11 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 17-27)
- **File 2**: `app/application/market/sync_price.py` (lines 17-27)
- **Similarity**: 100%

### Block 5 - 11 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 17-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 20-30)
- **Similarity**: 100%

### Block 6 - 11 lines

- **File 1**: `app/application/market/sync_price.py` (lines 17-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 20-30)
- **Similarity**: 100%

### Block 7 - 11 lines

- **File 1**: `app/infrastructure/external/mexc/ws/ws_client.py` (lines 11-21)
- **File 2**: `app/infrastructure/exchange/mexc/ws/handlers.py` (lines 5-15)
- **Similarity**: 100%

### Block 8 - 10 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 18-27)
- **File 2**: `app/application/market/sync_price.py` (lines 18-27)
- **Similarity**: 100%

### Block 9 - 10 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 18-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 21-30)
- **Similarity**: 100%

### Block 10 - 10 lines

- **File 1**: `app/application/market/sync_price.py` (lines 18-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 21-30)
- **Similarity**: 100%

### Block 11 - 10 lines

- **File 1**: `app/infrastructure/external/mexc/ws/ws_client.py` (lines 12-21)
- **File 2**: `app/infrastructure/exchange/mexc/ws/handlers.py` (lines 6-15)
- **Similarity**: 100%

### Block 12 - 9 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 19-27)
- **File 2**: `app/application/market/sync_price.py` (lines 19-27)
- **Similarity**: 100%

### Block 13 - 9 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 19-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 22-30)
- **Similarity**: 100%

### Block 14 - 9 lines

- **File 1**: `app/application/market/sync_price.py` (lines 19-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 22-30)
- **Similarity**: 100%

### Block 15 - 9 lines

- **File 1**: `app/infrastructure/external/mexc/ws/ws_client.py` (lines 13-21)
- **File 2**: `app/infrastructure/exchange/mexc/ws/handlers.py` (lines 7-15)
- **Similarity**: 100%

### Block 16 - 9 lines

- **File 1**: `app/infrastructure/persistence/repos/account/cost_calculator.py` (lines 47-55)
- **File 2**: `app/infrastructure/persistence/repos/account/cost_repository_core.py` (lines 45-53)
- **Similarity**: 100%

### Block 17 - 8 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 20-27)
- **File 2**: `app/application/market/sync_price.py` (lines 20-27)
- **Similarity**: 100%

### Block 18 - 8 lines

- **File 1**: `app/application/market/sync_cost.py` (lines 20-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 23-30)
- **Similarity**: 100%

### Block 19 - 8 lines

- **File 1**: `app/application/market/sync_price.py` (lines 20-27)
- **File 2**: `app/application/account/sync_balance.py` (lines 23-30)
- **Similarity**: 100%

### Block 20 - 8 lines

- **File 1**: `app/application/account/list_orders.py` (lines 31-38)
- **File 2**: `app/infrastructure/exchange/mexc/http/account/list_orders.py` (lines 14-21)
- **Similarity**: 100%


## Duplicate Function Signatures

### `_get_mexc_client()`

- `app/interfaces/http/sub_account.py:13`
- `app/interfaces/http/market.py:17`
- `app/interfaces/http/account.py:23`

### `_require_scheduler_auth(x_cloudscheduler, authorization)`

- `app/application/market/sync_cost.py:16`
- `app/application/market/sync_price.py:16`
- `app/application/account/sync_balance.py:19`

### `__init__(self)`

- `app/application/trading/services/market/cache_service.py:12`
- `app/application/trading/services/market/price_repo_service.py:12`
- `app/application/trading/services/market/mexc_client_service.py:12`
- `app/application/trading/services/trading/strategy_service.py:13`
- `app/application/trading/services/trading/repository_service.py:12`
- `app/application/trading/services/trading/risk_service.py:12`
- `app/application/trading/services/trading/position_service.py:12`
- `app/infrastructure/persistence/redis/client.py:45`

### `__init__(self, mexc_client, price_repo)`

- `app/application/trading/services/market/price_resolver.py:6`
- `app/application/trading/services/trading/price_resolver.py:8`

### `__init__(self, redis_client)`

- `app/infrastructure/utils/redis_data_manager.py:15`
- `app/infrastructure/persistence/repos/market/price_repository_core.py:17`
- `app/infrastructure/persistence/repos/trade/trade_repository_core.py:18`
- `app/infrastructure/persistence/repos/account/position_repository_core.py:17`
- `app/infrastructure/persistence/repos/account/cost_repository_core.py:23`

### `decorator(func)`

- `app/infrastructure/utils/decorators.py:17`
- `app/infrastructure/utils/decorators.py:34`
- `app/infrastructure/utils/decorators.py:53`

### `_redis_client(self)`

- `app/infrastructure/persistence/redis/cache/balance.py:16`
- `app/infrastructure/persistence/redis/cache/market.py:18`
- `app/infrastructure/persistence/redis/repos/trade_counter.py:10`
- `app/infrastructure/persistence/redis/repos/cost.py:9`
- `app/infrastructure/persistence/redis/repos/position_layers.py:10`
- `app/infrastructure/persistence/redis/repos/mexc_raw.py:8`
- `app/infrastructure/persistence/redis/repos/position.py:10`
- `app/infrastructure/persistence/redis/repos/price.py:11`
- `app/infrastructure/persistence/redis/repos/bot_status.py:11`
- `app/infrastructure/persistence/redis/repos/trade_history.py:10`

### `generate_signal(self, price, short_prices, long_prices, avg_cost)`

- `app/domain/strategies/trading_strategy.py:30`
- `app/domain/strategies/base.py:11`


## Common Patterns

- **src.app imports**: 183 occurrences
- **try-except blocks**: 103 occurrences
- **validation checks**: 94 occurrences