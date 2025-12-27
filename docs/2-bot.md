# Cloud Run + Redis + MEXC v3 API - QRL/USDT 自動交易機器人設計文檔

## 📋 目錄
- [系統架構設計](#系統架構設計)
- [Redis 連線架構](#redis-連線架構)
- [定時運行設計](#定時運行設計)
- [交易機器人邏輯流程](#交易機器人邏輯流程)
- [Redis 數據結構設計](#redis-數據結構設計)
- [交易策略示例](#交易策略示例)
- [監控與告警](#監控與告警)
- [成本估算](#成本估算)
- [部署步驟概要](#部署步驟概要)
- [重要注意事項](#重要注意事項)

---

## 🏗️ 系統架構設計

### 核心組件

```
┌─────────────────────────────────────────────┐
│           Cloud Scheduler (定時觸發)          │
│         每分鐘/每5分鐘/自定義時間              │
└──────────────────┬──────────────────────────┘
                   │ HTTP POST
                   ↓
┌─────────────────────────────────────────────┐
│           Cloud Run Service                 │
│  ┌─────────────────────────────────────┐   │
│  │   交易機器人主程序                    │   │
│  │  - 接收 Scheduler 觸發                │   │
│  │  - 執行交易邏輯                       │   │
│  │  - 處理訂單                          │   │
│  └─────────────────────────────────────┘   │
└──────────┬──────────────────┬───────────────┘
           │                  │
           ↓                  ↓
┌──────────────────┐   ┌──────────────────┐
│  Redis (Memorystore) │   │  MEXC API v3     │
│  - 交易狀態          │   │  - 市場數據       │
│  - 價格歷史          │   │  - 下單/查詢      │
│  - 持倉信息          │   │  - 餘額查詢       │
└──────────────────┘   └──────────────────┘
           │
           ↓
┌──────────────────────────────────────────────┐
│           Firestore (可選)                    │
│  - 長期交易記錄                               │
│  - 策略配置                                   │
│  - 性能統計                                   │
└──────────────────────────────────────────────┘
```

---

## 🔌 Redis 連線架構

### 完整連線架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                        GCP Project                          │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │              VPC Network (自訂網路)                  │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │     Serverless VPC Access Connector          │  │   │
│  │  │     (us-central1)                            │  │   │
│  │  │     - IP Range: 10.8.0.0/28                  │  │   │
│  │  │     - Min Instances: 2                       │  │   │
│  │  │     - Max Instances: 10                      │  │   │
│  │  └──────────────┬───────────────────────────────┘  │   │
│  │                 │                                    │   │
│  │                 │ 內網連線                           │   │
│  │                 ↓                                    │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │         Cloud Run Service                    │  │   │
│  │  │  ┌────────────────────────────────────────┐ │  │   │
│  │  │  │     Container Instance                 │ │  │   │
│  │  │  │                                        │ │  │   │
│  │  │  │  ┌──────────────────────────────────┐ │ │  │   │
│  │  │  │  │   Redis Client Library           │ │ │  │   │
│  │  │  │  │   (ioredis / redis-py)           │ │ │  │   │
│  │  │  │  │                                  │ │ │  │   │
│  │  │  │  │  - Connection Pool: 5-10        │ │ │  │   │
│  │  │  │  │  - Timeout: 5s                  │ │ │  │   │
│  │  │  │  │  - Retry: 3 次                  │ │ │  │   │
│  │  │  │  │  - Keep-alive: 60s              │ │ │  │   │
│  │  │  │  └───────────┬──────────────────────┘ │ │  │   │
│  │  │  │              │                         │ │  │   │
│  │  │  │              │ Redis 命令              │ │  │   │
│  │  │  │              ↓                         │ │  │   │
│  │  │  └──────────────────────────────────────┘ │  │   │
│  │  └──────────────┼───────────────────────────┘  │   │
│  │                 │                                │   │
│  │                 │ 通過 VPC Connector              │   │
│  │                 ↓                                │   │
│  │  ┌──────────────────────────────────────────────┐  │   │
│  │  │   Memorystore for Redis (Managed)           │  │   │
│  │  │                                              │  │   │
│  │  │   實例詳情:                                   │  │   │
│  │  │   - 層級: Basic (單節點)                     │  │   │
│  │  │   - 記憶體: 1GB                              │  │   │
│  │  │   - 區域: us-central1-a                     │  │   │
│  │  │   - 版本: Redis 7.0                         │  │   │
│  │  │   - IP: 10.0.0.3 (內網)                     │  │   │
│  │  │   - Port: 6379                              │  │   │
│  │  │   - 密碼認證: 啟用                           │  │   │
│  │  │                                              │  │   │
│  │  │   ┌──────────────────────────────────────┐  │  │   │
│  │  │   │        Redis Data Structure          │  │  │   │
│  │  │   │                                      │  │  │   │
│  │  │   │  Keys:                               │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:status             │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:position           │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:price:latest       │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:price:history      │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:indicators:ma      │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:indicators:rsi     │  │  │   │
│  │  │   │  ├─ bot:qrl-usdt:trades:today       │  │  │   │
│  │  │   │  └─ bot:qrl-usdt:last-trade         │  │  │   │
│  │  │   │                                      │  │  │   │
│  │  │   └──────────────────────────────────────┘  │  │   │
│  │  └──────────────────────────────────────────────┘  │   │
│  │                                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  外部連線:                                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Cloud Run ──HTTPS──> MEXC API (api.mexc.com)        │  │
│  │                       - 市場數據 API                   │  │
│  │                       - 交易 API                       │  │
│  │                       - 帳戶 API                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Redis 連線配置詳解

#### 1. VPC Connector 配置

**作用:** 讓 Cloud Run (無伺服器) 可以訪問 VPC 內的 Redis

```yaml
資源配置:
  名稱: trading-bot-connector
  區域: us-central1
  網路: default (或自訂 VPC)
  IP 範圍: 10.8.0.0/28
  
擴展設定:
  最小實例數: 2
  最大實例數: 10
  機器類型: e2-micro
  
連線限制:
  最大吞吐量: 300 Mbps (每個實例)
  並發連線: 1000
```

#### 2. Redis 連線池設定

**Node.js (ioredis) 範例配置:**

```typescript
{
  host: '10.0.0.3',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  
  // 連線池設定
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 50, 2000),
  
  // 連線保持
  enableReadyCheck: true,
  keepAlive: 60000,
  
  // 超時設定
  connectTimeout: 5000,
  commandTimeout: 3000,
  
  // 連線池大小
  lazyConnect: false,
  db: 0
}
```

**Python (redis-py) 範例配置:**

```python
{
    'host': '10.0.0.3',
    'port': 6379,
    'password': os.getenv('REDIS_PASSWORD'),
    'db': 0,
    
    # 連線池設定
    'max_connections': 10,
    'socket_connect_timeout': 5,
    'socket_timeout': 3,
    'socket_keepalive': True,
    'socket_keepalive_options': {
        socket.TCP_KEEPIDLE: 60,
        socket.TCP_KEEPINTVL: 10,
        socket.TCP_KEEPCNT: 3
    },
    
    # 重試策略
    'retry_on_timeout': True,
    'retry': Retry(ExponentialBackoff(), 3)
}
```

#### 3. 連線生命週期

```
Cloud Run 容器啟動
  ↓
初始化 Redis 連線池 (2-5個連線)
  ↓
執行 PING 命令驗證連線
  ↓
[交易循環開始]
  ↓
從連線池取得連線
  ↓
執行 Redis 命令 (GET/SET/LPUSH 等)
  ↓
命令執行完成,連線返回池
  ↓
[交易循環結束]
  ↓
HTTP 請求完成,返回響應
  ↓
容器閒置 (保持連線池活躍)
  ↓
15分鐘無請求 → 容器自動銷毀
```

#### 4. 連線錯誤處理

```
Redis 命令執行
  ↓
[命令超時/連線斷開]
  ↓
重試機制 (Retry 1)
  ├─ 等待 50ms
  └─ 重新執行命令
  ↓
[仍然失敗]
  ↓
重試機制 (Retry 2)
  ├─ 等待 100ms
  └─ 重新執行命令
  ↓
[仍然失敗]
  ↓
重試機制 (Retry 3)
  ├─ 等待 150ms
  └─ 重新執行命令
  ↓
[最終失敗]
  ↓
記錄錯誤到 Cloud Logging
  ↓
返回降級響應 (使用 Firestore 備份數據)
  ↓
發送告警通知
```

### Redis 性能優化

#### 連線池最佳實踐

| 場景 | 連線池大小 | 原因 |
|------|-----------|------|
| 低頻交易 (>5分鐘) | 2-3 | 減少資源消耗 |
| 中頻交易 (1-5分鐘) | 5-10 | 平衡性能與成本 |
| 高頻交易 (<1分鐘) | 10-20 | 最大化吞吐量 |

#### 命令優化建議

1. **批次操作:** 使用 Pipeline 減少往返次數
   ```
   單個命令: 3 次往返 = 15ms
   Pipeline:  1 次往返 = 5ms (3倍速度提升)
   ```

2. **數據結構選擇:**
   - 價格歷史: 使用 `LPUSH` + `LTRIM` (List)
   - 持倉狀態: 使用 `HSET` (Hash)
   - 交易計數: 使用 `INCR` + `EXPIRE` (String)

3. **TTL 策略:**
   - 實時數據: 5分鐘
   - 歷史數據: 1小時
   - 統計數據: 24小時

---

## ⚙️ 定時運行設計

### 方案一: Cloud Scheduler (推薦)

**優點:**
- GCP 原生服務,免管理
- 精確的 Cron 表達式
- 自動重試機制
- 成本低廉

**配置示例:**

```yaml
觸發頻率選項:
  高頻交易: "*/1 * * * *"     # 每分鐘
  中頻交易: "*/5 * * * *"     # 每5分鐘
  低頻交易: "*/15 * * * *"    # 每15分鐘
  自定義:   "0 */4 * * *"     # 每4小時
  
HTTP 目標設定:
  URL: https://trading-bot-xxxxxx.run.app/execute
  方法: POST
  標頭:
    - Content-Type: application/json
  Body:
    {
      "pair": "QRL/USDT",
      "strategy": "ma-crossover"
    }
  
重試設定:
  最大重試: 3
  重試間隔: 1分鐘
  超時時間: 60秒
```

**工作流程:**

```
Cloud Scheduler (每分鐘觸發)
  ↓
發送 HTTP POST 到 Cloud Run
  ↓
Cloud Run 容器啟動 (冷啟動 <1秒)
  ↓
執行交易邏輯 (5-30秒)
  ↓
返回 HTTP 200 響應
  ↓
容器保持活躍 15分鐘
  ↓
無新請求 → 自動縮容到 0
```

### 方案二: Cloud Run Jobs (批次任務)

**優點:**
- 適合長時間運行的分析任務
- 可以手動觸發
- 更好的日誌管理

**使用場景:**
- 每日策略回測
- 市場數據分析
- 週期性倉位調整

**配置範例:**

```yaml
Job 名稱: daily-market-analysis
執行頻率: "0 0 * * *"  # 每日凌晨
超時時間: 3600s (1小時)
並行數: 1
重試次數: 2

任務:
  - 下載過去24小時數據
  - 計算技術指標
  - 生成交易信號
  - 更新策略參數
```

---

## 🔄 交易機器人邏輯流程

### 完整執行流程 (20秒內完成)

#### Phase 1: 啟動階段 (0-2秒)

```
接收 Scheduler HTTP 請求
  ↓
驗證請求來源 (檢查 Authorization Header)
  ↓
從 Redis 載入機器人狀態
  ├─ GET bot:qrl-usdt:status
  └─ 如果 = "paused" → 直接返回
  ↓
初始化 MEXC API 客戶端
  ├─ 載入 API Key (Secret Manager)
  └─ 測試連線 (ping API)
```

#### Phase 2: 數據採集 (2-5秒)

```
並行請求 MEXC API:
  ├─ GET /api/v3/ticker/24hr?symbol=QRLUSDT
  │   → 取得最新價格、24小時成交量
  │
  ├─ GET /api/v3/account
  │   → 取得帳戶餘額 (USDT, QRL)
  │
  └─ GET /api/v3/openOrders?symbol=QRLUSDT
      → 取得當前掛單
  ↓
數據寫入 Redis (Pipeline 批次寫入):
  ├─ SET bot:qrl-usdt:price:latest {price} EX 300
  ├─ LPUSH bot:qrl-usdt:price:history {price}
  ├─ LTRIM bot:qrl-usdt:price:history 0 99
  ├─ HSET bot:qrl-usdt:balance usdt {usdt_amount}
  └─ HSET bot:qrl-usdt:balance qrl {qrl_amount}
```

#### Phase 3: 策略判斷 (5-8秒)

```
從 Redis 讀取歷史數據:
  ├─ LRANGE bot:qrl-usdt:price:history 0 99
  └─ GET bot:qrl-usdt:position
  ↓
計算技術指標:
  ├─ MA(5) = SUM(最近5個價格) / 5
  ├─ MA(20) = SUM(最近20個價格) / 20
  ├─ RSI(14) = 100 - (100 / (1 + RS))
  └─ MACD = EMA(12) - EMA(26)
  ↓
存儲指標到 Redis:
  ├─ SET bot:qrl-usdt:indicators:ma5 {value}
  ├─ SET bot:qrl-usdt:indicators:ma20 {value}
  └─ SET bot:qrl-usdt:indicators:rsi {value}
  ↓
生成交易信號:
  IF (MA5 > MA20) AND (前次 MA5 < MA20):
    信號 = BUY
  ELSE IF (MA5 < MA20) AND (前次 MA5 > MA20):
    信號 = SELL
  ELSE:
    信號 = HOLD
```

#### Phase 4: 風險控制 (8-10秒)

```
風險檢查清單:
  ├─ 檢查 1: 餘額是否足夠?
  │   └─ IF USDT餘額 < 10 → 取消交易
  │
  ├─ 檢查 2: 今日交易次數限制
  │   ├─ GET bot:qrl-usdt:trades:today
  │   └─ IF 次數 >= 5 → 取消交易
  │
  ├─ 檢查 3: 倉位限制
  │   ├─ 計算當前持倉佔總資產比例
  │   └─ IF 比例 > 30% → 降低交易量
  │
  ├─ 檢查 4: 價格波動檢查
  │   ├─ 計算最近5分鐘波動率
  │   └─ IF 波動率 > 5% → 暫停交易
  │
  └─ 檢查 5: 冷卻期
      ├─ GET bot:qrl-usdt:last-trade
      └─ IF 距離上次交易 < 3分鐘 → 取消交易
  ↓
計算訂單數量:
  IF 信號 = BUY:
    交易金額 = MIN(USDT餘額 * 0.1, 50 USDT)
    QRL數量 = 交易金額 / 當前價格
  ELSE IF 信號 = SELL:
    QRL數量 = QRL餘額 * 0.5
```

#### Phase 5: 執行交易 (10-15秒)

```
IF 信號 = BUY:
  ├─ 準備訂單參數:
  │   {
  │     symbol: "QRLUSDT",
  │     side: "BUY",
  │     type: "MARKET",
  │     quantity: {計算出的數量}
  │   }
  │
  ├─ POST /api/v3/order 下單
  │   ├─ 等待 API 響應 (1-3秒)
  │   └─ 取得 orderId
  │
  ├─ 輪詢訂單狀態 (最多5次):
  │   └─ GET /api/v3/order?orderId={orderId}
  │       └─ 直到 status = "FILLED"
  │
  └─ 更新 Redis 持倉:
      ├─ HSET bot:qrl-usdt:position avg_price {成交價}
      ├─ HSET bot:qrl-usdt:position quantity {數量}
      ├─ SET bot:qrl-usdt:last-trade {timestamp}
      └─ INCR bot:qrl-usdt:trades:today
  ↓
ELSE IF 信號 = SELL:
  └─ (同上,但 side = "SELL")
  ↓
ELSE (HOLD):
  └─ 記錄日誌: "無交易信號,保持持有"
```

#### Phase 6: 記錄與清理 (15-20秒)

```
計算本次交易盈虧:
  IF 有成交:
    盈虧 = (賣出價 - 買入價) * 數量 - 手續費
  ↓
更新統計數據 (Redis):
  ├─ HINCRBY bot:qrl-usdt:stats total_trades 1
  ├─ HINCRBYFLOAT bot:qrl-usdt:stats total_pnl {盈虧}
  └─ HSET bot:qrl-usdt:stats last_update {timestamp}
  ↓
寫入長期記錄 (Firestore):
  Collection: trades
  Document: {
    timestamp: "2025-12-27T10:30:00Z",
    pair: "QRL/USDT",
    side: "BUY",
    price: 0.1234,
    quantity: 100,
    fee: 0.05,
    pnl: 1.23,
    strategy: "ma-crossover"
  }
  ↓
發送通知 (可選):
  IF 交易成功:
    └─ 發送 Telegram 訊息:
        "✅ 買入 100 QRL @ 0.1234
        💰 帳戶餘額: 450 USDT"
  ↓
返回 HTTP 200 響應:
  {
    "status": "success",
    "signal": "BUY",
    "executed": true,
    "price": 0.1234,
    "quantity": 100,
    "execution_time": "18.5s"
  }
```

---

## 💾 Redis 數據結構設計

### Key 命名規範

#### 1. 系統狀態類

```redis
# 機器人運行狀態
bot:qrl-usdt:status
類型: String
值: "running" | "paused" | "error"
TTL: 無 (永久)

# 最後心跳時間
bot:qrl-usdt:heartbeat
類型: String
值: Unix timestamp
TTL: 300秒 (5分鐘)
```

#### 2. 價格數據類

```redis
# 最新價格
bot:qrl-usdt:price:latest
類型: String
值: "0.1234"
TTL: 300秒 (5分鐘)
範例: SET bot:qrl-usdt:price:latest "0.1234" EX 300

# 價格歷史 (最多100條)
bot:qrl-usdt:price:history
類型: List
值: ["0.1234", "0.1235", "0.1233", ...]
操作:
  - LPUSH bot:qrl-usdt:price:history "0.1234"
  - LTRIM bot:qrl-usdt:price:history 0 99
  - LRANGE bot:qrl-usdt:price:history 0 19  # 取最近20條

# 價格時間戳記錄
bot:qrl-usdt:price:timestamps
類型: List
值: ["1735294200", "1735294260", ...]
操作: 與 price:history 同步維護
```

#### 3. 帳戶數據類

```redis
# 帳戶餘額 (Hash結構)
bot:qrl-usdt:balance
類型: Hash
欄位:
  - usdt: "450.25"
  - qrl: "1000.00"
  - total_value: "550.75"  # USDT等值
操作:
  - HSET bot:qrl-usdt:balance usdt "450.25"
  - HGET bot:qrl-usdt:balance usdt
  - HGETALL bot:qrl-usdt:balance

# 當前持倉 (Hash結構)
bot:qrl-usdt:position
類型: Hash
欄位:
  - quantity: "1000.00"      # 持有數量
  - avg_price: "0.1234"      # 平均成本
  - total_cost: "123.40"     # 總成本
  - unrealized_pnl: "12.34"  # 未實現盈虧
操作:
  - HSET bot:qrl-usdt:position quantity "1000"
  - HMGET bot:qrl-usdt:position quantity avg_price
```

#### 4. 技術指標類

```redis
# 移動平均線
bot:qrl-usdt:indicators:ma5
bot:qrl-usdt:indicators:ma20
bot:qrl-usdt:indicators:ma50
類型: String
值: "0.1234"
TTL: 600秒 (10分鐘)

# RSI 指標
bot:qrl-usdt:indicators:rsi
類型: String
值: "65.43"
TTL: 600秒

# MACD 指標
bot:qrl-usdt:indicators:macd
類型: Hash
欄位:
  - macd: "0.0012"
  - signal: "0.0010"
  - histogram: "0.0002"
TTL: 600秒
```

#### 5. 交易記錄類

```redis
# 今日交易次數
bot:qrl-usdt:trades:today
類型: String (Counter)
值: "3"
TTL: 到當日午夜 (使用 EXPIREAT)
操作:
  - INCR bot:qrl-usdt:trades:today
  - EXPIREAT bot:qrl-usdt:trades:today {midnight_timestamp}

# 最後交易時間
bot:qrl-usdt:last-trade
類型: String
值: "1735294200"  # Unix timestamp
TTL: 無

# 最後交易詳情
bot:qrl-usdt:last-trade:detail
類型: Hash
欄位:
  - side: "BUY"
  - price: "0.1234"
  - quantity: "100"
  - fee: "0.05"
  - timestamp: "1735294200"
TTL: 86400秒 (24小時)
```

#### 6. 統計數據類

```redis
# 統計數據 (Hash結構)
bot:qrl-usdt:stats
類型: Hash
欄位:
  - total_trades: "127"          # 總交易次數
  - total_pnl: "45.67"          # 總盈虧
  - win_trades: "78"            # 盈利交易數
  - loss_trades: "49"           # 虧損交易數
  - win_rate: "0.6141"          # 勝率
  - max_drawdown: "-12.34"      # 最大回撤
  - last_update: "1735294200"   # 最後更新時間
TTL: 無 (永久保存)

# 每日統計 (按日期分割)
bot:qrl-usdt:stats:2025-12-27
類型: Hash
欄位: (同上,但僅針對當日)
TTL: 2592000秒 (30天)
```

#### 7. 風控數據類

```redis
# 冷卻期標記
bot:qrl-usdt:cooldown
類型: String
值: "1"
TTL: 180秒 (3分鐘冷卻期)
操作:
  - SETEX bot:qrl-usdt:cooldown 180 "1"
  - EXISTS bot:qrl-usdt:cooldown  # 檢查是否在冷卻期

# 連續虧損次數
bot:qrl-usdt:consecutive-losses
類型: String
值: "2"
TTL: 無 (手動重置)

# 每日虧損額
bot:qrl-usdt:daily-loss
類型: String
值: "-15.23"
TTL: 到當日午夜
```

### 完整操作範例

#### 寫入價格數據 (Pipeline 批次操作)

```python
pipe = redis.pipeline()

# 1. 更新最新價格
pipe.set('bot:qrl-usdt:price:latest', '0.1234', ex=300)

# 2. 添加到歷史記錄
pipe.lpush('bot:qrl-usdt:price:history', '0.1234')
pipe.ltrim('bot:qrl-usdt:price:history', 0, 99)

# 3. 添加時間戳
pipe.lpush('bot:qrl-usdt:price:timestamps', '1735294200')
pipe.ltrim('bot:qrl-usdt:price:timestamps', 0, 99)

# 4. 更新心跳
pipe.set('bot:qrl-usdt:heartbeat', '1735294200', ex=300)

# 執行所有命令 (僅1次網路往返)
pipe.execute()
```

#### 讀取完整狀態

```python
# 使用 Pipeline 批次讀取
pipe = redis.pipeline()

pipe.get('bot:qrl-usdt:status')
pipe.get('bot:qrl-usdt:price:latest')
pipe.lrange('bot:qrl-usdt:price:history', 0, 19)
pipe.hgetall('bot:qrl-usdt:balance')
pipe.hgetall('bot:qrl-usdt:position')
pipe.get('bot:qrl-usdt:trades:today')
pipe.hgetall('bot:qrl-usdt:stats')

results = pipe.execute()

# 解析結果
state = {
    'status': results[0],
    'latest_price': float(results[1]),
    'price_history': [float(p) for p in results[2]],
    'balance': results[3],
    'position': results[4],
    'trades_today': int(results[5] or 0),
    'stats': results[6]
}
```

---

## 🎯 交易策略示例

### 策略 1: 簡單移動平均線交叉 (MA Crossover)

#### 策略邏輯

```
進場條件 (買入):
  1. MA(5) 從下方突破 MA(20)
  2. RSI > 30 (不在超賣區)
  3. 成交量 > 平均成交量的 1.2倍
  4. 帳戶 USDT 餘額 >= 10

出場條件 (賣出):
  1. MA(5) 從上方跌破 MA(20)
  OR
  2. 價格達到止盈目標 (+5%)
  OR
  3. 價格達到止損目標 (-3%)

持有條件:
  - MA(5) 與 MA(20) 未發生交叉
  - 停損/停利未觸發
```

#### 風控參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 單筆最大投入 | 帳戶的 10% | 降低單次風險 |
| 止損比例 | -3% | 虧損3%自動賣出 |
| 止盈比例 | +5% | 盈利5%自動賣出 |
| 每日最大交易次數 | 5次 | 避免過度交易 |
| 冷卻期 | 3分鐘 | 避免頻繁交易 |
| 最大倉位 | 總資產的 30% | 保留流動性 |

#### 實作偽代碼

```python
def ma_crossover_strategy():
    # 1. 取得數據
    prices = redis.lrange('bot:qrl-usdt:price:history', 0, 49)
    
    # 2. 計算指標
    ma5 = calculate_ma(prices[:5])
    ma20 = calculate_ma(prices[:20])
    prev_ma5 = calculate_ma(prices[1:6])
    prev_ma20 = calculate_ma(prices[1:21])
    
    rsi = calculate_rsi(prices[:14])
    volume = get_current_volume()
    avg_volume = calculate_average_volume()
    
    # 3. 檢查交叉
    bullish_cross = (ma5 > ma20) and (prev_ma5 <= prev_ma20)
    bearish_cross = (ma5 < ma20) and (prev_ma5 >= prev_ma20)
    
    # 4. 生成信號
    if bullish_cross and rsi > 30 and volume > avg_volume * 1.2:
        return "BUY"
    elif bearish_cross:
        return "SELL"
    else:
        # 檢查止盈止損
        position = redis.hgetall('bot:qrl-usdt:position')
        if position:
            current_price = float(redis.get('bot:qrl-usdt:price:latest'))
            avg_price = float(position['avg_price'])
            pnl_percent = (current_price - avg_price) / avg_price * 100
            
            if pnl_percent >= 5:
                return "SELL"  # 止盈
            elif pnl_percent <= -3:
                return "SELL"  # 止損
        
        return "HOLD"
```

### 策略 2: RSI 超買超賣

#### 策略邏輯

```
進場條件 (買入):
  1. RSI(14) < 30 (超賣區)
  2. 價格連續3根K線下跌
  3. 價格跌破下軌 Bollinger Band

出場條件 (賣出):
  1. RSI(14) > 70 (超買區)
  2. 價格連續3根K線上漲
  3. 價格突破上軌 Bollinger Band

持有條件:
  - 30 <= RSI <= 70 (中性區)
```

#### 風控參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 單筆最大投入 | 帳戶的 15% | 稍微激進 |
| 止損比例 | -2% | 較緊的止損 |
| 止盈比例 | +4% | 快速獲利了結 |
| 每日最大交易次數 | 10次 | 允許更多交易 |
| 連續虧損停止 | 3次 | 連虧3次暫停 |
| 單日最大虧損 | -5% | 達到後暫停當日交易 |

#### 實作偽代碼

```python
def rsi_strategy():
    # 1. 取得數據
    prices = redis.lrange('bot:qrl-usdt:price:history', 0, 19)
    
    # 2. 計算指標
    rsi = calculate_rsi(prices[:14])
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices[:20])
    current_price = float(prices[0])
    
    # 3. 檢查趨勢
    last_3_prices = [float(p) for p in prices[:3]]
    is_falling = all(last_3_prices[i] > last_3_prices[i+1] 
                     for i in range(len(last_3_prices)-1))
    is_rising = all(last_3_prices[i] < last_3_prices[i+1] 
                    for i in range(len(last_3_prices)-1))
    
    # 4. 生成信號
    if rsi < 30 and is_falling and current_price < bb_lower:
        return "BUY"
    elif rsi > 70 and is_rising and current_price > bb_upper:
        return "SELL"
    else:
        return "HOLD"
```

### 策略 3: 網格交易 (Grid Trading)

#### 策略邏輯

```
設定價格網格:
  基準價: 0.1200
  網格間距: 2%
  上限: 0.1560 (+30%)
  下限: 0.0960 (-20%)
  
  網格價位:
  [0.0960, 0.0979, 0.0999, 0.1019, 0.1039, 
   0.1200,  # 基準價
   0.1224, 0.1248, 0.1273, 0.1298, 0.1560]

交易規則:
  - 價格下跌到網格線 → 買入固定金額
  - 價格上漲到網格線 → 賣出固定數量
  - 每個網格只交易一次
  - 所有網格重置時重新開始
```

#### 風控參數

| 參數 | 值 | 說明 |
|------|-----|------|
| 總投入資金 | 100 USDT | 分散到各網格 |
| 每格投入 | 10 USDT | 10個網格 |
| 網格間距 | 2% | 平衡頻率與收益 |
| 重置條件 | 價格突破上下限 | 重新設定網格 |

---

## 📊 監控與告警

### 需要監控的指標

#### 1. 系統健康指標

```
監控項目:
├─ Cloud Run 實例狀態
│  ├─ 啟動成功率: > 99%
│  ├─ 平均啟動時間: < 2秒
│  └─ 記憶體使用率: < 80%
│
├─ Redis 連線狀態
│  ├─ 連線成功率: > 99.9%
│  ├─ 平均延遲: < 5ms
│  └─ 連線池使用率: < 80%
│
├─ MEXC API 健康度
│  ├─ API 響應時間: < 1秒
│  ├─ API 錯誤率: < 1%
│  └─ 速率限制狀況: < 80%
│
└─ Cloud Scheduler 執行
   ├─ 觸發準時率: > 99%
   └─ 執行成功率: > 98%
```

#### 2. 交易性能指標

```
監控項目:
├─ 今日盈虧
│  └─ 實時計算,每次交易更新
│
├─ 累計盈虧
│  └─ 從啟動至今的總盈虧
│
├─ 勝率
│  └─ 盈利交易數 / 總交易數 * 100%
│
├─ 平均盈虧
│  ├─ 平均每筆盈利
│  └─ 平均每筆虧損
│
├─ 盈虧比
│  └─ 平均盈利 / 平均虧損
│
├─ 交易頻率
│  ├─ 每日交易次數
│  └─ 平均交易間隔
│
└─ 持倉時間
   ├─ 平均持倉時長
   └─ 最長持倉時長
```

#### 3. 風險指標

```
監控項目:
├─ 當前倉位
│  ├─ QRL 持有數量
│  └─ 佔總資產比例
│
├─ 最大回撤
│  └─ 從最高點到最低點的跌幅
│
├─ 連續虧損次數
│  └─ 連續虧損交易的次數
│
├─ 單日虧損額
│  └─ 當日累計虧損金額
│
├─ 餘額警報
│  ├─ USDT 餘額 < 10
│  └─ 總資產 < 初始資產的 80%
│
└─ 波動率
   └─ 最近24小時價格波動率
```

### 告警設定

#### Cloud Monitoring 告警策略

```yaml
告警 1: API 連線失敗
條件:
  - MEXC API 連續失敗 >= 3次
  - 時間窗口: 5分鐘
嚴重性: Critical
通知管道:
  - Email
  - Telegram
行動:
  - 暫停機器人
  - 記錄錯誤日誌

告警 2: 單日虧損超限
條件:
  - 單日虧損 >= 初始資產的 5%
嚴重性: Critical
通知管道:
  - Email
  - Telegram
  - SMS
行動:
  - 立即停止交易
  - 平倉所有持倉

告警 3: Redis 連線中斷
條件:
  - Redis 心跳超時 > 5分鐘
嚴重性: High
通知管道:
  - Email
行動:
  - 嘗試重新連線
  - 切換到 Firestore 備份

告警 4: 餘額不足
條件:
  - USDT 餘額 < 10
嚴重性: Medium
通知管道:
  - Email
行動:
  - 停止開新倉
  - 僅允許平倉操作

告警 5: 連續虧損
條件:
  - 連續虧損 >= 3次
嚴重性: Medium
通知管道:
  - Telegram
行動:
  - 暫停交易 1小時
  - 等待人工確認

告警 6: 異常波動
條件:
  - 10分鐘內價格波動 > 10%
嚴重性: Low
通知管道:
  - Telegram
行動:
  - 記錄事件
  - 繼續監控
```

### 監控儀表板設計

#### Dashboard 1: 即時交易監控

```
┌─────────────────────────────────────────────────┐
│  QRL/USDT 自動交易機器人 - 即時監控               │
├─────────────────────────────────────────────────┤
│                                                 │
│  當前狀態: ● 運行中        最後更新: 2秒前        │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │  當前價格     │  │  24h 變化    │           │
│  │  0.1234      │  │  +2.34%      │           │
│  │  USDT        │  │  ↑           │           │
│  └──────────────┘  └──────────────┘           │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │  價格走勢 (最近1小時)                      │  │
│  │                                            │  │
│  │  0.125 │              ╱╲                  │  │
│  │  0.124 │           ╱╲╱  ╲                 │  │
│  │  0.123 │        ╱╲╱      ╲╱╲              │  │
│  │  0.122 │     ╱╲╱              ╲          │  │
│  │        └────────────────────────────      │  │
│  │        10:00  10:15  10:30  10:45         │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  帳戶資訊                                        │
│  ├─ USDT 餘額: 450.25                          │
│  ├─ QRL 餘額: 1,000.00                         │
│  ├─ 總資產: 573.65 USDT                        │
│  └─ 持倉佔比: 21.5%                            │
│                                                 │
│  今日統計                                        │
│  ├─ 交易次數: 3 / 5                            │
│  ├─ 盈利交易: 2                                │
│  ├─ 虧損交易: 1                                │
│  ├─ 今日盈虧: +5.23 USDT (+0.91%)             │
│  └─ 勝率: 66.7%                                │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### Dashboard 2: 系統健康監控

```
┌─────────────────────────────────────────────────┐
│  系統健康監控                                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  Cloud Run                                      │
│  ├─ 狀態: ✓ 正常                               │
│  ├─ 實例數: 1                                   │
│  ├─ CPU: 15%                                    │
│  ├─ 記憶體: 120MB / 512MB (23%)                │
│  └─ 平均響應時間: 1.2秒                        │
│                                                 │
│  Redis (Memorystore)                            │
│  ├─ 狀態: ✓ 正常                               │
│  ├─ 延遲: 2.3ms                                │
│  ├─ 連線數: 3 / 10                             │
│  ├─ 記憶體使用: 45MB / 1GB (4.5%)              │
│  └─ 命中率: 98.5%                              │
│                                                 │
│  MEXC API                                       │
│  ├─ 狀態: ✓ 正常                               │
│  ├─ 平均響應: 850ms                            │
│  ├─ 成功率: 99.2%                              │
│  ├─ 今日請求: 287                              │
│  └─ 速率限制: 287 / 1200 (23.9%)               │
│                                                 │
│  Cloud Scheduler                                │
│  ├─ 狀態: ✓ 正常                               │
│  ├─ 今日觸發: 145 / 145                        │
│  ├─ 成功率: 100%                               │
│  └─ 下次執行: 30秒後                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 通知範例

#### Telegram 通知格式

```
📊 QRL/USDT 交易通知

✅ 交易類型: 買入
💰 數量: 100 QRL
💵 價格: 0.1234 USDT
📈 總金額: 12.34 USDT
⏰ 時間: 2025-12-27 10:30:15

帳戶狀態:
├─ USDT: 437.91
├─ QRL: 1,100.00
└─ 總資產: 573.65 USDT

策略: MA交叉 (MA5 上穿 MA20)
```

---

## 💰 成本估算 (每月)

### 詳細成本分析

#### 1. Cloud Run

```yaml
使用場景: 每分鐘觸發一次交易檢查

計費項目:
  CPU 時間:
    - 執行時間: 20秒/次
    - 每月次數: 60 * 24 * 30 = 43,200次
    - 總 CPU 時間: 43,200 * 20 = 864,000秒 = 240 CPU小時
    - 單價: $0.00002400 / vCPU秒
    - 成本: 864,000 * 0.00002400 = $20.74
  
  記憶體:
    - 記憶體配置: 512MB
    - 總記憶體時間: 43,200 * 20 * 0.5 = 432,000 GB秒
    - 單價: $0.00000250 / GB秒
    - 成本: 432,000 * 0.00000250 = $1.08
  
  請求數:
    - 月請求數: 43,200
    - 免費額度: 2,000,000 (不收費)
    - 成本: $0
  
  網路流出:
    - 每次響應: ~5KB
    - 總流量: 43,200 * 5KB = 216MB
    - 免費額度: 1GB (不收費)
    - 成本: $0

小計: $21.82
```

#### 2. Memorystore for Redis

```yaml
實例配置: Basic Tier, 1GB

計費項目:
  實例費用:
    - 單價: $0.049 / GB / 小時
    - 月小時數: 24 * 30 = 720小時
    - 成本: 1 * 0.049 * 720 = $35.28
  
  網路流量:
    - 同區域內網傳輸: 免費
    - 成本: $0

小計: $35.28
```

#### 3. Cloud Scheduler

```yaml
作業數: 1 個

計費項目:
  作業執行:
    - 月執行次數: 43,200
    - 免費額度: 3 個作業 (完全免費)
    - 成本: $0

小計: $0
```

#### 4. Cloud Logging

```yaml
日誌量估算:
  每次執行日誌: ~10KB
  月總日誌量: 43,200 * 10KB = 432MB

計費項目:
  日誌攝取:
    - 免費額度: 50GB (不收費)
    - 成本: $0
  
  日誌存儲:
    - 存儲時間: 30天
    - 總存儲量: 432MB * 30 = 12.96GB
    - 免費額度: 50GB (不收費)
    - 成本: $0

小計: $0
```

#### 5. Firestore (可選)

```yaml
使用場景: 存儲長期交易記錄

數據量估算:
  每筆交易記錄: ~1KB
  每日交易: 5筆
  月總數據: 5 * 30 * 1KB = 150KB

計費項目:
  存儲:
    - 月總量: 150KB
    - 單價: $0.18 / GB / 月
    - 成本: 0.00015 * 0.18 = $0.00003
  
  讀取操作:
    - 月讀取: 1,000次
    - 免費額度: 50,000 (不收費)
    - 成本: $0
  
  寫入操作:
    - 月寫入: 150次
    - 免費額度: 20,000 (不收費)
    - 成本: $0

小計: $0.00003 (可忽略)
```

#### 6. Secret Manager (存儲 API Key)

```yaml
密鑰數量: 1 個 (MEXC API Key)

計費項目:
  密鑰版本:
    - 數量: 1
    - 免費額度: 6 個 (不收費)
    - 成本: $0
  
  訪問次數:
    - 月訪問: 43,200 (每次執行讀取)
    - 免費額度: 10,000
    - 超額: 43,200 - 10,000 = 33,200
    - 單價: $0.03 / 10,000次
    - 成本: (33,200 / 10,000) * 0.03 = $0.10

小計: $0.10
```

#### 7. Cloud Monitoring (告警)

```yaml
告警策略: 6 個

計費項目:
  告警策略:
    - 免費額度: 100 個 (不收費)
    - 成本: $0
  
  指標攝取:
    - 月指標數: ~5,000 個
    - 免費額度: 150 MB (不收費)
    - 成本: $0

小計: $0
```

### 總成本彙總

| 服務 | 月費用 (USD) | 佔比 |
|------|-------------|------|
| Cloud Run | $21.82 | 38% |
| Memorystore (Redis) | $35.28 | 61% |
| Cloud Scheduler | $0 | 0% |
| Cloud Logging | $0 | 0% |
| Firestore | $0.00003 | 0% |
| Secret Manager | $0.10 | 0.2% |
| Cloud Monitoring | $0 | 0% |
| **總計** | **$57.20** | **100%** |

### 成本優化建議

#### 優化方案 1: 降低觸發頻率

```
當前: 每1分鐘觸發
優化: 改為每5分鐘觸發

節省:
├─ Cloud Run: $21.82 → $4.36 (節省 $17.46)
└─ 月總成本: $57.20 → $39.74 (節省 30%)

適用場景: 低頻交易策略
```

#### 優化方案 2: 使用 Cloud Run Jobs

```
當前: 持續運行 Service
優化: 改用 Cloud Run Jobs (僅在需要時運行)

節省:
├─ 無需 VPC Connector 常駐
└─ 按需計費,更靈活

適用場景: 每日1-2次的大批量分析任務
```

#### 優化方案 3: Redis 實例優化

```
當前: Basic Tier 1GB
優化方案:
  A. 降級至 0.5GB (如果數據量小)
     └─ $35.28 → $17.64 (節省 50%)
  
  B. 僅在交易時段運行 (如: 交易所開市時)
     └─ 自動化啟停實例
     └─ 節省 ~60% 成本

注意: Basic Tier 不支持自動縮容
```

#### 優化方案 4: 批次處理

```
當前: 每次觸發執行完整流程
優化: 將多個輕量級檢查合併

範例:
├─ 價格更新: 每1分鐘
├─ 技術指標計算: 每5分鐘
└─ 交易決策: 每15分鐘

預期節省: 40-50% Cloud Run 成本
```

---

## 🚀 部署步驟概要

### Phase 1: 基礎設施建置 (30分鐘)

#### 步驟 1.1: 建立 GCP 專案

```bash
# 1. 建立專案
gcloud projects create trading-bot-project --name="Trading Bot"

# 2. 設定為當前專案
gcloud config set project trading-bot-project

# 3. 啟用計費帳戶
gcloud beta billing projects link trading-bot-project \
  --billing-account=BILLING_ACCOUNT_ID

# 4. 啟用所需 API
gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

#### 步驟 1.2: 建立 VPC 與 Connector

```bash
# 1. 建立 VPC 網路 (如使用自訂網路)
gcloud compute networks create trading-bot-vpc \
  --subnet-mode=custom

# 2. 建立子網路
gcloud compute networks subnets create trading-bot-subnet \
  --network=trading-bot-vpc \
  --region=us-central1 \
  --range=10.0.0.0/24

# 3. 建立 Serverless VPC Access Connector
gcloud compute networks vpc-access connectors create trading-bot-connector \
  --region=us-central1 \
  --subnet=trading-bot-subnet \
  --min-instances=2 \
  --max-instances=10 \
  --machine-type=e2-micro
```

#### 步驟 1.3: 建立 Redis 實例

```bash
# 建立 Memorystore Redis 實例
gcloud redis instances create trading-bot-redis \
  --size=1 \
  --region=us-central1 \
  --zone=us-central1-a \
  --network=trading-bot-vpc \
  --redis-version=redis_7_0 \
  --tier=basic \
  --enable-auth

# 取得 Redis 連線資訊
gcloud redis instances describe trading-bot-redis \
  --region=us-central1
```

#### 步驟 1.4: 存儲 API 密鑰

```bash
# 1. 建立 Secret
echo -n "YOUR_MEXC_API_KEY" | \
  gcloud secrets create mexc-api-key --data-file=-

echo -n "YOUR_MEXC_SECRET_KEY" | \
  gcloud secrets create mexc-secret-key --data-file=-

echo -n "YOUR_REDIS_PASSWORD" | \
  gcloud secrets create redis-password --data-file=-

# 2. 授予 Cloud Run 服務帳戶訪問權限
gcloud secrets add-iam-policy-binding mexc-api-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Phase 2: 機器人開發 (2-4小時)

#### 步驟 2.1: 專案結構

```
trading-bot/
├── Dockerfile
├── requirements.txt (或 package.json)
├── .dockerignore
├── src/
│   ├── main.py (或 index.ts)
│   ├── config.py
│   ├── strategies/
│   │   ├── ma_crossover.py
│   │   └── rsi_strategy.py
│   ├── services/
│   │   ├── redis_service.py
│   │   ├── mexc_service.py
│   │   └── firestore_service.py
│   └── utils/
│       ├── indicators.py
│       └── risk_manager.py
└── tests/
    └── test_strategies.py
```

#### 步驟 2.2: Dockerfile 範例

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY src/ ./src/

# 設定環境變數
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# 啟動應用
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 60 src.main:app
```

#### 步驟 2.3: 核心程式架構 (Python 範例)

```python
# main.py
from flask import Flask, request, jsonify
import redis
from strategies import ma_crossover
from services import mexc_service, redis_service

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_trade():
    try:
        # 1. 驗證請求
        data = request.json
        
        # 2. 檢查機器人狀態
        status = redis_service.get_bot_status()
        if status == 'paused':
            return jsonify({'status': 'paused'}), 200
        
        # 3. 取得市場數據
        price_data = mexc_service.get_ticker('QRLUSDT')
        
        # 4. 執行策略
        signal = ma_crossover.analyze(price_data)
        
        # 5. 風險控制
        if should_execute(signal):
            order = mexc_service.place_order(signal)
            redis_service.update_position(order)
        
        return jsonify({
            'status': 'success',
            'signal': signal
        }), 200
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Phase 3: 部署到 Cloud Run (15分鐘)

#### 步驟 3.1: 建置並推送映像

```bash
# 1. 設定 Artifact Registry
gcloud artifacts repositories create trading-bot-repo \
  --repository-format=docker \
  --location=us-central1

# 2. 建置映像
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/trading-bot-repo/trading-bot:v1

# 或使用本地 Docker
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/trading-bot-repo/trading-bot:v1 .
docker push us-central1-docker.pkg.dev/PROJECT_ID/trading-bot-repo/trading-bot:v1
```

#### 步驟 3.2: 部署 Cloud Run Service

```bash
gcloud run deploy trading-bot \
  --image=us-central1-docker.pkg.dev/PROJECT_ID/trading-bot-repo/trading-bot:v1 \
  --platform=managed \
  --region=us-central1 \
  --vpc-connector=trading-bot-connector \
  --vpc-egress=private-ranges-only \
  --memory=512Mi \
  --cpu=1 \
  --timeout=60s \
  --min-instances=0 \
  --max-instances=1 \
  --set-env-vars="REDIS_HOST=10.0.0.3,REDIS_PORT=6379" \
  --set-secrets="MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest,REDIS_PASSWORD=redis-password:latest" \
  --no-allow-unauthenticated
```

### Phase 4: 設定 Cloud Scheduler (10分鐘)

#### 步驟 4.1: 建立服務帳戶

```bash
# 1. 建立服務帳戶
gcloud iam service-accounts create trading-bot-scheduler \
  --display-name="Trading Bot Scheduler"

# 2. 授予 Cloud Run Invoker 角色
gcloud run services add-iam-policy-binding trading-bot \
  --region=us-central1 \
  --member="serviceAccount:trading-bot-scheduler@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

#### 步驟 4.2: 建立排程作業

```bash
# 取得 Cloud Run URL
SERVICE_URL=$(gcloud run services describe trading-bot \
  --region=us-central1 \
  --format='value(status.url)')

# 建立 Scheduler 作業 (每分鐘執行)
gcloud scheduler jobs create http trading-bot-trigger \
  --location=us-central1 \
  --schedule="*/1 * * * *" \
  --uri="${SERVICE_URL}/execute" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"pair":"QRL/USDT","strategy":"ma-crossover"}' \
  --oidc-service-account-email=trading-bot-scheduler@PROJECT_ID.iam.gserviceaccount.com \
  --oidc-token-audience="${SERVICE_URL}"
```

### Phase 5: 測試與驗證 (30分鐘)

#### 測試檢查清單

```
✓ 基礎設施測試
  ├─ VPC Connector 連線正常
  ├─ Redis 實例可訪問
  └─ Cloud Run 服務可啟動

✓ API 連線測試
  ├─ MEXC API 認證成功
  ├─ 市場數據取得正常
  └─ 餘額查詢正常

✓ Redis 操作測試
  ├─ 寫入數據成功
  ├─ 讀取數據正確
  └─ TTL 設定生效

✓ 策略執行測試
  ├─ 技術指標計算正確
  ├─ 交易信號生成正常
  └─ 風險控制觸發正確

✓ 端到端測試
  ├─ Scheduler 觸發成功
  ├─ 交易流程完整執行
  └─ 日誌記錄完整

✓ 告警測試
  ├─ 錯誤告警觸發
  └─ 通知發送成功
```

#### 手動觸發測試

```bash
# 1. 手動觸發 Scheduler
gcloud scheduler jobs run trading-bot-trigger --location=us-central1

# 2. 查看日誌
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=trading-bot" \
  --limit=50 \
  --format=json

# 3. 檢查 Redis 數據
# 連接到 Redis (需要通過 Cloud Shell 或有權限的 VM)
redis-cli -h 10.0.0.3 -a YOUR_REDIS_PASSWORD
> GET bot:qrl-usdt:price:latest
> LRANGE bot:qrl-usdt:price:history 0 10
```

### Phase 6: 監控設定 (20分鐘)

#### 步驟 6.1: 建立 Dashboard

```bash
# 使用 Cloud Console 建立 Monitoring Dashboard
# 或使用 Terraform/gcloud CLI 自動化
```

#### 步驟 6.2: 設定告警策略

```bash
# 範例: CPU 使用率告警
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud Run High CPU" \
  --condition-display-name="CPU > 80%" \
  --condition-threshold-value=0.8 \
  --condition-threshold-duration=300s
```

---

## ⚠️ 重要注意事項

### 1. 安全性

#### API 密鑰管理

```
✓ 使用 Secret Manager 存儲密鑰
✗ 絕不將密鑰寫入程式碼或 Git

✓ 定期輪換 API 密鑰 (建議每30天)
✓ 使用 IP 白名單限制 API 訪問
✓ 限制 API Key 權限 (僅交易,不要提幣)
```

#### 服務帳戶權限

```
最小權限原則:
├─ Cloud Run → 僅需 Secret Accessor
├─ Scheduler → 僅需 Run Invoker
└─ Monitoring → 僅需 Metric Writer

禁止:
└─ Owner / Editor 等高權限角色
```

#### 網路安全

```
✓ Redis 僅允許 VPC 內部訪問
✓ Cloud Run 使用認證的 OIDC token
✓ 禁用 Cloud Run 的公開訪問
```

### 2. 冪等性設計

#### 問題場景

```
Scheduler 觸發 → Cloud Run 執行 → 下單成功
                                 ↓
                           但響應超時
                                 ↓
                         Scheduler 重試
                                 ↓
                          重複下單! ❌
```

#### 解決方案

```python
# 使用 Redis SETNX 實現分散式鎖
def execute_trade_with_lock():
    lock_key = f"bot:qrl-usdt:lock:{minute_timestamp}"
    
    # 嘗試獲取鎖 (60秒有效)
    if redis.set(lock_key, "1", nx=True, ex=60):
        try:
            # 執行交易邏輯
            result = perform_trading()
            return result
        finally:
            # 釋放鎖
            redis.delete(lock_key)
    else:
        # 已有實例在執行,跳過
        return {"status": "skipped", "reason": "already_running"}
```

### 3. 錯誤處理策略

#### API 錯誤處理

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置重試策略
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=1,  # 1s, 2s, 4s
    allowed_methods=["GET", "POST"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)

# 使用 session 呼叫 MEXC API
try:
    response = session.post(
        "https://api.mexc.com/api/v3/order",
        json=order_params,
        timeout=5
    )
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logging.error(f"API Error: {e}")
    # 降級處理: 記錄錯誤,不下單
    return {"status": "error", "message": str(e)}
```

#### 部分失敗處理

```python
def execute_trading_cycle():
    """
    即使某些步驟失敗,也要盡可能完成其他步驟
    """
    results = {
        'price_fetch': False,
        'balance_fetch': False,
        'signal_generated': False,
        'order_placed': False
    }
    
    # 1. 取得價格 (critical)
    try:
        price = fetch_price()
        results['price_fetch'] = True
    except Exception as e:
        logging.error(f"Price fetch failed: {e}")
        return results  # 無價格無法繼續
    
    # 2. 取得餘額 (non-critical)
    try:
        balance = fetch_balance()
        results['balance_fetch'] = True
    except Exception as e:
        logging.warning(f"Balance fetch failed: {e}")
        balance = get_cached_balance()  # 使用快取
    
    # 3. 生成信號
    try:
        signal = generate_signal(price)
        results['signal_generated'] = True
    except Exception as e:
        logging.error(f"Signal generation failed: {e}")
        return results
    
    # 4. 下單 (如果信號為 BUY/SELL)
    if signal in ['BUY', 'SELL']:
        try:
            order = place_order(signal, balance)
            results['order_placed'] = True
        except Exception as e:
            logging.error(f"Order failed: {e}")
            send_alert(f"下單失敗: {e}")
    
    return results
```

### 4. MEXC API 限制

#### 速率限制

```
MEXC API 限制 (v3):
├─ 市場數據: 20 請求/秒
├─ 帳戶查詢: 5 請求/秒
├─ 下單: 50 請求/10秒
└─ 取消訂單: 50 請求/10秒

我們的機器人 (每分鐘觸發):
├─ 市場數據: 1 請求/分鐘 ✓
├─ 帳戶查詢: 1 請求/分鐘 ✓
└─ 下單: 最多 5 請求/天 ✓

結論: 遠低於限制,安全
```

#### 實作速率限制控制

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, time_window):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # 移除超出時間窗口的記錄
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()
            
            # 檢查是否超過限制
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                logging.warning(f"Rate limit reached, sleeping {sleep_time}s")
                time.sleep(sleep_time)
            
            # 執行函數
            self.calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper

# 使用範例
@RateLimiter(max_calls=5, time_window=1)  # 每秒最多5次
def fetch_account_info():
    return mexc_api.get_account()
```

### 5. 災難恢復

#### Redis 數據備份

```bash
# 定期備份 Redis 數據到 Cloud Storage
# 使用 Cloud Scheduler 觸發

# backup.sh
redis-cli -h 10.0.0.3 -a $REDIS_PASSWORD SAVE
gsutil cp /var/lib/redis/dump.rdb \
  gs://trading-bot-backups/redis-$(date +%Y%m%d-%H%M%S).rdb
```

#### 降級策略

```python
def get_price_with_fallback():
    """
    價格獲取的降級鏈
    """
    try:
        # 1. 嘗試從 MEXC API
        return mexc_api.get_ticker('QRLUSDT')['price']
    except Exception as e:
        logging.warning(f"MEXC API failed: {e}")
        
        try:
            # 2. 嘗試從 Redis 快取
            cached = redis.get('bot:qrl-usdt:price:latest')
            if cached:
                return float(cached)
        except Exception as e:
            logging.warning(f"Redis failed: {e}")
            
            try:
                # 3. 嘗試從 Firestore 備份
                doc = firestore.collection('prices').document('latest').get()
                return doc.to_dict()['price']
            except Exception as e:
                logging.error(f"All price sources failed: {e}")
                
                # 4. 最終降級: 拒絕交易
                raise Exception("Cannot fetch price from any source")
```

### 6. 合規性與法律

#### 交易所規則

```
MEXC 規則:
✓ 遵守 API 速率限制
✓ 不得使用自動化程序操縱市場
✓ 禁止套利/搶先交易
✓ 需要通過 KYC 驗證

我們的機器人:
✓ 僅自動化個人交易決策
✓ 無市場操縱行為
✓ 遵守所有 API 限制
```

#### 稅務考量

```
重要提醒:
├─ 記錄所有交易用於報稅
├─ 加密貨幣交易可能需要繳稅
├─ 諮詢當地稅務專業人士
└─ Firestore 記錄可作為稅務憑證
```

#### 風險聲明

```
⚠️ 風險警告:
1. 加密貨幣交易有高度風險
2. 自動交易機器人可能虧損
3. 過去表現不代表未來結果
4. 僅投入可承受損失的資金
5. 定期監控機器人運作
6. 建議從小額開始測試
```

---

## 📚 延伸閱讀

### 技術文檔

- [Cloud Run 官方文檔](https://cloud.google.com/run/docs)
- [Memorystore for Redis 文檔](https://cloud.google.com/memorystore/docs/redis)
- [MEXC API v3 文檔](https://mexcdevelop.github.io/apidocs/spot_v3_en/)
- [Cloud Scheduler 文檔](https://cloud.google.com/scheduler/docs)

### 交易策略

- [TradingView 技術分析教學](https://www.tradingview.com/wiki/)
- [量化交易策略](https://www.quantstart.com/)
- [Python 量化交易框架](https://github.com/quantopian/zipline)

### 最佳實踐

- [Google Cloud 架構中心](https://cloud.google.com/architecture)
- [微服務設計模式](https://microservices.io/patterns/)
- [Redis 最佳實踐](https://redis.io/docs/manual/patterns/)

---

## 📞 支援與協助

如需進一步協助,請聯繫:
- 技術問題: support@example.com
- 策略諮詢: trading@example.com

---

**文檔版本:** 1.0.0  
**最後更新:** 2025-12-27  
**作者:** Claude AI Assistant