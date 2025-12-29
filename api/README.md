api/
├─ __init__.py
│
├─ account_routes.py   # 聚合帳戶相關路由 (balance/orders/trades/sub-accounts)
├─ bot_routes.py       # 機器人控制與執行路由
├─ market_routes.py    # 市場行情路由
├─ status_routes.py    # 健康檢查 / 狀態 / dashboard 路由
├─ sub_account_routes.py# 子帳戶相關路由
│
├─ account/            # 細分的帳戶路由模組
│  ├─ __init__.py
│  ├─ balance.py         # /account/balance
│  ├─ orders.py          # /account/orders
│  ├─ trades.py          # /account/trades
│  └─ sub_accounts.py    # /account/sub-accounts
│
├─ bot/
│  ├─ __init__.py
│  ├─ control.py         # /bot/control
│  └─ execute.py         # /bot/execute
│
├─ sub_account/
│  ├─ __init__.py
│  ├─ list.py            # /account/sub-account/list
│  ├─ balance.py         # /account/sub-account/balance
│  ├─ transfer.py        # /account/sub-account/transfer
│  └─ api_key.py         # /account/sub-account/api-key (create/delete)
│
├─ status/
│  ├─ __init__.py
│  ├─ dashboard.py       # / 和 /dashboard
│  ├─ api_info.py        # /api/info
│  ├─ health.py          # /health
│  └─ status.py          # /status
│
└─ market/
   ├─ __init__.py
   ├─ ticker.py          # /market/ticker/{symbol}
   ├─ price.py           # /market/price/{symbol}
   ├─ exchange_info.py   # /market/exchange-info
   ├─ orderbook.py       # /market/orderbook/{symbol}
   ├─ book_ticker.py     # /market/book-ticker/{symbol}
   ├─ trades.py          # /market/trades/{symbol}
   ├─ agg_trades.py      # /market/agg-trades/{symbol}
   └─ klines.py          # /market/klines/{symbol}
