# 監控指南：Cloud Task 數據儲存修復

## 部署後監控清單

### 1. Cloud Scheduler 執行日誌

#### 查看日誌
```bash
# 查看最近的 Cloud Scheduler 執行日誌
gcloud logging read "resource.type=cloud_run_revision AND \
  labels.service_name=qrl-api AND \
  textPayload=~'Cloud Task'" \
  --limit 50 \
  --format json
```

#### 預期日誌訊息

**task_sync_balance 成功執行**：
```
[Cloud Task] Stored raw account_info response
[Cloud Task] Balance synced - QRL: 1000.5000 (locked: 0.0), USDT: 500.25 (locked: 10.0), Total assets: 3
```

**task_update_price 成功執行**：
```
[Cloud Task] Stored raw ticker_24hr response
[Cloud Task] Price updated - Price: 0.020500, Change: 2.50%, Volume: 1500000.00, 24h High/Low: 0.021000/0.019500
```

**task_update_cost 成功執行**：
```
[Cloud Task] Cost updated - Position: 1000.5000 QRL @ $0.020000, Current: $0.020500, Value: $20.51, Unrealized P&L: $0.50 (2.50%), Realized P&L: $0.00, Total P&L: $0.50
```

### 2. Redis 數據驗證

#### 連接到 Redis
```bash
# 使用 Redis Cloud URL
redis-cli -u $REDIS_URL

# 或使用主機和密碼
redis-cli -h your-redis-host -p 6379 -a your-password
```

#### 檢查原始 MEXC 響應
```bash
# 查看所有原始響應 keys
KEYS mexc:raw:*

# 預期輸出：
# 1) "mexc:raw:account_info:latest"
# 2) "mexc:raw:account_info:history"
# 3) "mexc:raw:ticker_24hr:latest"
# 4) "mexc:raw:ticker_24hr:history"
# 5) "mexc:raw:ticker_price:latest"
# 6) "mexc:raw:ticker_price:history"

# 查看最新的 account_info 響應
GET mexc:raw:account_info:latest

# 預期輸出（JSON 格式）：
# {
#   "response": {
#     "accountType": "SPOT",
#     "canTrade": true,
#     "balances": [...]
#   },
#   "timestamp": 1703750000000,
#   "datetime": "2024-12-28T04:00:00",
#   "metadata": {"task": "sync-balance", "source": "cloud_scheduler"}
# }

# 查看歷史記錄數量
ZCARD mexc:raw:account_info:history
ZCARD mexc:raw:ticker_24hr:history
```

#### 檢查價格數據
```bash
# 檢查永久價格存儲（無 TTL）
GET bot:QRLUSDT:price:latest
TTL bot:QRLUSDT:price:latest
# 預期 TTL 輸出：-1 (表示無過期時間)

# 檢查快取價格存儲（30秒 TTL）
GET bot:QRLUSDT:price:cached
TTL bot:QRLUSDT:price:cached
# 預期 TTL 輸出：0-30 (剩餘秒數)

# 查看價格歷史
ZRANGE bot:QRLUSDT:price:history 0 9 WITHSCORES
# 預期輸出：價格列表，按時間戳排序
```

#### 檢查倉位數據
```bash
# 查看完整倉位數據
HGETALL bot:QRLUSDT:position

# 預期輸出應包含：
# qrl_balance: "1000.5"
# usdt_balance: "500.25"
# qrl_locked: "0.0"
# usdt_locked: "10.0"
# all_balances: "{...JSON...}"
# account_type: "SPOT"
# can_trade: "True"
# can_withdraw: "True"
# can_deposit: "True"
# update_time: "1703750000000"
# updated_at: "2024-12-28T04:00:00"

# 檢查 TTL（應該沒有）
TTL bot:QRLUSDT:position
# 預期輸出：-1 (無過期時間)
```

### 3. API 端點測試

#### 測試 Cloud Task 端點
```bash
# 替換為你的 Cloud Run URL
CLOUD_RUN_URL="https://your-app.run.app"

# 測試 sync-balance (需要 Cloud Scheduler header)
curl -X POST "$CLOUD_RUN_URL/tasks/sync-balance" \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json" | jq

# 預期輸出：
# {
#   "status": "success",
#   "task": "sync-balance",
#   "data": {
#     "qrl_balance": 1000.5,
#     "usdt_balance": 500.25,
#     "qrl_locked": 0.0,
#     "usdt_locked": 10.0,
#     "total_assets": 3,
#     "account_type": "SPOT"
#   },
#   "timestamp": "2024-12-28T04:00:00"
# }

# 測試 update-price
curl -X POST "$CLOUD_RUN_URL/tasks/update-price" \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json" | jq

# 預期輸出：
# {
#   "status": "success",
#   "task": "update-price",
#   "data": {
#     "price": 0.020500,
#     "volume_24h": 1500000.0,
#     "price_change": 0.0005,
#     "price_change_percent": 2.5,
#     "high_24h": 0.021000,
#     "low_24h": 0.019500,
#     ...
#   },
#   "timestamp": "2024-12-28T04:00:00"
# }
```

#### 測試狀態端點
```bash
# 查看機器人狀態
curl "$CLOUD_RUN_URL/status" | jq

# 確認 latest_price 有數據
curl "$CLOUD_RUN_URL/status" | jq '.latest_price'

# 預期輸出：
# {
#   "price": "0.020500",
#   "volume": "1500000.0",
#   "timestamp": "2024-12-28T04:00:00"
# }
```

### 4. 數據持久性驗證

#### 30 秒後檢查
```bash
# 等待 30 秒後，檢查永久價格是否仍然存在
sleep 30

# 永久價格應該仍然存在
redis-cli GET bot:QRLUSDT:price:latest
# 應該返回價格數據

# 快取價格可能已過期
redis-cli GET bot:QRLUSDT:price:cached
# 可能返回 (nil)

# 檢查 TTL
redis-cli TTL bot:QRLUSDT:price:latest
# 應該返回 -1 (無過期)
```

#### 1 小時後檢查
```bash
# 1 小時後，原始響應和價格數據應該都還在
redis-cli GET mexc:raw:account_info:latest
redis-cli GET bot:QRLUSDT:price:latest
redis-cli HGETALL bot:QRLUSDT:position

# 所有數據都應該存在，證明永久儲存成功
```

### 5. 錯誤監控

#### 查看錯誤日誌
```bash
# 查看所有錯誤日誌
gcloud logging read "resource.type=cloud_run_revision AND \
  labels.service_name=qrl-api AND \
  (severity=ERROR OR severity=WARNING)" \
  --limit 50
```

#### 常見問題排查

**問題 1：原始響應未儲存**
```bash
# 檢查日誌是否有 "Stored raw" 訊息
# 如果沒有，檢查 MEXC API 是否正常調用
```

**問題 2：價格數據仍然過期**
```bash
# 檢查 TTL
redis-cli TTL bot:QRLUSDT:price:latest

# 如果不是 -1，代碼可能沒有部署成功
# 重新部署並確認版本
```

**問題 3：倉位數據不完整**
```bash
# 檢查倉位數據欄位
redis-cli HGETALL bot:QRLUSDT:position

# 確認包含：all_balances, qrl_locked, usdt_locked 等欄位
# 如果缺少，檢查 cloud_tasks.py 是否正確部署
```

### 6. 性能監控

#### Redis 記憶體使用
```bash
# 檢查 Redis 記憶體使用
redis-cli INFO memory

# 監控以下指標：
# - used_memory_human
# - used_memory_peak_human
# - mem_fragmentation_ratio
```

#### Cloud Run 指標
```bash
# 在 Google Cloud Console 查看：
# 1. Cloud Run > qrl-api > Metrics
# 2. 監控：
#    - Request count
#    - Request latency
#    - Container CPU utilization
#    - Container memory utilization
```

### 7. 成功標準

✅ **數據持久化成功**：
- [ ] `mexc:raw:*:latest` keys 存在
- [ ] `bot:QRLUSDT:price:latest` TTL 為 -1
- [ ] `bot:QRLUSDT:position` 包含所有欄位
- [ ] 數據在 1 小時後仍然存在

✅ **日誌記錄正確**：
- [ ] 看到 "Stored raw" 訊息
- [ ] 看到詳細的餘額和價格指標
- [ ] 無錯誤日誌

✅ **API 響應正確**：
- [ ] Task 端點返回完整數據
- [ ] Status 端點顯示持久化數據
- [ ] 所有欄位都有值

### 8. 告警設置建議

#### Cloud Monitoring 告警
```yaml
# 建議設置以下告警：

1. Cloud Task 執行失敗
   - 條件：HTTP 5xx 錯誤 > 3 次/5分鐘
   - 通知：Email + Slack

2. Redis 連接失敗
   - 條件：日誌包含 "Redis not connected"
   - 通知：Email

3. MEXC API 調用失敗
   - 條件：日誌包含 "Failed to get" 或 "API request failed"
   - 通知：Email

4. 數據儲存失敗
   - 條件：日誌包含 "Failed to store" 或 "Failed to set"
   - 通知：Email
```

## 總結

部署後請按照以上步驟監控系統運行狀況，確保：
1. Scheduled tasks 成功執行
2. 數據永久儲存到 Redis
3. 原始 MEXC 響應被記錄
4. 所有欄位都被正確儲存
5. 數據不再過期

如有任何問題，檢查日誌並參考 `CLOUD_TASK_STORAGE_FIX.md` 文檔。
