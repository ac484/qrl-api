## 04 營運、排程與監控

**目標**：知道有哪些定時任務、如何確認執行、如何快速查問題。

### 任務總覽（預設頻率）
- `tasks/sync-balance` (01-min-job)：每 1 分鐘，抓帳戶餘額與原始回應，寫入 `mexc:raw:*` 與倉位。  
- `tasks/update-price` (05-min-job)：每 5 分鐘，抓最新價格與 24h 數據，寫入永久層與快取層。  
- `tasks/update-cost` (15-min-job)：每 15 分鐘，更新成本/未實現損益。  
- 授權：支援 `X-CloudScheduler` 及 OIDC `Authorization: Bearer ...`（建議用 OIDC）。

### 快速監控
- **Cloud Run 日誌**  
  ```bash
  gcloud logging read "resource.type=cloud_run_revision AND labels.service_name=qrl-api" --limit=50
  gcloud logging read "jsonPayload.message=~'Cloud Task'" --limit=20
  ```
- **Redis 快速檢查**  
  ```bash
  redis-cli TTL bot:QRLUSDT:price:latest    # 期望 -1
  redis-cli TTL bot:QRLUSDT:price:cached    # 期望 0-30
  redis-cli GET mexc:raw:account_info:latest
  redis-cli HGETALL bot:QRLUSDT:position
  ```
- **API 健康度**  
  ```bash
  curl ${SERVICE_URL}/health
  curl ${SERVICE_URL}/status | jq '.latest_price'
  ```

### 監控重點指標
- Cloud Run：請求數、延遲、錯誤率、記憶體。  
- Scheduler：觸發成功率、HTTP 401/5xx。  
- Redis：`used_memory_human`、`mem_fragmentation_ratio`、TTL 是否意外出現。  

### 告警建議
- Cloud Task 5xx 連續 >3 次/5 分鐘。  
- 日誌出現「Redis not connected」或「Failed to store」。  
- `bot:QRLUSDT:price:latest` TTL 不是 -1。  
- Cloud Run 錯誤率或延遲高於基線。  

### 常見故障速排
- **Scheduler 401**：檢查 OIDC audience、`roles/run.invoker`。  
- **Redis 無資料**：確認任務有跑；手動觸發 `update-price` 後再看 TTL。  
- **Dashboard 餘額怪異**：比對 `/account/balance` 回傳；永遠以 API 為準。  
- **原始回應缺失**：查日誌中是否有「Stored raw」，如無重新部署並確認權限。  

### 例行維運清單
1. 每日：查看最近 20 筆 Cloud Run 日誌、TTL 檢查。  
2. 每週：檢查 Scheduler 任務狀態、Redis 記憶體使用量。  
3. 每月：輪換 API Key（保留同樣的權限），確認告警仍然有效。  
