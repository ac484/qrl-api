services/
└─ trading/
   ├─ __init__.py

   # ===== Orchestrator =====
   ├─ trading_service.py              # 對外 Facade（HTTP / Job 呼叫）
   ├─ trading_workflow.py             # 6-phase 流程（純流程）

   # ===== Use Cases =====
   ├─ execute_trade_usecase.py        # 自動交易一次
   ├─ manual_trade_usecase.py         # 手動交易
   ├─ bot_control_usecase.py          # start / stop / status

   # ===== Domain Coordinators =====
   ├─ balance_resolver.py             # 取得 USDT（API + cache fallback）
   ├─ price_resolver.py               # current price + history 補齊
   ├─ position_updater.py             # BUY / SELL 後 position 更新

   # ===== Domain Services（已存在）=====
   ├─ strategy_service.py
   ├─ risk_service.py
   ├─ position_service.py

   # ===== Repository Facade =====
   └─ repository_service.py            # 聚合 position / price / trade / cost

services/
└─ market/
   ├─ __init__.py

   # ===== Facade =====
   ├─ market_service.py              # 對外唯一入口

   # ===== Use Cases =====
   ├─ get_market_snapshot.py         # ticker + price
   ├─ get_orderbook_usecase.py
   ├─ get_trades_usecase.py
   ├─ get_klines_usecase.py
   ├─ update_price_cache_usecase.py

   # ===== Domain Helpers =====
   ├─ price_resolver.py              # current price / fallback
   ├─ price_history_manager.py       # add / statistics
   ├─ cache_strategy.py              # cache-first / ttl 決策

   # ===== Infra Glue =====
   ├─ mexc_client_service.py         # 封裝 mexc client
   ├─ price_repo_service.py          # Redis price repo
   ├─ cache_service.py               # Redis cache facade
   └─ cache_policy.py                # TTL（已存在）
