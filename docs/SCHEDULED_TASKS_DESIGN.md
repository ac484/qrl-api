# 定時任務設計文檔 (Scheduled Tasks Design)

## 概述 (Overview)

QRL 交易機器人需要定時執行多個任務來維持系統運作、更新數據和執行交易策略。

## 任務架構 (Task Architecture)

### 1. 任務調度器 (Task Scheduler)

**技術選擇**:
- Python: `APScheduler` (Advanced Python Scheduler)
- 支持 Cron 表達式、間隔觸發、一次性任務
- 異步任務支持 (async/await)

**實作位置**: `scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()
```

### 2. 核心任務清單 (Core Tasks)

#### 任務 A: 價格更新任務 (Price Update Task)

**頻率**: 每 10 秒
**優先級**: 高
**用途**: 更新 QRL/USDT 最新價格和行情數據

```python
@scheduler.scheduled_job(IntervalTrigger(seconds=10))
async def update_price_task():
    """每 10 秒更新一次價格"""
    ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
    price = float(ticker.get("lastPrice", 0))
    
    # 存入 Redis
    await redis_client.set_latest_price(price, ticker.get("volume"))
    await redis_client.add_price_to_history(price)
    
    logger.info(f"Price updated: {price}")
```

**數據流**:
```
MEXC API (/api/v3/ticker/24hr)
    ↓
Redis (price:latest, price:history)
    ↓
Dashboard (即時顯示)
```

---

#### 任務 B: 帳戶餘額同步任務 (Balance Sync Task)

**頻率**: 每 30 秒
**優先級**: 高
**用途**: 同步 MEXC 帳戶餘額到 Redis

```python
@scheduler.scheduled_job(IntervalTrigger(seconds=30))
async def sync_balance_task():
    """每 30 秒同步帳戶餘額"""
    if not config.MEXC_API_KEY:
        return
    
    account_info = await mexc_client.get_account_info()
    
    qrl_balance = 0
    usdt_balance = 0
    
    for balance in account_info.get("balances", []):
        if balance.get("asset") == "QRL":
            qrl_balance = float(balance.get("free", 0))
        elif balance.get("asset") == "USDT":
            usdt_balance = float(balance.get("free", 0))
    
    # 更新 Redis 持倉數據
    await redis_client.set_position({
        "qrl_balance": str(qrl_balance),
        "usdt_balance": str(usdt_balance),
        "updated_at": datetime.now().isoformat()
    })
    
    logger.info(f"Balance synced: QRL={qrl_balance}, USDT={usdt_balance}")
```

**數據流**:
```
MEXC API (/api/v3/account)
    ↓
Redis (position)
    ↓
Dashboard (即時餘額顯示)
```

**重要性**: 這個任務解決當前問題 - 確保 Redis 持倉數據是最新的！

---

#### 任務 C: 交易策略執行任務 (Trading Strategy Task)

**頻率**: 每 5 分鐘 (可配置)
**優先級**: 中
**用途**: 執行交易策略判斷和下單

```python
@scheduler.scheduled_job(IntervalTrigger(minutes=5))
async def execute_trading_strategy():
    """每 5 分鐘執行交易策略"""
    bot_status = await redis_client.get_bot_status()
    
    # 檢查機器人狀態
    if bot_status.get("status") != "running":
        logger.info("Bot not running, skip trading")
        return
    
    # 執行交易邏輯
    from bot import TradingBot
    bot = TradingBot(mexc_client, redis_client, "QRLUSDT")
    result = await bot.execute_cycle()
    
    logger.info(f"Trading cycle result: {result}")
```

**交易檢查項**:
1. Bot 狀態是否為 "running"
2. 是否超過每日交易次數限制
3. 距離上次交易是否超過最小間隔
4. 風險控制檢查

---

#### 任務 D: 成本數據更新任務 (Cost Data Update Task)

**頻率**: 每 1 分鐘
**優先級**: 中
**用途**: 重新計算平均成本和未實現盈虧

```python
@scheduler.scheduled_job(IntervalTrigger(minutes=1))
async def update_cost_data():
    """每分鐘更新成本數據"""
    position = await redis_client.get_position()
    cost_data = await redis_client.get_cost_data()
    
    qrl_balance = float(position.get("qrl_balance", 0))
    avg_cost = float(cost_data.get("avg_cost", 0))
    
    if qrl_balance > 0 and avg_cost > 0:
        # 獲取當前價格
        ticker = await mexc_client.get_ticker_price("QRLUSDT")
        current_price = float(ticker.get("price", 0))
        
        # 計算未實現盈虧
        unrealized_pnl = (current_price - avg_cost) * qrl_balance
        total_invested = avg_cost * qrl_balance
        
        await redis_client.set_cost_data(
            avg_cost=avg_cost,
            total_invested=total_invested,
            unrealized_pnl=unrealized_pnl
        )
        
        logger.info(f"Cost data updated: unrealized_pnl={unrealized_pnl}")
```

**數據流**:
```
Redis (position + cost_data)
    +
MEXC API (current_price)
    ↓
計算 unrealized_pnl
    ↓
Redis (cost_data updated)
    ↓
Dashboard (顯示最新盈虧)
```

---

#### 任務 E: 數據清理任務 (Data Cleanup Task)

**頻率**: 每天 00:00 (Cron)
**優先級**: 低
**用途**: 清理舊數據，維持 Redis 效能

```python
@scheduler.scheduled_job(CronTrigger(hour=0, minute=0))
async def cleanup_old_data():
    """每天午夜清理舊數據"""
    # 清理超過 30 天的價格歷史
    cutoff_timestamp = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
    await redis_client.client.zremrangebyscore(
        "bot:QRLUSDT:price:history",
        0,
        cutoff_timestamp
    )
    
    # 清理超過 90 天的交易記錄
    cutoff_timestamp = int((datetime.now() - timedelta(days=90)).timestamp() * 1000)
    await redis_client.client.zremrangebyscore(
        "bot:QRLUSDT:trades:history",
        0,
        cutoff_timestamp
    )
    
    logger.info("Old data cleaned up")
```

---

#### 任務 F: 健康檢查任務 (Health Check Task)

**頻率**: 每 1 分鐘
**優先級**: 高
**用途**: 檢查系統各組件健康狀態

```python
@scheduler.scheduled_job(IntervalTrigger(minutes=1))
async def health_check_task():
    """每分鐘健康檢查"""
    health_status = {
        "redis": False,
        "mexc_api": False,
        "timestamp": datetime.now().isoformat()
    }
    
    # 檢查 Redis
    try:
        health_status["redis"] = await redis_client.health_check()
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    # 檢查 MEXC API
    try:
        await mexc_client.ping()
        health_status["mexc_api"] = True
    except Exception as e:
        logger.error(f"MEXC API health check failed: {e}")
    
    # 存入 Redis
    await redis_client.client.set(
        "bot:health_status",
        json.dumps(health_status),
        ex=120
    )
    
    # 如果有問題，發送告警
    if not all(health_status.values()):
        logger.warning(f"Health check issues: {health_status}")
```

---

#### 任務 G: 統計報告任務 (Statistics Report Task)

**頻率**: 每天 08:00 (Cron)
**優先級**: 低
**用途**: 生成每日交易報告

```python
@scheduler.scheduled_job(CronTrigger(hour=8, minute=0))
async def generate_daily_report():
    """每天早上 8 點生成報告"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 獲取昨日交易次數
    daily_trades_key = f"bot:QRLUSDT:trades:daily:{yesterday}"
    trades_count = await redis_client.client.get(daily_trades_key)
    
    # 獲取昨日交易歷史
    trades = await redis_client.get_trade_history(limit=100)
    yesterday_trades = [
        t for t in trades
        if datetime.fromtimestamp(t["timestamp"] / 1000).strftime("%Y-%m-%d") == yesterday
    ]
    
    # 計算昨日盈虧
    total_pnl = sum(
        float(t.get("realized_pnl", 0))
        for t in yesterday_trades
    )
    
    report = {
        "date": yesterday,
        "trades_count": trades_count or 0,
        "total_pnl": total_pnl,
        "trades": yesterday_trades
    }
    
    logger.info(f"Daily report: {report}")
```

---

## 任務調度表 (Task Schedule)

| 任務 | 頻率 | 優先級 | 用途 |
|------|------|--------|------|
| A. 價格更新 | 10 秒 | 高 | 即時價格 |
| B. 餘額同步 | 30 秒 | 高 | **解決當前問題** |
| C. 交易策略 | 5 分鐘 | 中 | 自動交易 |
| D. 成本更新 | 1 分鐘 | 中 | 盈虧計算 |
| E. 數據清理 | 每天 00:00 | 低 | 維護效能 |
| F. 健康檢查 | 1 分鐘 | 高 | 系統監控 |
| G. 統計報告 | 每天 08:00 | 低 | 數據分析 |

---

## 實作文件結構 (Implementation)

```
qrl-api/
├── scheduler.py          # 主調度器
├── tasks/
│   ├── __init__.py
│   ├── price_tasks.py    # 任務 A
│   ├── balance_tasks.py  # 任務 B ← 解決當前問題的關鍵
│   ├── trading_tasks.py  # 任務 C
│   ├── cost_tasks.py     # 任務 D
│   ├── cleanup_tasks.py  # 任務 E
│   ├── health_tasks.py   # 任務 F
│   └── report_tasks.py   # 任務 G
├── main.py              # 啟動調度器
└── requirements.txt     # 添加 APScheduler
```

---

## 啟動方式 (Startup)

### 在 main.py 添加:

```python
from scheduler import scheduler

@app.on_event("startup")
async def startup_event():
    # ... 現有啟動邏輯 ...
    
    # 啟動任務調度器
    scheduler.start()
    logger.info("Task scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    # ... 現有關閉邏輯 ...
    
    # 關閉任務調度器
    scheduler.shutdown()
    logger.info("Task scheduler stopped")
```

---

## 關鍵：解決當前問題 (Solving Current Issue)

**任務 B (餘額同步)** 是解決當前儀表板顯示問題的關鍵：

1. **問題**: 儀表板顯示餘額為 0.00，但價格正常顯示
2. **原因**: Redis 持倉數據只有在手動執行 bot 時才更新
3. **解決**: 每 30 秒自動從 MEXC API 同步餘額到 Redis
4. **效果**: 儀表板永遠顯示最新餘額，不需要手動執行 bot

**數據流 (修復後)**:
```
定時任務 B (每 30 秒)
    ↓
MEXC API → 取得最新餘額
    ↓
Redis → 更新 position 數據
    ↓
Dashboard /status endpoint → 讀取 Redis
    ↓
前端 → 顯示正確餘額 ✅
```

---

## 配置選項 (Configuration)

在 `config.py` 添加:

```python
# Scheduler Configuration
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
PRICE_UPDATE_INTERVAL = int(os.getenv("PRICE_UPDATE_INTERVAL", "10"))  # 秒
BALANCE_SYNC_INTERVAL = int(os.getenv("BALANCE_SYNC_INTERVAL", "30"))  # 秒
TRADING_INTERVAL = int(os.getenv("TRADING_INTERVAL", "300"))  # 秒 (5分鐘)
```

---

## 監控和日誌 (Monitoring)

所有任務都記錄到日誌:
- 執行時間
- 成功/失敗狀態
- 處理的數據量
- 錯誤訊息

可通過 FastAPI logs 查看:
```bash
tail -f logs/scheduler.log
```

---

## 總結 (Summary)

這個定時任務設計：

1. ✅ **解決當前問題**: 任務 B 確保餘額數據始終最新
2. ✅ **自動化交易**: 任務 C 定時執行交易策略
3. ✅ **數據準確性**: 任務 A, D 保持價格和成本數據即時更新
4. ✅ **系統健康**: 任務 F 監控系統狀態
5. ✅ **資源管理**: 任務 E 清理舊數據
6. ✅ **數據分析**: 任務 G 提供交易報告

**核心優勢**: 不依賴手動執行，系統自動維護所有數據的準確性。
