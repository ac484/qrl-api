# Cloud Scheduler 設置說明

## 您的部署資訊

- **Cloud Run URL**: `https://qrl-trading-api-545492969490.asia-southeast1.run.app`
- **區域**: `asia-southeast1`
- **專案 ID**: (您需要從 Cloud Console 取得)

## 方法 1: 使用自動化腳本 (推薦)

### 步驟 1: 取得專案 ID

```bash
gcloud config get-value project
```

### 步驟 2: 編輯 setup_cloud_scheduler.sh

將第 6 行的 `PROJECT_ID="your-project-id"` 替換為您的專案 ID:

```bash
PROJECT_ID="your-actual-project-id"
```

### 步驟 3: 執行腳本

```bash
chmod +x setup_cloud_scheduler.sh
./setup_cloud_scheduler.sh
```

## 方法 2: 使用 Cloud Console (手動設置)

### 步驟 1: 開啟 Cloud Scheduler

前往: https://console.cloud.google.com/cloudscheduler

### 步驟 2: 創建 Job 1 - 餘額同步

點擊 **「建立工作」**

```
名稱: sync-balance-job
區域: asia-southeast1
描述: Sync MEXC account balance to Redis
頻率: * * * * * (每分鐘)
時區: Asia/Taipei

目標類型: HTTP
URL: https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/sync-balance
HTTP 方法: POST
正文: {} (空 JSON)
標頭:
  - 名稱: X-CloudScheduler
  - 值: true
驗證: (不需要，端點會檢查 header)
```

點擊 **「建立」**

### 步驟 3: 創建 Job 2 - 價格更新

點擊 **「建立工作」**

```
名稱: update-price-job
區域: asia-southeast1
描述: Update QRL/USDT price
頻率: * * * * * (每分鐘)
時區: Asia/Taipei

目標類型: HTTP
URL: https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/update-price
HTTP 方法: POST
正文: {}
標頭:
  - 名稱: X-CloudScheduler
  - 值: true
```

點擊 **「建立」**

### 步驟 4: 創建 Job 3 - 成本更新

點擊 **「建立工作」**

```
名稱: update-cost-job
區域: asia-southeast1
描述: Update cost and PnL data
頻率: */5 * * * * (每 5 分鐘)
時區: Asia/Taipei

目標類型: HTTP
URL: https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/update-cost
HTTP 方法: POST
正文: {}
標頭:
  - 名稱: X-CloudScheduler
  - 值: true
```

點擊 **「建立」**

## 方法 3: 使用 gcloud 命令 (快速)

### 前置要求

```bash
# 啟用 Cloud Scheduler API
gcloud services enable cloudscheduler.googleapis.com

# 創建 App Engine 應用 (如果還沒有)
gcloud app create --region=asia-southeast1
```

### Job 1: 餘額同步 (每分鐘)

```bash
gcloud scheduler jobs create http sync-balance-job \
    --location=asia-southeast1 \
    --schedule="* * * * *" \
    --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/sync-balance" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --time-zone="Asia/Taipei" \
    --description="Sync MEXC account balance to Redis"
```

### Job 2: 價格更新 (每分鐘)

```bash
gcloud scheduler jobs create http update-price-job \
    --location=asia-southeast1 \
    --schedule="* * * * *" \
    --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/update-price" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --time-zone="Asia/Taipei" \
    --description="Update QRL/USDT price"
```

### Job 3: 成本更新 (每 5 分鐘)

```bash
gcloud scheduler jobs create http update-cost-job \
    --location=asia-southeast1 \
    --schedule="*/5 * * * *" \
    --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/update-cost" \
    --http-method=POST \
    --headers="X-CloudScheduler=true" \
    --time-zone="Asia/Taipei" \
    --description="Update cost and PnL data"
```

## 驗證設置

### 查看所有 Jobs

```bash
gcloud scheduler jobs list --location=asia-southeast1
```

### 手動測試 Job

```bash
# 測試餘額同步
gcloud scheduler jobs run sync-balance-job --location=asia-southeast1

# 測試價格更新
gcloud scheduler jobs run update-price-job --location=asia-southeast1

# 測試成本更新
gcloud scheduler jobs run update-cost-job --location=asia-southeast1
```

### 查看執行日誌

```bash
# Cloud Scheduler 日誌
gcloud logging read "resource.type=cloud_scheduler_job" --limit=20 --format=json

# Cloud Run 日誌 (查看任務執行結果)
gcloud logging read "resource.type=cloud_run_revision" --limit=20 --format=json
```

或在 Cloud Console:
- Cloud Scheduler 日誌: https://console.cloud.google.com/cloudscheduler
- Cloud Run 日誌: https://console.cloud.google.com/run

## 測試端點

您也可以直接測試端點 (需要添加 X-CloudScheduler header):

```bash
# 測試餘額同步
curl -X POST \
  https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/sync-balance \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json"

# 測試價格更新
curl -X POST \
  https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/update-price \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json"

# 測試成本更新
curl -X POST \
  https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/update-cost \
  -H "X-CloudScheduler: true" \
  -H "Content-Type: application/json"
```

## 暫停/啟用 Jobs

### 暫停

```bash
gcloud scheduler jobs pause sync-balance-job --location=asia-southeast1
gcloud scheduler jobs pause update-price-job --location=asia-southeast1
gcloud scheduler jobs pause update-cost-job --location=asia-southeast1
```

### 恢復

```bash
gcloud scheduler jobs resume sync-balance-job --location=asia-southeast1
gcloud scheduler jobs resume update-price-job --location=asia-southeast1
gcloud scheduler jobs resume update-cost-job --location=asia-southeast1
```

## 刪除 Jobs

```bash
gcloud scheduler jobs delete sync-balance-job --location=asia-southeast1
gcloud scheduler jobs delete update-price-job --location=asia-southeast1
gcloud scheduler jobs delete update-cost-job --location=asia-southeast1
```

## 監控儀表板

設置完成後，您可以在儀表板查看自動更新的數據:

- **URL**: https://qrl-trading-api-545492969490.asia-southeast1.run.app/dashboard
- **餘額**: 每分鐘自動更新
- **價格**: 每分鐘自動更新
- **盈虧**: 每 5 分鐘自動更新

## 費用預估

- Cloud Scheduler: 前 3 個 jobs 免費
- Cloud Run: 
  - 3 個 jobs × 每分鐘 = ~4,320 次請求/天
  - 每次請求 ~200ms
  - 預估: **~$0.20/月**

## 疑難排解

### Job 執行失敗

1. 查看 Cloud Scheduler 日誌
2. 查看 Cloud Run 日誌
3. 確認 X-CloudScheduler header 已設置
4. 確認 Cloud Run 服務正在運行

### 401 Unauthorized 錯誤

確保請求包含 `X-CloudScheduler: true` header

### 500 Internal Server Error

1. 檢查 Cloud Run 日誌查看詳細錯誤
2. 確認環境變數 (MEXC_API_KEY, MEXC_SECRET_KEY, REDIS_URL) 已正確設置
3. 確認 Redis 連接正常

## 需要協助?

如有問題，請提供:
1. Job 名稱
2. Cloud Scheduler 日誌
3. Cloud Run 日誌
4. 錯誤訊息截圖
