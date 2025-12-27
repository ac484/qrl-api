# QRL Trading Bot

自動化 QRL/USDT 交易機器人，部署在 Google Cloud Run，使用 Redis 進行狀態管理。

## 🏗️ 架構概覽

```
Cloud Scheduler → Cloud Run (Flask App) → Redis (State Management)
                       ↓
                  MEXC API (Trading)
```

## 📁 專案結構

```
qrl-api/
├── main.py              # Flask 主應用程式
├── bot.py               # 交易機器人邏輯
├── redis_client.py      # Redis 客戶端
├── config.py            # 配置管理
├── requirements.txt     # Python 依賴
├── Dockerfile           # Docker 容器配置
├── .env.example         # 環境變數範例
└── docs/
    └── README.md        # 詳細架構文檔
```

## 🚀 快速開始

### 本地開發

1. **安裝依賴**
```bash
pip install -r requirements.txt
```

2. **配置環境變數**
```bash
cp .env.example .env
# 編輯 .env 文件，填入你的配置
```

3. **啟動 Redis (使用 Docker)**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

4. **運行應用**
```bash
python main.py
```

應用將在 http://localhost:8080 啟動

### Docker 本地測試

1. **構建映像**
```bash
docker build -t qrl-trading-api .
```

2. **運行容器**
```bash
docker run -p 8080:8080 \
  -e REDIS_HOST=host.docker.internal \
  -e REDIS_PORT=6379 \
  qrl-trading-api
```

## 📡 API 端點

### GET /
基本服務信息
```bash
curl http://localhost:8080/
```

### GET /health
健康檢查端點
```bash
curl http://localhost:8080/health
```

### POST /execute
執行交易策略（由 Cloud Scheduler 觸發）
```bash
curl -X POST http://localhost:8080/execute
```

### GET /status
獲取機器人當前狀態
```bash
curl http://localhost:8080/status
```

### POST /control
控制機器人（啟動/暫停/停止）
```bash
# 啟動
curl -X POST http://localhost:8080/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# 暫停
curl -X POST http://localhost:8080/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pause"}'

# 停止
curl -X POST http://localhost:8080/control \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'
```

## ☁️ GCP 部署

### 前置條件

1. 安裝 [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. 創建 GCP 專案
3. 啟用必要的 API：
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable redis.googleapis.com
```

### 部署 Redis (Memorystore)

```bash
gcloud redis instances create qrl-redis \
  --size=1 \
  --region=asia-southeast1 \
  --redis-version=redis_7_0
```

獲取 Redis IP：
```bash
gcloud redis instances describe qrl-redis --region=asia-southeast1
```

### 部署到 Cloud Run

1. **構建並推送映像到 Artifact Registry**
```bash
# 創建 Artifact Registry 倉庫
gcloud artifacts repositories create qrl-trading-api \
  --repository-format=docker \
  --location=asia-southeast1

# 構建並推送
gcloud builds submit --tag asia-southeast1-docker.pkg.dev/PROJECT_ID/qrl-trading-api/qrl-trading-api:latest
```

2. **部署 Cloud Run 服務**
```bash
gcloud run deploy qrl-trading-api \
  --image asia-southeast1-docker.pkg.dev/PROJECT_ID/qrl-trading-api/qrl-trading-api:latest \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --vpc-connector YOUR_VPC_CONNECTOR \
  --set-env-vars REDIS_HOST=REDIS_IP,REDIS_PORT=6379 \
  --max-instances 1 \
  --memory 512Mi
```

### 設置 Cloud Scheduler

```bash
# 每分鐘執行一次
gcloud scheduler jobs create http qrl-trading-api-trigger \
  --schedule="*/1 * * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/execute" \
  --http-method=POST \
  --location=asia-southeast1
```

## 🔧 配置說明

### 環境變數

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| PORT | 服務端口 | 8080 |
| DEBUG | 調試模式 | False |
| REDIS_HOST | Redis 主機 | localhost |
| REDIS_PORT | Redis 端口 | 6379 |
| REDIS_PASSWORD | Redis 密碼 | (空) |
| TRADING_PAIR | 交易對 | QRL-USDT |
| MAX_DAILY_TRADES | 每日最大交易次數 | 5 |
| MEXC_API_KEY | MEXC API Key | (必填) |
| MEXC_API_SECRET | MEXC API Secret | (必填) |

### 策略參數

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| SHORT_MA_PERIOD | 短期均線周期 | 5 |
| LONG_MA_PERIOD | 長期均線周期 | 20 |
| RSI_PERIOD | RSI 周期 | 14 |
| RSI_OVERSOLD | RSI 超賣閾值 | 30 |
| RSI_OVERBOUGHT | RSI 超買閾值 | 70 |

### 風險控制

| 變數名 | 說明 | 預設值 |
|--------|------|--------|
| STOP_LOSS_PERCENT | 止損百分比 | 3.0 |
| TAKE_PROFIT_PERCENT | 止盈百分比 | 5.0 |
| MAX_DAILY_LOSS_PERCENT | 每日最大虧損 | 5.0 |
| MAX_POSITION_PERCENT | 最大倉位百分比 | 10.0 |

## 💾 Redis 數據結構

```
bot:qrl-usdt:status          → 運行狀態 (running/paused/stopped)
bot:qrl-usdt:position        → 當前持倉 (JSON)
bot:qrl-usdt:price:latest    → 最新價格 (TTL: 5分鐘)
bot:qrl-usdt:price:history   → 價格歷史 (List, 最多100條)
bot:qrl-usdt:trades:today    → 今日交易次數 (TTL: 24小時)
bot:qrl-usdt:last-trade      → 最後交易時間戳
```

## 🔒 安全建議

1. **使用 Secret Manager 存儲 API 密鑰**
2. **啟用 Cloud Run 身份驗證**
3. **使用 VPC Connector 連接 Redis**
4. **定期輪換 API 密鑰**
5. **監控異常交易活動**

## 📊 監控與日誌

### 查看日誌
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=qrl-trading-api" --limit 50
```

### 監控指標
- 請求成功率
- 執行時間
- Redis 連接狀態
- 每日交易次數

## 🧪 測試

```bash
# 測試健康檢查
curl https://YOUR_CLOUD_RUN_URL/health

# 測試狀態查詢
curl https://YOUR_CLOUD_RUN_URL/status

# 手動觸發執行（測試用）
curl -X POST https://YOUR_CLOUD_RUN_URL/execute
```

## 📝 待辦事項

- [ ] 實作 MEXC API 整合
- [ ] 實作 RSI 和 MACD 指標計算
- [ ] 添加 Firestore 長期數據存儲
- [ ] 實作通知系統 (Email/Telegram)
- [ ] 添加回測功能
- [ ] 實作更多交易策略

## 📄 授權

MIT License

## 🔗 相關資源

- [MEXC API 文檔](https://mexcdevelop.github.io/apidocs/)
- [Google Cloud Run 文檔](https://cloud.google.com/run/docs)
- [Redis 文檔](https://redis.io/docs/)
