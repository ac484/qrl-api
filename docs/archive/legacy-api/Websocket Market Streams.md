## Websocket Market Streams
The base endpoint is: wss://wbs-api.mexc.com/ws

### Connection basics
- Each connection is valid for no more than 24 hours; reconnect proactively before expiry.
- Symbols must be uppercase, for example `spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT`.
- One websocket connection supports a maximum of 30 subscriptions; without a valid subscription the server closes the link after ~30 seconds.
- Send `{"method":"PING"}` periodically (and reply `{"method":"PONG"}` to server PINGs) to keep the connection alive; the server also closes idle links with no data flow after about one minute.
- Only rely on documented fields; undocumented ones may be removed by the exchange.

## Web visualization packages (Web 視覺化套件建議)

- **輕量蠟燭圖／走勢圖**：`lightweight-charts`（TradingView 官方 npm 套件）能以極小體積呈現 K 線、交易量與即時游標提示，適合 streaming 的 kline、trade streams。
- **通用統計圖表**：`chart.js` 搭配 `chartjs-chart-financial`（蠟燭／OHLC 插件）與 `chartjs-adapter-luxon`（時間軸解析）可快速繪製 K 線、成交量柱狀圖與 VWAP/MA 疊加。
- **深度圖／熱力圖**：`apache-echarts` 內建豐富圖表類型，可用折線／面積圖呈現 order book depth，或使用 heatmap/treemap 呈現成交分佈。
- **在瀏覽器解 protobuf**：若前端直接連到 `*.api.pb` channel，可在瀏覽器端安裝 `protobufjs@7.2.5`（支援 proto3），並引入官方 proto schema（來源：https://github.com/mexcdevelop/websocket-proto）；可優先使用 `protobufjs/light` 並搭配 tree-shaking 以降低瀏覽器 bundle 大小。
- **後端轉 JSON 再推送**：若由後端解析再轉推前端，確保 Python 端已安裝 `protobuf`（已在 `requirements.txt` 鎖定 `protobuf==4.25.1`），再將解析後的 JSON 串流給圖表元件。

## 實現方式與計畫 (Implementation plan)

1) 後端處理
- 以 websockets 連 MEXC `*.api.pb` channel，使用 `protobuf==4.25.1` 解析 proto，轉為標準 JSON。
- 依資料型態拆不同推播：交易/klines -> K 線 & 成交量；depth -> order book; ticker/miniTicker -> 指標卡片。
- 透過內部 WS/SSE/Redis pub-sub 將 JSON 轉送到前端，並保留心跳/重連邏輯。

2) 前端顯示
- kline/成交量：`lightweight-charts` 或 `chart.js + chartjs-chart-financial`。
- depth/heatmap：`apache-echarts` 折線/面積/heatmap。
- protobuf 直讀：若前端直連 WS，裝 `protobufjs@7.2.5` + 官方 schema；若取後端 JSON，直接餵圖表即可。
- 加上滑動視窗快取與節流 (如 100ms) 以避免過度重繪。

Live Subscription/Unsubscription to Data Streams
The following data can be sent via websocket to subscribe or unsubscribe from data streams. Examples are provided below.
The in the response is an unsigned integer and serves as the unique identifier for communication.id
If the in the response matches the corresponding request field, it indicates that the request was sent successfully.msg
## Protocol Buffers Integration
The websocket push uses protobuf envelopes. Official schema files: https://github.com/mexcdevelop/websocket-proto

1. **PB definition & codegen**
   - Use `protoc` (https://github.com/protocolbuffers/protobuf) to compile `.proto` files.
   - Python bindings plus the shared decoder already live in `src/app/infrastructure/external/proto/websocket_pb`.
   - The default binary decoder `decode_push_data` (re-exported by `src.app.infrastructure.external.mexc.ws.ws_client`) converts `PushDataV3ApiWrapper` frames into a Python `dict`.

2. **Java example**
   ```
   <dependency>
       <groupId>com.google.protobuf</groupId>
       <artifactId>protobuf-java</artifactId>
       <version>{protobuf.version}</version>
   </dependency>
   PushDataV3ApiWrapper wrapper = PushDataV3ApiWrapper.newBuilder()
       .setChannel("spot@public.aggre.depth.v3.api.pb@10ms")
       .setSymbol("BTCUSDT")
       .setSendTime(System.currentTimeMillis())
       .build();
   byte[] payload = wrapper.toByteArray();
   PushDataV3ApiWrapper decoded = PushDataV3ApiWrapper.parseFrom(payload);
   ```

3. **Python example (uses in-repo bindings + shared decoder)**
   ```
   from src.app.infrastructure.external.proto.websocket_pb import PushDataV3ApiWrapper_pb2
   from src.app.infrastructure.external.mexc.websocket.market_streams import decode_push_data

   wrapper = PushDataV3ApiWrapper_pb2.PushDataV3ApiWrapper(
       channel="spot@public.aggre.depth.v3.api.pb@10ms",
       symbol="BTCUSDT",
   )
   payload = wrapper.SerializeToString()
   print(decode_push_data(payload))  # dict with channel + payload fields
   ```

4. **Other languages**
   protobuf supports C++, C#, Go, Ruby, PHP, JS, and more. If you supply your own decoder, pass it as `binary_decoder` when building `MEXCWebSocketClient`; otherwise the default PushData decoder is used.

Subscribe to a Data Stream
Subscription Channel Response

{
  "id": 0,
  "code": 0,
  "msg": "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"
}

Request
{
 "method": "SUBSCRIPTION",
 "params": ["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"]
}

Unsubscribe from a Data Stream
Unsubscription Response

{
  "id": 0,
  "code": 0,
  "msg": "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"
}

Request
{
 "method": "UNSUBSCRIPTION",
 "params": ["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"]
}

PING/PONG Mechanism
PING/PONG Response

{
  "id": 0,
  "code": 0,
  "msg": "PONG"
}

Request
{"method": "PING"}

Trade Streams
Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"
    ]
}

Response:

{
  "channel": "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT",
  "publicdeals": {
    "dealsList": [
      {
        "price": "93220.00", // Trade price
        "quantity": "0.04438243", // Trade quantity
        "tradetype": 2, // Trade type (1: Buy, 2: Sell)
        "time": 1736409765051 // Trade time
      }
    ],
    "eventtype": "spot@public.aggre.deals.v3.api.pb@100ms" // Event type 
  },
  "symbol": "BTCUSDT", // Trading pair
  "sendtime": 1736409765052 // Event time
}

Request Parameter: spot@public.aggre.deals.v3.api.pb@(100ms|10ms)@&lt;symbol&gt;

The Trade Streams push raw trade information; each trade has a unique buyer and seller

Response Parameters:

Parameter	Data Type	Description
dealsList	array	Trade information
price	string	Trade price
quantity	string	Trade quantity
tradetype	int	Trade type (1: Buy, 2: Sell)
time	long	Trade time
eventtype	string	Event type
symbol	string	Trading pair
sendtime	long	Event time
K-line Streams
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

The Kline/Candlestick Stream push updates to the current klines/candlestick every second.

Request Parameter: spot@public.kline.v3.api.pb@&lt;symbol&gt;@&lt;interval&gt;

Response Parameters:

Parameter	Data Type	Description
publicspotkline	object	K-line information
interval	string	K-line interval
windowstart	long	Start time of the K-line
openingprice	bigDecimal	Opening trade price during this K-line
closingprice	bigDecimal	Closing trade price during this K-line
highestprice	bigDecimal	Highest trade price during this K-line
lowestprice	bigDecimal	Lowest trade price during this K-line
volume	bigDecimal	Trade volume during this K-line
amount	bigDecimal	Trade amount during this K-line
windowend	long	End time of the K-line
symbol	string	Trading pair
symbolid	string	Trading pair ID
createtime	long	Event time
K-line Interval Parameters:

Min: Minutes; Hour: Hours; Day: Days; Week: Weeks; M: Month
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
MiniTickers
minitickers of all trading pairs in the specified timezone, pushed every 3 seconds.
UTC value range: 24H, UTC-10, UTC-8, UTC-7, UTC-6, UTC-5, UTC-4, UTC-3, UTC+0, UTC+1, UTC+2, UTC+3, UTC+4, UTC+4:30, UTC+5, UTC+5:30, UTC+6, UTC+7, UTC+8, UTC+9, UTC+10, UTC+11, UTC+12, UTC+12:45, UTC+13

Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.miniTickers.v3.api.pb@UTC+8"
    ]
}

Response:

{
    "channel": "spot@public.miniTickers.v3.api.pb@UTC+8",
    "sendTime": "1755076614201",
    "publicMiniTickers":
    {
        "items":
        [
            {
                "symbol": "METAUSDT",
                "price": "0.055",
                "rate": "-0.2361",
                "zonedRate": "-0.2361",
                "high": "0.119",
                "low": "0.053",
                "volume": "814864.474",
                "quantity": "10764997.16",
                "lastCloseRate": "-0.2567",
                "lastCloseZonedRate": "-0.2567",
                "lastCloseHigh": "0.119",
                "lastCloseLow": "0.053"
            },
            {
                "symbol": "FCATUSDT",
                "price": "0.0000031",
                "rate": "-0.4464",
                "zonedRate": "-0.4464",
                "high": "0.0000066",
                "low": "0.0000025",
                "volume": "2825.4350195",
                "quantity": "654649950.75",
                "lastCloseRate": "-0.4464",
                "lastCloseZonedRate": "-0.4464",
                "lastCloseHigh": "0.0000066",
                "lastCloseLow": "0.0000025"
            },
            {
                "symbol": "CRVETH",
                "price": "0.00022592",
                "rate": "0.028",
                "zonedRate": "0.028",
                "high": "0.00022856",
                "low": "0.00021024",
                "volume": "1062.48406269",
                "quantity": "4884456.998",
                "lastCloseRate": "0.0276",
                "lastCloseZonedRate": "0.0276",
                "lastCloseHigh": "0.00022856",
                "lastCloseLow": "0.00021024"
            }
        ]
    }
}

Request Parameter: spot@public.miniTickers.v3.api.pb@&lt;timezone&gt;

Response Parameters:

Parameter Name	Data Type	Description
symbol	string	Trading pair name
price	string	Latest price
rate	string	Price change percentage (UTC+8 timezone)
zonedRate	string	Price change percentage (local timezone)
high	string	Rolling highest price
low	string	Rolling lowest price
volume	string	Rolling turnover amount
quantity	string	Rolling trading volume
lastCloseRate	string	Previous close change percentage (UTC+8 timezone)
lastCloseZonedRate	string	Previous close change percentage (local timezone)
lastCloseHigh	string	Previous close rolling highest price
lastCloseLow	string	Previous close rolling lowest price
MiniTicker
miniticker of the specified trading pair in the specified timezone, pushed every 3 seconds.
UTC value range: 24H, UTC-10, UTC-8, UTC-7, UTC-6, UTC-5, UTC-4, UTC-3, UTC+0, UTC+1, UTC+2, UTC+3, UTC+4, UTC+4:30, UTC+5, UTC+5:30, UTC+6, UTC+7, UTC+8, UTC+9, UTC+10, UTC+11, UTC+12, UTC+12:45, UTC+13

Request:

{
    "method": "SUBSCRIPTION",
    "params": [
        "spot@public.miniTicker.v3.api.pb@MXUSDT@UTC+8"
    ]
}

Response:

{
  "channel" : "spot@public.miniTicker.v3.api.pb@MXUSDT@UTC+8",
  "symbol" : "MXUSDT",
  "sendTime" : "1755076752201",
  "publicMiniTicker" : {
    "symbol" : "MXUSDT",
    "price" : "2.5174",
    "rate" : "0.0766",
    "zonedRate" : "0.0766",
    "high" : "2.6299",
    "low" : "2.302",
    "volume" : "11336518.0264",
    "quantity" : "4638390.17",
    "lastCloseRate" : "0.0767",
    "lastCloseZonedRate" : "0.0767",
    "lastCloseHigh" : "2.6299",
    "lastCloseLow" : "2.302"
  }
}

Request Parameter: spot@public.miniTicker.v3.api.pb@&lt;symbol&gt;@&lt;timezone&gt;

Response Parameters:

Parameter Name	Data Type	Description
symbol	string	Trading pair name
price	string	Latest price
rate	string	Price change percentage (UTC+8 timezone)
zonedRate	string	Price change percentage (local timezone)
high	string	Rolling highest price
low	string	Rolling lowest price
volume	string	Rolling turnover amount
quantity	string	Rolling trading volume
lastCloseRate	string	Previous close change percentage (UTC+8 timezone)
lastCloseZonedRate	string	Previous close change percentage (local timezone)
lastCloseHigh	string	Previous close rolling highest price
lastCloseLow	string	Previous close rolling lowest price
How to Properly Maintain a Local Copy of the Order Book
Connect to the WebSocket and subscribe to to obtain incremental aggregated depth information.spot@public.aggre.depth.v3.api.pb@(100ms|10ms)@MXBTC
Access the REST API to obtain a depth snapshot with 1000 levels.https://api.mexc.com/api/v3/depth?symbol=MXBTC&limit=1000
The of each new push message should be exactly equal to the of the previous message. Otherwise, packet loss has occurred, and reinitialization from step 2 is required.fromVersiontoVersion + 1
The order quantity in each push message represents the absolute value of the current order quantity at that price level, not a relative change.
If the in the push message is smaller than the in the snapshot, the message is outdated and should be ignored.toVersionversion
If the in the push message is greater than the in the snapshot, data is missing between the push message and the snapshot, requiring reinitialization from step 2.fromVersionversion
Now that the in the snapshot falls within the range of the push message, the push message can be integrated with the snapshot data as follows:version[fromVersion, toVersion]
If the price level in the push message already exists in the snapshot, update the quantity based on the push message.
If the price level in the push message does not exist in the snapshot, insert a new entry with the quantity from the push message.
If a price level in the push message has a quantity of 0, remove that price level from the snapshot.
Note: Since the depth snapshot has a limitation on the number of price levels, price levels outside the initial snapshot that have not changed in quantity will not appear in incremental push messages. Therefore, the local order book may differ slightly from the real order book. However, for most use cases, the 5000-depth limit is sufficient to effectively understand the market and trading activity.
