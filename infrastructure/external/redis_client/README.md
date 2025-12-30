infrastructure/external/redis_client
├─ __init__.py
├─ core.py                # Redis connection/pool setup (async redis client)
├─ client.py              # Facade composing all mixin repos
├─ balance_cache.py       # Cache balances
├─ market_cache.py        # Cache market data
├─ bot_status_repo.py     # Bot status flags
├─ position_repo.py       # Positions store
├─ position_layers_repo.py# Layered positions
├─ price_repo.py          # Latest/avg price cache
├─ trade_counter_repo.py  # Trade counters
├─ trade_history_repo.py  # Trade history records
├─ cost_repo.py           # Cost/PnL tracking
└─ mexc_raw_repo.py       # Persist raw MEXC payloads

心智模型（最簡）
[ Application ]
     ↓
[ RedisClient (client.py) ]
     ↓
[ Connection/Pool (core.py, hiredis 可選) ]
     ↓
[ Repos & Cache Mixins ]
     ↓
[ Redis ]
