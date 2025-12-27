# Cloud Scheduler 選項說明

## 問題澄清

**Cloud Scheduler ≠ APScheduler**

### 選項 1: Google Cloud Scheduler (真正的 Cloud Scheduler)

**什麼是 Google Cloud Scheduler？**
- Google Cloud Platform 的雲端服務
- 完全托管的 Cron 作業調度器
- 透過 HTTP/HTTPS、Pub/Sub 或 App Engine 觸發任務

**架構**:
```
Google Cloud Scheduler (雲端)
    ↓ HTTP POST
FastAPI Endpoint (例如: /tasks/sync-balance)
    ↓
執行任務邏輯
```

**優點**:
- ✅ 無需在應用內運行調度器
- ✅ 高可用性（Google 管理）
- ✅ 獨立於應用程式
- ✅ 可視化管理界面
- ✅ 自動重試和錯誤處理

**缺點**:
- ❌ 需要 Google Cloud 帳戶
- ❌ 產生額外費用
- ❌ 需要公開可訪問的 HTTP 端點

**實作方式**:

1. 在 FastAPI 創建任務端點:
```python
@app.post("/tasks/sync-balance")
async def task_sync_balance(request: Request):
    """由 Cloud Scheduler 調用的任務端點"""
    # 驗證請求來自 Cloud Scheduler
    # ... 執行餘額同步邏輯 ...
    return {"status": "success"}
```

2. 在 Google Cloud Console 創建 Cloud Scheduler Job:
```
名稱: sync-balance-job
頻率: */30 * * * * (每 30 秒)
目標: HTTP
URL: https://your-api.com/tasks/sync-balance
方法: POST
```

---

### 選項 2: APScheduler (應用內調度器)

**什麼是 APScheduler？**
- Python 套件，運行在應用程式內部
- 應用內記憶體調度器
- 適合單體應用

**架構**:
```
FastAPI Application
    ├─ API Endpoints
    └─ APScheduler (內部)
        └─ 定時執行任務
```

**優點**:
- ✅ 無需外部服務
- ✅ 免費
- ✅ 簡單設定
- ✅ 適合開發和小型部署

**缺點**:
- ❌ 應用重啟時調度器重啟
- ❌ 多實例部署會重複執行任務
- ❌ 應用崩潰則調度器停止

**已實作**: `scheduler.py` (目前使用的方案)

---

### 選項 3: Celery + Redis (企業級)

**什麼是 Celery？**
- 分佈式任務隊列
- 支持定時任務 (Celery Beat)
- 適合大規模生產環境

**架構**:
```
Celery Beat (調度器)
    ↓
Redis (消息隊列)
    ↓
Celery Worker (執行任務)
```

**優點**:
- ✅ 分佈式執行
- ✅ 高可靠性
- ✅ 支持任務隊列、重試、超時
- ✅ 適合微服務架構

**缺點**:
- ❌ 複雜度高
- ❌ 需要額外的 Redis/RabbitMQ
- ❌ 配置較複雜

---

## 建議方案

### 對於當前項目 (QRL Trading Bot)

**推薦: APScheduler (選項 2) - 已實作 ✅**

**原因**:
1. **簡單**: 無需額外服務，直接集成到 FastAPI
2. **成本**: 完全免費
3. **適合規模**: 單一交易機器人，不需要分佈式
4. **即時生效**: 應用啟動即開始調度
5. **本地開發友好**: 不需要 Google Cloud 帳戶

**適用場景**:
- ✅ 單一服務器部署
- ✅ 開發和測試環境
- ✅ 小到中型交易機器人
- ✅ 不需要高可用性保證

---

### 何時使用 Google Cloud Scheduler？

**適合場景**:
- 多個微服務，每個需要觸發不同的端點
- 需要高可用性（99.9% SLA）
- 已經使用 Google Cloud Platform
- 需要獨立於應用的調度器
- 多實例部署，避免重複執行

**不適合當前項目**:
- ❌ 增加部署複雜度
- ❌ 需要公開 HTTP 端點（安全性考慮）
- ❌ 產生額外費用
- ❌ 本地開發不便

---

### 何時使用 Celery？

**適合場景**:
- 大規模生產環境
- 需要任務隊列（異步處理）
- 多個 worker 並行處理
- 需要任務重試、超時控制
- 微服務架構

**不適合當前項目**:
- ❌ 過度設計（overkill）
- ❌ 增加系統複雜度
- ❌ 需要額外的消息隊列服務

---

## 當前實作 (APScheduler)

**已實作的調度器**: `scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 5 個自動任務:
1. Price Update (10秒) - 即時價格
2. Balance Sync (30秒) - 解決餘額顯示問題 ⭐
3. Cost Update (1分鐘) - 盈虧計算
4. Health Check (1分鐘) - 系統監控
5. Data Cleanup (每天) - 數據維護
```

**啟動方式**:
```bash
# 啟動 FastAPI，調度器自動啟動
python main.py
# 或
uvicorn main:app --reload
```

**查看日誌**:
```
[INFO] Starting scheduler...
[INFO] Scheduler started successfully with 5 tasks
[INFO] [Balance Sync] QRL: 1000.5000, USDT: 500.00
[DEBUG] [Price Update] QRL/USDT: 3.090690
```

---

## 結論

**對於 QRL Trading Bot，APScheduler 是最佳選擇**

| 需求 | APScheduler | Cloud Scheduler | Celery |
|------|-------------|-----------------|--------|
| 簡單性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 成本 | 免費 | 付費 | 免費(需Redis) |
| 設置複雜度 | 低 | 中 | 高 |
| 適合小型項目 | ✅ | ❌ | ❌ |
| 適合大型項目 | ⚠️ | ✅ | ✅ |
| 本地開發 | ✅ | ❌ | ⚠️ |

**已選擇**: APScheduler ✅

**理由**: 簡單、免費、符合項目規模，能夠解決當前的餘額同步問題。

如需升級到 Cloud Scheduler 或 Celery，可以在項目擴展時再考慮。
