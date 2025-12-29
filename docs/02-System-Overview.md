## 02 系統概要與資料流

**目標**：用一頁理解系統組件、資料流與保護原則。

### 核心組件
- **FastAPI**：提供 `/health`、`/market/price`、`/account/balance`、`/status` 等 API。
- **MEXCClient**：簽名請求 HMAC-SHA256，`X-MEXC-APIKEY` 標頭，依官方 v3 規格。
- **Redis**：雙層存儲  
  - 永久層（無 TTL）：最新價格、倉位、成本、原始 MEXC 回應  
  - 快取層（短 TTL）：對外 API 查詢用的價格快取
- **Cloud Scheduler / Cloud Run**：定期觸發 `05-min-job`、`01-min-job`、`15-min-job`。

### 資料流（簡化）
```
MEXC API → Cloud Task → Redis 永久層 (無 TTL)
                   ↘→ Redis 快取層 (30s TTL，用於公開 API)

Dashboard / API 查詢 → 讀取快取層，失效時回退永久層
Position / Cost 計算 → 只用永久層資料
```

### 倉位與顯示規則
- **餘額顯示**：永遠以 MEXC API 為權威（真實餘額可能因手動交易變動）。  
- **策略分析欄位**：avg_cost、unrealized/realized PnL 來自 Redis 永久層（只反映機器人交易視角）。  
- **倉位分層**：核心/波段/機動（詳見 05），核心倉位永不賣出。

### 安全與資源
- API Key：只開 Spot Trading，禁用提款，建議白名單 IP，90 天內輪換。
- Redis：生產請啟用驗證與 TLS，Cloud Run 可透過 VPC Connector。
- 最小權限：Cloud Scheduler 以 OIDC 呼叫，服務帳號只給 `roles/run.invoker`。

### 重要端點速查
- `/health`：健康檢查（Redis、MEXC 可用性）。  
- `/market/price/{symbol}`：市場價格（使用快取層，失效回退）。  
- `/account/balance`：實時餘額（直連 MEXC）。  
- `/status`：機器人狀態、倉位、成本、層級。  
- `/tasks/05-min-job` / `/tasks/01-min-job` / `/tasks/15-min-job`：Cloud Task 目標。

### 核心保護原則
1. **資料一致性**：真實餘額用 API；分析用 Redis；不要混用。  
2. **持久存儲**：Scheduler 相關 key 不設 TTL；快取層才設短 TTL。  
3. **最低暴露**：不輸出敏感金鑰；只暴露必要欄位於公開 API。  
4. **可觀測性**：所有 Cloud Task 記錄來源與授權方式（X-CloudScheduler 或 OIDC）。  
5. **可回滾**：保留原始 MEXC 回應（`mexc:raw:*`）便於重算或排障。  
