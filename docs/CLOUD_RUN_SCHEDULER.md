# Google Cloud Run + Cloud Scheduler 架構

## 重要說明

**Google Cloud Run 是 serverless 平台**
- ❌ 不適合使用 APScheduler (需要 24/7 運行)
- ✅ 必須使用 Google Cloud Scheduler 觸發 HTTP 端點
- 💰 Cloud Run 按請求計費，不運行時不收費

## 正確架構

```
Google Cloud Scheduler (雲端 Cron)
    ↓ HTTP POST (每 30 秒)
Google Cloud Run (您的 FastAPI)
    ↓ 執行任務
    ↓ 完成後容器可以停止
節省成本 ✅
```

## 實作方式

### 1. 創建任務端點 (在 main.py)

```python
from fastapi import Header, HTTPException

@app.post("/tasks/sync-balance")
async def task_sync_balance(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler")
):
    """由 Cloud Scheduler 調用 - 同步餘額"""
    # 驗證請求來自 Cloud Scheduler
    if not x_cloudscheduler:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # 執行餘額同步邏輯
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            return {"status": "skipped", "reason": "API keys not configured"}
        
        async with mexc_client:
            account_info = await mexc_client.get_account_info()
            
            qrl_balance = 0.0
            usdt_balance = 0.0
            
            for balance in account_info.get("balances", []):
                asset = balance.get("asset")
                if asset == "QRL":
                    qrl_balance = float(balance.get("free", 0))
                elif asset == "USDT":
                    usdt_balance = float(balance.get("free", 0))
            
            # 更新 Redis
            await redis_client.set_position({
                "qrl_balance": str(qrl_balance),
                "usdt_balance": str(usdt_balance),
                "updated_at": datetime.now().isoformat()
            })
            
            logger.info(f"[Cloud Task] Balance synced: QRL={qrl_balance}, USDT={usdt_balance}")
            
            return {
                "status": "success",
                "qrl_balance": qrl_balance,
                "usdt_balance": usdt_balance
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Balance sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/update-price")
async def task_update_price(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler")
):
    """由 Cloud Scheduler 調用 - 更新價格"""
    if not x_cloudscheduler:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            
            await redis_client.set_latest_price(price, volume_24h)
            await redis_client.add_price_to_history(price)
            
            logger.info(f"[Cloud Task] Price updated: {price}")
            
            return {
                "status": "success",
                "price": price,
                "volume": volume_24h
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Price update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tasks/update-cost")
async def task_update_cost(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler")
):
    """由 Cloud Scheduler 調用 - 更新成本數據"""
    if not x_cloudscheduler:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        position = await redis_client.get_position()
        cost_data = await redis_client.get_cost_data()
        
        qrl_balance = float(position.get("qrl_balance", 0))
        avg_cost = float(cost_data.get("avg_cost", 0))
        
        if qrl_balance > 0 and avg_cost > 0:
            async with mexc_client:
                ticker = await mexc_client.get_ticker_price("QRLUSDT")
                current_price = float(ticker.get("price", 0))
            
            unrealized_pnl = (current_price - avg_cost) * qrl_balance
            total_invested = avg_cost * qrl_balance
            realized_pnl = float(cost_data.get("realized_pnl", 0))
            
            await redis_client.set_cost_data(
                avg_cost=avg_cost,
                total_invested=total_invested,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl
            )
            
            logger.info(f"[Cloud Task] Cost updated: unrealized_pnl={unrealized_pnl}")
            
            return {
                "status": "success",
                "unrealized_pnl": unrealized_pnl
            }
        
        return {"status": "skipped", "reason": "No position or cost data"}
    
    except Exception as e:
        logger.error(f"[Cloud Task] Cost update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. 在 Google Cloud Console 設置 Cloud Scheduler

#### Job 1: 餘額同步 (每 30 秒)
```
名稱: sync-balance-job
描述: Sync MEXC account balance to Redis
頻率: */30 * * * * (每 30 秒，注意 Cloud Scheduler 最小間隔是 1 分鐘)
  或使用: * * * * * (每分鐘)
時區: Asia/Taipei
目標類型: HTTP
URL: https://your-cloud-run-url/tasks/sync-balance
HTTP 方法: POST
正文: {}
標頭: X-CloudScheduler: true
```

#### Job 2: 價格更新 (每 1 分鐘)
```
名稱: update-price-job
描述: Update QRL/USDT price
頻率: * * * * * (每分鐘)
時區: Asia/Taipei
目標類型: HTTP
URL: https://your-cloud-run-url/tasks/update-price
HTTP 方法: POST
標頭: X-CloudScheduler: true
```

#### Job 3: 成本更新 (每 5 分鐘)
```
名稱: update-cost-job
描述: Update cost and PnL data
頻率: */5 * * * * (每 5 分鐘)
時區: Asia/Taipei
目標類型: HTTP
URL: https://your-cloud-run-url/tasks/update-cost
HTTP 方法: POST
標頭: X-CloudScheduler: true
```

### 3. 部署到 Cloud Run

**Dockerfile** (不需要改動):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**部署命令**:
```bash
gcloud run deploy qrl-api \
  --source . \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars MEXC_API_KEY=$MEXC_API_KEY \
  --set-env-vars MEXC_SECRET_KEY=$MEXC_SECRET_KEY \
  --set-env-vars REDIS_URL=$REDIS_URL
```

### 4. 費用估算

**Cloud Run 費用** (按實際使用計費):
- 請求費用: 每 100 萬次請求 $0.40
- CPU 費用: 每 vCPU-秒 $0.00002400
- 內存費用: 每 GiB-秒 $0.00000250

**示例計算** (每月):
- 3 個 Cloud Scheduler Jobs
- Job 1 (每分鐘): 30 天 × 24 小時 × 60 分鐘 = 43,200 次請求
- Job 2 (每分鐘): 43,200 次請求
- Job 3 (每 5 分鐘): 8,640 次請求
- 總請求: ~95,000 次/月
- 每次請求 ~200ms

**預估成本**:
- 請求: $0.40 × (95,000 / 1,000,000) ≈ $0.04
- CPU: $0.024 × (95,000 × 0.2s / 3600s) ≈ $0.13
- **總計: ~$0.20/月** ✅

**對比 APScheduler** (24/7 運行):
- 需要 1 vCPU × 720 小時/月
- 費用: ~$17/月 ❌

**節省**: 98.8% 💰

### 5. Cloud Scheduler 費用

- 前 3 個 jobs: 免費
- 之後每個 job: $0.10/月

**總費用**: $0 (我們只有 3 個 jobs)

## 移除 APScheduler

**刪除以下文件**:
- `scheduler.py` (不再需要)

**移除 requirements.txt 中的**:
- `APScheduler==3.10.4`

**移除 main.py 中的**:
```python
# 移除這些
from scheduler import trading_scheduler
await trading_scheduler.start()
await trading_scheduler.stop()
```

## 總結

| 方案 | 月費用 | 適用場景 |
|------|--------|----------|
| APScheduler (24/7) | ~$17 | 傳統伺服器 |
| Cloud Scheduler + Cloud Run | ~$0.20 | **Serverless (推薦)** ✅ |

**Cloud Run + Cloud Scheduler = 正確且經濟的選擇**

費用降低 98%，功能完全相同！
