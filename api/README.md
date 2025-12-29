api/
├─ __init__.py

├─ account/
│  ├─ __init__.py
│  ├─ balance.py         # /account/balance
│  ├─ orders.py          # /account/orders
│  ├─ trades.py          # /account/trades
│  └─ sub_accounts.py    # /account/sub-accounts

├─ bot/
│  ├─ __init__.py
│  ├─ control.py         # /bot/control
│  └─ execute.py         # /bot/execute

├─ sub_account/
│  ├─ __init__.py
│  ├─ list.py            # /account/sub-account/list
│  ├─ balance.py         # /account/sub-account/balance
│  ├─ transfer.py        # /account/sub-account/transfer
│  └─ api_key.py         # /account/sub-account/api-key (create/delete)

├─ status/
│  ├─ __init__.py
│  ├─ dashboard.py       # / 和 /dashboard
│  ├─ api_info.py        # /api/info
│  ├─ health.py          # /health
│  └─ status.py          # /status

├─ market/
│  ├─ __init__.py
│  ├─ ticker.py          # /market/ticker/{symbol}
│  ├─ price.py           # /market/price/{symbol}
│  ├─ exchange_info.py   # /market/exchange-info
│  ├─ orderbook.py       # /market/orderbook/{symbol}
│  ├─ book_ticker.py     # /market/book-ticker/{symbol}
│  ├─ trades.py          # /market/trades/{symbol}
│  ├─ agg_trades.py      # /market/agg-trades/{symbol}
│  └─ klines.py          # /market/klines/{symbol}
