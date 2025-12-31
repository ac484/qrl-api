## MEXC Spot V3 – Account & Trade (REST) + User Data Stream (REST)

### REST – Account & Trade (signed)
- [POST /api/v3/order/test](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#test-new-order-trade) – Validate params (empty success).
- [POST /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#new-order--trade) – Place order (`orderId/clientOrderId/status`).
- [GET /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-order-trade) – Query order (status, times, fills).
- [DELETE /api/v3/order](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-order-trade) – Cancel (returns cancelled order info).
- [GET /api/v3/openOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#current-open-orders-user_data) – Open orders list.
- [DELETE /api/v3/openOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-open-orders-trade) – Cancel all for symbol.
- [GET /api/v3/allOrders](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#all-orders-user_data) – Historical orders.
- [GET /api/v3/myTrades](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-trade-list-user_data) – Trades (`id/orderId/price/qty/commission`).
- [GET /api/v3/account](https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information-user_data) – Balances (`free/locked`) & permissions.

### Sample Responses (account/trade)
```json
// new order
{ "symbol":"BTCUSDT","orderId":1,"clientOrderId":"abc","transactTime":1700000000000,"status":"NEW" }
// query order
{ "orderId":1,"status":"FILLED","price":"100","origQty":"1","executedQty":"1","time":1700000000000 }
// myTrades
[ { "id":10,"orderId":1,"price":"100","qty":"0.5","commission":"0.0005","isBuyer":true,"time":1700000000000 } ]
// account
{ "makerCommission":10,"takerCommission":10,"balances":[{"asset":"USDT","free":"100","locked":"0"}] }
```

### User Data Stream (REST for listen key)
- [POST /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key) – Generate listen key.
- [PUT /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity) – Keepalive.
- [GET /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys) – List active keys.
- [DELETE /api/v3/userDataStream](https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key) – Close key.

```json
// listen key
{ "listenKey": "abc123" }
// list listen keys
{ "listenKey": ["abc123"], "total": 1, "available": 0 }
```
