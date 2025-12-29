https://www.mexc.com/api-docs/spot-v3/introduction Introduction
https://www.mexc.com/api-docs/spot-v3/change-log Change Log
https://www.mexc.com/api-docs/spot-v3/faqs FAQs
https://www.mexc.com/api-docs/spot-v3/general-info General Info
https://www.mexc.com/api-docs/spot-v3/market-data-endpoints Market Data Endpoints
https://www.mexc.com/api-docs/spot-v3/subaccount-endpoints Sub-Account Endpoints
https://www.mexc.com/api-docs/spot-v3/spot-account-trade Spot Account/Trade
https://www.mexc.com/api-docs/spot-v3/wallet-endpoints Wallet Endpoints
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams Websocket Market Streams
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams Websocket User Data Streams
https://www.mexc.com/api-docs/spot-v3/rebate-endpoints Rebate Endpoints
https://www.mexc.com/api-docs/spot-v3/public-api-definitions Public API Definitions
https://github.com/mexcdevelop/mexc-api-sdk mexc-api-sdk


Websocket User Data Streams
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams
Listen Key
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#listen-key
Generate Listen Key
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key
Get Valid Listen Keys
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys
Extend Listen Key Validity
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity
Close Listen Key
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key
Spot Account Update
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-update
Spot Account Deals
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-deals
Spot Account Orders
https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#spot-account-orders

Live Subscription/Unsubscription to Data Streams
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#live-subscriptionunsubscription-to-data-streams
Protocol Buffers Integration
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#protocol-buffers-integration
Subscribe to a Data Stream
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#subscribe-to-a-data-stream
Unsubscribe from a Data Stream
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#unsubscribe-from-a-data-stream
PING/PONG Mechanism
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#pingpong-mechanism
Trade Streams
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#trade-streams
K-line Streams
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#k-line-streams
Diff.Depth Stream
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#diffdepth-stream
Partial Book Depth Streams
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#partial-book-depth-streams
Individual Symbol Book Ticker Streams
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streams
Individual Symbol Book Ticker Streams(Batch Aggregation)
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streamsbatch-aggregation
MiniTickers
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#minitickers
MiniTicker
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#miniticker
How to Properly Maintain a Local Copy of the Order Book
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#how-to-properly-maintain-a-local-copy-of-the-order-book

All Orders:
https://www.mexc.com/api-docs/spot-v3/spot-account-trade#all-orders
[
  {
    "symbol": "LTCBTC",
    "orderId": 1,
    "orderListId": -1, 
    "clientOrderId": "myOrder1",
    "price": "0.1",
    "origQty": "1.0",
    "executedQty": "0.0",
    "cummulativeQuoteQty": "0.0",
    "status": "NEW",
    "timeInForce": "GTC",
    "type": "LIMIT",
    "side": "BUY",
    "stopPrice": "0.0",
    "icebergQty": "0.0",
    "time": 1499827319559,
    "updateTime": 1499827319559,
    "isWorking": true,
    "stpMode":"", 
    "cancelReason":"stp_cancel", 
    "origQuoteOrderQty": "0.000000"
  }
]
Account Trade List: 應該要
https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-trade-list
[
  {
    "symbol": "BNBBTC",
    "id": "fad2af9e942049b6adbda1a271f990c6",
    "orderId": "bb41e5663e124046bd9497a3f5692f39",
    "orderListId": -1,
    "price": "4.00000100", 
    "qty": "12.00000000", 
    "quoteQty": "48.000012", 
    "commission": "10.10000000", 
    "commissionAsset": "BNB", 
    "time": 1499865549590, 
    "isBuyer": true, 
    "isMaker": false, 
    "isBestMatch": true,
    "isSelfTrade": true,
    "clientOrderId": null
  }
]

Account Information: 應該要
https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information
{
    "makerCommission": null,
    "takerCommission": null,
    "buyerCommission": null,
    "sellerCommission": null,
    "canTrade": true,
    "canWithdraw": true,
    "canDeposit": true,
    "updateTime": null,
    "accountType": "SPOT",
    "balances": [{
        "asset": "NBNTEST",
        "free": "1111078",
        "locked": "33",
        "available": "1"
    }, {
        "asset": "MAIN",
        "free": "1020000",
        "locked": "0",
        "available": "102000"
    }],
    "permissions": ["SPOT"]
}

Recent Trades List: 
https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#recent-trades-list
[
  {
    "id": null,
    "price": "23",
    "qty": "0.478468",
    "quoteQty": "11.004764",
    "time": 1640830579240,
    "isBuyerMaker": true,
    "isBestMatch": true
  }
]


Compressed/Aggregate Trades List:
https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#compressedaggregate-trades-list
[
  {
    "a": null,
    "f": null,
    "l": null,
    "p": "46782.67",
    "q": "0.0038",
    "T": 1641380483000,
    "m": false,
    "M": true
  }
]

Kline/Candlestick Data: 
https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#klinecandlestick-data
[
  [
    1640804880000, 
    "47482.36", 
    "47482.36", 
    "47416.57", 
    "47436.1", 
    "3.550717", 
    1640804940000, 
    "168387.3"
  ]
]

K-line Streams:
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#k-line-streams
Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.kline.v3.api.pb@BTCUSDT@Min15"
    ]
}

Response:

{
  "channel": "spot@public.kline.v3.api.pb@BTCUSDT@Min15",
  "publicspotkline": {
    "interval": "Min15", // K-line interval
    "windowstart": 1736410500, // Start time of the K-line
    "openingprice": "92925", // Opening trade price during this K-line
    "closingprice": "93158.47", // Closing trade price during this K-line
    "highestprice": "93158.47", // Highest trade price during this K-line
    "lowestprice": "92800", // Lowest trade price during this K-line
    "volume": "36.83803224", // Trade volume during this K-line
    "amount": "3424811.05", // Trade amount during this K-line
    "windowend": 1736411400 // End time of the K-line   
  },
  "symbol": "BTCUSDT",
  "symbolid": "2fb942154ef44a4ab2ef98c8afb6a4a7",
  "createtime": 1736410707571
}

Available intervals:

Min1
Min5
Min15
Min30
Min60
Hour4
Hour8
Day1
Week1
Month1

Diff.Depth Stream
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#k-line-streams
Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.aggre.depth.v3.api.pb@100ms@BTCUSDT"
    ]
}

Response:

{
  "channel": "spot@public.aggre.depth.v3.api.pb@100ms@BTCUSDT",
  "publicincreasedepths": {
    "asksList": [], // asks: Sell orders
    "bidsList": [ // bids: Buy orders
      {
        "price": "92877.58", // Price level of change
        "quantity": "0.00000000" // Quantity
      }
    ],
    "eventtype": "spot@public.aggre.depth.v3.api.pb@100ms", // Event type
    "fromVersion" : "10589632359", // from version
    "toVersion" : "10589632359" // to version
  },
  "symbol": "BTCUSDT", // Trading pair
  "sendtime": 1736411507002 // Event time
}

If the order quantity () for a price level is 0, it indicates that the order at that price has been canceled or executed, and that price level should be removed.quantity

Request Parameter: spot@public.aggre.depth.v3.api.pb@(100ms|10ms)@&lt;symbol&gt;

Response Parameters:

Parameter	Data Type	Description
price	string	Price level of change
quantity	string	Quantity
eventtype	string	Event type
version	string	Version number
symbol	string	Trading pair
sendtime	long	Event time

Partial Book Depth Streams
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#partial-book-depth-streams
This stream pushes limited level depth information. The "levels" indicate the number of order levels for buy and sell orders, which can be 5, 10, or 20 levels.

Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.limit.depth.v3.api.pb@BTCUSDT@5"
    ]
}

Response:

{
  "channel": "spot@public.limit.depth.v3.api.pb@BTCUSDT@5",
  "publiclimitdepths": {
    "asksList": [ // asks: Sell orders
      {
        "price": "93180.18", // Price level of change
        "quantity": "0.21976424" // Quantity
      }
    ],
    "bidsList": [ // bids: Buy orders
      {
        "price": "93179.98",
        "quantity": "2.82651000"
      }
    ],
    "eventtype": "spot@public.limit.depth.v3.api.pb", // Event type
    "version": "36913565463" // Version number 
  },
  "symbol": "BTCUSDT", // Trading pair
  "sendtime": 1736411838730 // Event time
}

Request Parameter: spot@public.limit.depth.v3.api.pb@&lt;symbol&gt;@&lt;level&gt;

Response Parameters:

Parameter	Data Type	Description
price	string	Price level of change
quantity	string	Quantity
eventtype	string	Event type
version	string	Version number
symbol	string	Trading pair
sendtime	long	Event time



https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streams

Individual Symbol Book Ticker Streams
Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.

Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.aggre.bookTicker.v3.api.pb@100ms@BTCUSDT"
    ]
}

Response:

{
  "channel": "spot@public.aggre.bookTicker.v3.api.pb@100ms@BTCUSDT",
  "publicbookticker": {
    "bidprice": "93387.28",  // Best bid price
    "bidquantity": "3.73485", // Best bid quantity
    "askprice": "93387.29", // Best ask price
    "askquantity": "7.669875" // Best ask quantity
  },
  "symbol": "BTCUSDT", // Trading pair
  "sendtime": 1736412092433 // Event time
}

Request Parameter: spot@public.aggre.bookTicker.v3.api.pb@(100ms|10ms)@&lt;symbol&gt;

Response Parameters:

Parameter	Data Type	Description
bidprice	string	Best bid price
bidquantity	string	Best bid quantity
askprice	string	Best ask price
askquantity	string	Best ask quantity
symbol	string	Trading pair
sendtime	long	Event time


Individual Symbol Book Ticker Streams(Batch Aggregation)
https://www.mexc.com/api-docs/spot-v3/websocket-market-streams#individual-symbol-book-ticker-streamsbatch-aggregation

This batch aggregation version pushes the best order information for a specified trading pair.

Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.bookTicker.batch.v3.api.pb@BTCUSDT"
    ]
}

Response:

{
  "channel" : "spot@public.bookTicker.batch.v3.api.pb@BTCUSDT",
  "symbol" : "BTCUSDT",
  "sendTime" : "1739503249114",
  "publicBookTickerBatch" : {
    "items" : [ {
      "bidPrice" : "96567.37",
      "bidQuantity" : "3.362925",
      "askPrice" : "96567.38",
      "askQuantity" : "1.545255"
    } ]
  }
}

Request Parameter: spot@public.bookTicker.batch.v3.api.pb@&lt;symbol&gt;

Response Parameters:

Parameter	Data Type	Description
bidprice	string	Best bid price
bidquantity	string	Best bid quantity
askprice	string	Best ask price
askquantity	string	Best ask quantity
symbol	string	Trading pair
sendtime	long	Event time

## 應用程式使用重點與疑難排解

- `/account/balance` 會先呼叫 **GET /api/v3/account (簽名)** 取得帳戶餘額，再呼叫 **GET /api/v3/ticker/price?symbol=QRLUSDT** 估值；若餘額沒有顯示，通常是 API Key 沒有 SPOT 讀取權限、`MEXC_API_KEY/MEXC_SECRET_KEY` 未設、或使用了 Broker key 卻在 SPOT 模式。
- 市場資料（如 `/market/klines`）僅使用公開端點（`/api/v3/klines` 等），與帳戶/交易的簽名請求分開，不會混用。
- `/account/orders` 使用 **GET /api/v3/openOrders (簽名)** 僅針對 `QRLUSDT` 查詢，與行情/健康檢查路徑互不影響。
- 若 Cloud Run 上僅回 500，請檢查上述簽名端點所需的環境變數與權限，並先用 `/health` 看 `missing` 欄位是否缺 Key/Secret。
