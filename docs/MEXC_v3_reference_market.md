## MEXC Spot V3 – Reference & Market REST

### Reference
- [Introduction](https://www.mexc.com/api-docs/spot-v3/introduction)
- [Change Log](https://www.mexc.com/api-docs/spot-v3/change-log)
- [FAQs](https://www.mexc.com/api-docs/spot-v3/faqs)
- [General Info](https://www.mexc.com/api-docs/spot-v3/general-info)
  - [Endpoints & security](https://www.mexc.com/api-docs/spot-v3/general-info#endpoint-security-type)
  - [Timing & recvWindow](https://www.mexc.com/api-docs/spot-v3/general-info#timestamp-recvwindow)
  - [Limits & weights](https://www.mexc.com/api-docs/spot-v3/general-info#limit-quotas)
  - [Error codes](https://www.mexc.com/api-docs/spot-v3/general-info#error-codes)
- [Public API Definitions](https://www.mexc.com/api-docs/spot-v3/public-api-definitions)
  - [Data types](https://www.mexc.com/api-docs/spot-v3/public-api-definitions#definitions)
  - [Enums](https://www.mexc.com/api-docs/spot-v3/public-api-definitions#enum-definitions)
- [Official SDK](https://github.com/mexcdevelop/mexc-api-sdk)

### REST – Public & Market Data
- [GET /api/v3/ping](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#test-connectivity) – Connectivity.
- [GET /api/v3/time](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#check-server-time) – Returns `serverTime`.
- [GET /api/v3/exchangeInfo](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#exchange-information) – Symbols/rules.
- [GET /api/v3/defaultSymbols](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#default-symbols) – Default pairs.
- [GET /api/v3/symbol/offline](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#offline-symbols) – Suspended/delisted list.
- [GET /api/v3/depth](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#order-book) – `bids/asks` with `price/qty`.
- [GET /api/v3/trades](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#recent-trades-list) – Recent trades `id/price/qty/time`.
- [GET /api/v3/historicalTrades](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#old-trade-lookup) – Older trades (same shape).
- [GET /api/v3/aggTrades](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#compressedaggregate-trades-list) – `a/f/l/p/q/T/m/M`.
- [GET /api/v3/klines](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#klinecandlestick-data) – `[openTime, open, high, low, close, volume, closeTime, quoteVolume]`.
- [GET /api/v3/ticker/24hr](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#24hr-ticker-price-change-statistics) – 24h stats (change %, volumes).
- [GET /api/v3/ticker/price](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#symbol-price-ticker) – `symbol/price`.
- [GET /api/v3/ticker/bookTicker](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#symbol-order-book-ticker) – `bidPrice/bidQty/askPrice/askQty`.

### Sample Responses (market)
```json
// depth
{ "lastUpdateId": 1, "bids": [["100.0","5"]], "asks": [["100.5","2"]] }
// trades
[ { "id": 123, "price": "100.1", "qty": "1", "time": 1700000000000, "isBuyerMaker": false } ]
// aggTrades
[ { "a": 10, "p": "100.0", "q": "2", "f": 1, "l": 2, "T": 1700000000000, "m": false, "M": true } ]
// klines (single entry)
[1700000000000,"100","101","99","100.5","10","1700000060000","1000"]
// ticker/24hr
{ "symbol":"BTCUSDT","priceChange":"10","priceChangePercent":"1.0","lastPrice":"100" }
// price
{ "symbol":"BTCUSDT","price":"100" }
// bookTicker
{ "symbol":"BTCUSDT","bidPrice":"99.9","bidQty":"1","askPrice":"100.1","askQty":"2" }
```
