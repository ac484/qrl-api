services/
└─ trading/
   ├─ __init__.py
   ├─ trading_service.py        # 核心入口：协调交易流程，类似你现在的 TradingService 类
   ├─ strategy_service.py       # 处理策略逻辑（MA crossover、成本判断等）
   ├─ risk_service.py           # 风控逻辑（每日限制、仓位层、USDT余额检查）
   ├─ position_service.py       # 仓位/数量计算，BUY/SELL 数量计算、仓位更新
   ├─ repository_service.py     # 对 Redis/数据库的读写封装（position_repo, trade_repo, price_repo, cost_repo）

services/
└─ market/
   ├─ __init__.py
   ├─ market_service.py        # 核心接口，對外暴露方法：get_ticker, get_current_price, get_klines...
   ├─ cache_service.py         # 封裝緩存邏輯（Redis操作），統一管理TTL
   ├─ price_repo_service.py    # 封裝價格倉庫操作（price_repo），提供歷史價格、統計、最新價格接口
   ├─ mexc_client_service.py   # 封裝 MEXC API 調用，對外提供 get_ticker_24hr, get_orderbook, get_klines 等方法


services\market\market_service.py
services/market/
├── data_service.py       # 抓行情、Kline、深度、歷史資料
├── cache_service.py      # market_cache_service.py 可保留
├── client_service.py     # mexc_client_service.py 可合併到這
├── price_service.py      # price_repo_service.py 改名，負責價格計算、指標
└── market_service.py     # 總控，調用上面各 service

services\trading\trading_service.py
services/trading/risk/
├── __init__.py
├── position_limit.py      # 持倉上限檢查
├── pnl_limit.py           # 未實現損益檢查
├── exposure_limit.py      # 整體風險敞口檢查
├── leverage_check.py      # 槓桿檢查
└── risk_service.py        # 總控，整合所有檢查
