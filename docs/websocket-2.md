## MEXC WebSocket – Market Streams (Minimal)

- WS base: `wss://wbs-api.mexc.com/ws`
- Limits: max 30 subscriptions per connection; idle 30s without subs, 1m without data; reconnect before 24h.
- Message format: protobuf (see https://github.com/mexcdevelop/websocket-proto). Use generated classes to decode; ignore undocumented fields.

Common request shapes
```json
{ "method": "SUBSCRIPTION", "params": ["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"] }
{ "method": "UNSUBSCRIPTION", "params": ["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"] }
{ "method": "PING" }  // expect PONG
```

Key channels (pick only what you need)
- Trades: `spot@public.aggre.deals.v3.api.pb@(100ms|10ms)@<symbol>`
- Klines: `spot@public.kline.v3.api.pb@<symbol>@<interval>` (Min1/5/15/30/60, Hour4/8, Day1, Week1, Month1)
- Diff depth: `spot@public.aggre.depth.v3.api.pb@(100ms|10ms)@<symbol>`
- Partial depth: `spot@public.limit.depth.v3.api.pb@<symbol>@(5|10|20)`
- Book ticker: `spot@public.aggre.bookTicker.v3.api.pb@(100ms|10ms)@<symbol>`
- Book ticker batch: `spot@public.bookTicker.batch.v3.api.pb@<symbol>`
- Mini tickers (all symbols): `spot@public.mini.ticker.v3.api.pb@<timezone>` (e.g., `UTC+0`, `24H`)

Sample payload shapes (abridged)
- Trades: `{ channel, publicdeals: { dealsList[{ price, quantity, tradetype, time }] }, symbol, sendtime }`
- Klines: `{ channel, publicspotkline: { interval, openingprice, closingprice, high, low, volume, windowstart, windowend }, symbol }`
- Diff depth: `{ channel, publicincreasedepths: { bidsList[], asksList[], fromVersion, toVersion }, symbol }`
- Partial depth: `{ channel, publiclimitdepths: { bidsList[], asksList[], version }, symbol }`
- Book ticker: `{ channel, publicbookticker: { bidprice, bidquantity, askprice, askquantity }, symbol }`

Minimal flow
1) Open WS → 2) SUBSCRIPTION for required channels → 3) Decode proto payloads → 4) Handle reconnect + ping when idle → 5) UNSUBSCRIPTION when done.
- Minimal client helper: `infrastructure/external/mexc_client/ws_client.py` (`connect_public_trades`)
