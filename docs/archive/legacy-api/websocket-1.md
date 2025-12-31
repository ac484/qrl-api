## MEXC WebSocket – User Data (Minimal)

- Base REST: `https://api.mexc.com`
- WS base: `wss://wbs-api.mexc.com/ws`
- Create listen key: `POST /api/v3/userDataStream` (valid 60m)
- Extend: `PUT /api/v3/userDataStream` (send every 30m)
- List keys: `GET /api/v3/userDataStream`
- Close: `DELETE /api/v3/userDataStream`
- Each key: max 5 WS connections; UID max 60 keys; WS connection auto-drops at 24h.

Connect
```
wss://wbs-api.mexc.com/ws?listenKey=<key>
```

Subscribe (protobuf channels)
```json
{ "method": "SUBSCRIPTION", "params": ["spot@private.account.v3.api.pb"] }
{ "method": "SUBSCRIPTION", "params": ["spot@private.deals.v3.api.pb"] }
{ "method": "SUBSCRIPTION", "params": ["spot@private.orders.v3.api.pb"] }
```

Keepalive / Close
```json
{ "method": "PING" }          // expect PONG
// Close socket or call DELETE to invalidate key
```

Sample payloads (structure only)
- Account: `channel`, `balances[] { asset, free, locked }`, `sendTime`
- Deals: `channel`, `symbol`, `price`, `quantity`, `tradeType`, `orderId`, `time`
- Orders: `channel`, `symbol`, `price`, `quantity`, `status`, `orderType`, `time`

Notes
- Proto definitions: https://github.com/mexcdevelop/websocket-proto
- Deserialize with generated protobuf classes; ignore undocumented fields.
- Keep logic minimal: create key → connect → subscribe → handle events → renew key periodically.
- Minimal client helper: `infrastructure/external/mexc_client/ws_client.py` (`connect_user_stream`)
