## Context7 採樣來源
- MEXC API docs: `/suenot/mexc-docs-markdown`（spot WebSocket market & user streams）
- Python websockets: `/python-websockets/websockets`（`ping_interval=None` 時可自行控制 PING/PONG 與 heartbeat）

## 市場行情 Stream 重點
- Base WS: `wss://wbs-api.mexc.com/ws`，單連線最長 24h、最多 30 個訂閱；空訂閱 30s 內會被斷線。
- 常用頻道：交易 `spot@public.aggre.deals.v3.api.pb@(100ms|10ms)@<SYMBOL>`、K線 `spot@public.kline.v3.api.pb@<SYMBOL>@<INTERVAL>`、深度 diff `spot@public.aggre.depth.v3.api.pb@(100ms|10ms)@<SYMBOL>`、partial depth `spot@public.limit.depth.v3.api.pb@<SYMBOL>@(5|10|20)`、book ticker `spot@public.aggre.bookTicker.v3.api.pb@(100ms|10ms)@<SYMBOL>`.
- PING/PONG: 逾時 server 會關閉，客戶端需定期發 `{"method":"PING"}`；收到 PING 時回 `{"method":"PONG"}`。
- Proto：官方 schema 來源 `mexcdevelop/websocket-proto`；建議在 Python 端用 `protobuf==4.25.1` 解析再轉 JSON。

## 用戶私有 Stream 重點
- ListenKey 透過 REST `/api/v3/userDataStream` 取得，60 分鐘過期；建議每 30 分鐘 `PUT` keepalive，必要時 `DELETE` 關閉。
- 連線 `wss://wbs-api.mexc.com/ws?listenKey=<key>`，單 key 最多 5 條 WS，UID 最多 60 個 key。
- 預設頻道：`spot@private.account.v3.api.pb`、`spot@private.deals.v3.api.pb`、`spot@private.orders.v3.api.pb`。

## 現況核對
- `src/app/infrastructure/external/mexc/websocket/market_streams.py` 已提供主要 channel builder 與 `decode_push_data`（proto -> dict）。
- `src/app/infrastructure/external/mexc/ws/ws_client.py` 以 `MEXCWebSocketClient` 包裝；已將 keepalive 預設 25 分鐘、heartbeat 20s 並禁用內建 ping。
- 測試 `tests/test_ws_client.py` 覆蓋 PING/PONG、SUB/UNSUB、proto decoder 與 user stream builders。

## 下一步行動（最小變更）
1) 檢查是否需要 diff depth 本地重建流程（fromVersion/toVersion）的小提示，可在 README 或 docs 補充。
2) 若前端需直連 protobuf，補充 schema 取得方式連結（`mexcdevelop/websocket-proto`）與版本鎖定。
3) 保持 `keepalive_interval` 預設 ≤30 分鐘；必要時為 REST 429/5xx 加入回退策略。
4) 維持定期測試：`python -m pytest tests/test_ws_client.py`。
