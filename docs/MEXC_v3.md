## MEXC Spot V3 API Links

### Reference
- [Introduction](https://www.mexc.com/api-docs/spot-v3/introduction)
- [Change Log](https://www.mexc.com/api-docs/spot-v3/change-log)
- [FAQs](https://www.mexc.com/api-docs/spot-v3/faqs)
- [General Info](https://www.mexc.com/api-docs/spot-v3/general-info)
  - [Endpoints & security](https://www.mexc.com/api-docs/spot-v3/general-info#endpoint-security-type) – Base URLs, signature rules.
  - [Timing & recvWindow](https://www.mexc.com/api-docs/spot-v3/general-info#timestamp-recvwindow) – Server time and request validity.
  - [Limits & weights](https://www.mexc.com/api-docs/spot-v3/general-info#limit-quotas) – Rate limits, IP weights.
  - [Error codes](https://www.mexc.com/api-docs/spot-v3/general-info#error-codes) – Common error meanings.
- [Public API Definitions](https://www.mexc.com/api-docs/spot-v3/public-api-definitions)
  - [Data types](https://www.mexc.com/api-docs/spot-v3/public-api-definitions#definitions) – Standard fields and formats.
  - [Enums](https://www.mexc.com/api-docs/spot-v3/public-api-definitions#enum-definitions) – Order types, sides, timeInForce, interval values.
- [Official SDK](https://github.com/mexcdevelop/mexc-api-sdk)

### REST – Public & Market Data
- [GET /api/v3/ping](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#test-connectivity) – Test connectivity.
- [GET /api/v3/time](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#check-server-time) – Server time.
- [GET /api/v3/exchangeInfo](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#exchange-information) – Symbols and rules.
- [GET /api/v3/defaultSymbols](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#default-symbols) – Default trading pairs.
- [GET /api/v3/symbol/offline](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#offline-symbols) – Suspended/delisted symbols.
- [GET /api/v3/depth](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#order-book) – Order book.
- [GET /api/v3/trades](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#recent-trades-list) – Recent trades.
- [GET /api/v3/historicalTrades](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#old-trade-lookup) – Older trades.
- [GET /api/v3/aggTrades](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#compressedaggregate-trades-list) – Aggregate trades.
- [GET /api/v3/klines](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#klinecandlestick-data) – Candles.
- [GET /api/v3/ticker/24hr](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#24hr-ticker-price-change-statistics) – 24h stats.
- [GET /api/v3/ticker/price](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#symbol-price-ticker) – Last price.
- [GET /api/v3/ticker/bookTicker](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#symbol-order-book-ticker) – Best bid/ask.

### REST – Account & Trade (signed)
- [POST /api/v3/order/test](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#test-new-order-trade) – Validate order params.
- [POST /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#new-order--trade) – Place order.
- [GET /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-order-trade) – Query order.
- [DELETE /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-order-trade) – Cancel order.
- [GET /api/v3/openOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#current-open-orders-user_data) – Open orders.
- [DELETE /api/v3/openOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-open-orders-trade) – Cancel open orders.
- [GET /api/v3/allOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#all-orders-user_data) – All orders.
- [GET /api/v3/myTrades](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-trade-list-user_data) – Account trades.
- [GET /api/v3/account](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information-user_data) – Balances and permissions.

### REST – Wallet (signed)
- [GET /api/v3/capital/config/getall](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#user-coin-information-user_data) – Coin list.
- [POST /api/v3/capital/deposit/address](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#generate-deposit-address-user_data) – Deposit address.
- [GET /api/v3/capital/deposit/hisrec](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#deposit-history-user_data) – Deposit history.
- [POST /api/v3/capital/withdraw](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#withdraw-user_data) – Withdraw.
- [DELETE /api/v3/capital/withdraw](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#withdraw-cancel-user_data) – Cancel withdraw.
- [GET /api/v3/capital/withdraw/history](https://www.mexc.com/api-docs/spot-v3/wallet-endpoints#withdraw-history-user_data) – Withdraw history.

### REST – Sub-Account (signed)
- [POST /api/v3/sub-account/virtualSubAccount](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#create-virtual-sub-account) – Create virtual sub-account.
- [GET /api/v3/sub-account/list](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#query-virtual-sub-account) – List sub-accounts.
- [POST /api/v3/sub-account/apiKey](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#create-api-key) – Create API key.
- [GET /api/v3/sub-account/apiKey](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#query-api-key) – Query API key.
- [DELETE /api/v3/sub-account/apiKey](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#delete-api-key) – Delete API key.
- [POST /api/v3/capital/sub-account/universalTransfer](https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints#sub-account-universal-transfer) – Universal transfer.

### REST – Rebate (signed)
- [GET /api/v3/rebate/history](https://www.mexc.com/api-docs/spot-v3/rebate-endpoints#get-rebate-history-records) – Rebate summary.
- [GET /api/v3/rebate/records/detail](https://www.mexc.com/api-docs/spot-v3/rebate-endpoints#get-rebate-records-detail) – Invitee rebate detail.
- [GET /api/v3/rebate/self-records/detail](https://www.mexc.com/api-docs/spot-v3/rebate-endpoints#get-self-rebate-records-detail) – Self rebate detail.

### User Data Stream (listen key)
- [POST /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key) – Generate listen key.
- [PUT /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity) – Keepalive.
- [GET /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys) – List active keys.
- [DELETE /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key) – Close key.

### WebSocket Streams
- [Market streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams)
  - [Live subscription/unsubscription](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#live-subscriptionunsubscription-to-data-streams)
  - [Protocol Buffers integration](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#protocol-buffers-integration)
  - [Subscribe](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#subscribe-to-a-data-stream) / [Unsubscribe](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#unsubscribe-from-a-data-stream)
  - [PING/PONG](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#pingpong-mechanism)
  - [Trade streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#trade-streams)
  - [K-line streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#k-line-streams)
  - [Diff. depth stream](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#diffdepth-stream)
  - [Partial book depth streams](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#partial-book-depth-streams)
  - [Individual symbol book ticker](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streams)
  - [Individual symbol book ticker (batch)](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streamsbatch-aggregation)
  - [MiniTickers](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#minitickers) / [MiniTicker](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#miniticker)
  - [Maintain local order book](https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#how-to-properly-maintain-a-local-copy-of-the-order-book)
- [User data streams](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams)
  - [Listen key](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#listen-key) / [Generate](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key) / [Extend](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity) / [Close](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key)
  - [Get valid listen keys](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys)
  - [Spot account update](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-update)
  - [Spot account deals](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-deals)
  - [Spot account orders](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-orders)
