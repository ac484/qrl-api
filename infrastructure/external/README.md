infrastructure/
└─ external/
   └─ redis_client/
      ├─ __init__.py

      # ===== Connection / Base =====
      ├─ core.py                  # Redis connection, pool, health_check
      ├─ client.py                # Facade / 聚合所有 repos

      # ===== Cache Mixins（已存在）=====
      ├─ balance_cache.py         # BalanceCacheMixin
      ├─ market_cache.py          # MarketCacheMixin

      # ===== Domain Repositories =====
      ├─ bot_status_repo.py       # bot status (running / paused / error)
      ├─ position_repo.py         # position (balance, avg_cost...)
      ├─ position_layers_repo.py  # core / swing / active
      ├─ price_repo.py            # latest / cached / history price
      ├─ trade_counter_repo.py    # daily trades / last trade time
      ├─ trade_history_repo.py    # trade records
      ├─ cost_repo.py             # avg cost / pnl
      └─ mexc_raw_repo.py         # raw MEXC API responses


infrastructure/
└─ external/
   └─ mexc_client/
      ├─ __init__.py

      # ===== Core / Transport Layer =====
      ├─ core.py                  # httpx client lifecycle, headers, retry, _request
      ├─ client.py                # Facade / 對外唯一入口

      # ===== Auth / Signing =====
      ├─ signer.py                # HMAC SHA256 signature (_generate_signature)

      # ===== Account Domain =====
      ├─ account.py               # account info, balance, snapshot helpers

      # ===== Market Domain =====
      ├─ market_endpoints.py      # public market endpoints (ticker, klines, etc.)

      # ===== Trading Domain =====
      ├─ trade_repo.py            # create/cancel/get orders, trades

      # ===== Sub-Account Domain =====
      ├─ sub_account_spot_repo.py     # Spot API sub-account methods
      ├─ sub_account_broker_repo.py   # Broker API sub-account methods
      └─ sub_account_facade.py        # unified get_sub_accounts / get_balance
