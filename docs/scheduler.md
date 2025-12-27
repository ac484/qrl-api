# Cloud Scheduler 設定指南

## 📅 排程策略

### 為什麼選擇 3 分鐘間隔？

QRL/USDT 交易機器人採用囤幣累積策略，特點如下：

1. **不需要高頻交易**
   - 策略基於移動平均線（MA20）和價格回調
   - 每日交易限制：最多 8 次
   - 不追求短線套利，著重長期累積

2. **3 分鐘的優勢**
   - 每小時檢查 20 次，足夠捕捉價格變化
   - 每天執行約 480 次，遠超實際交易需求
   - 降低 Cloud Run 成本（相比每分鐘執行減少 67% 調用）
   - 減少 API 請求，避免觸及 MEXC 速率限制

3. **執行時間分布**
   ```
   每小時: 00, 03, 06, 09, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57
   每天:   480 次執行機會
   ```

## 🚀 快速部署

### 步驟 1: 準備環境

```bash
# 確認已安裝 gcloud CLI
gcloud version

# 設定專案
gcloud config set project YOUR_PROJECT_ID

# 啟用必要的 API
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable run.googleapis.com
```

### 步驟 2: 部署 Cloud Run 服務

```bash
# 構建並部署
gcloud builds submit --tag asia-east1-docker.pkg.dev/PROJECT_ID/qrl-trading-api/qrl-trading-api:latest
gcloud run deploy qrl-trading-api \
  --image asia-east1-docker.pkg.dev/PROJECT_ID/qrl-trading-api/qrl-trading-api:latest \
  --platform managed \
  --region asia-east1 \
  --set-env-vars REDIS_URL=redis://10.0.0.3:6379/0

# 獲取服務 URL
export CLOUD_RUN_URL=$(gcloud run services describe qrl-trading-api --region=asia-east1 --format='value(status.url)')
echo "Cloud Run URL: $CLOUD_RUN_URL"
```

### 步驟 3: 部署排程器

#### 方式 A: 使用自動腳本（推薦）

```bash
./deploy_scheduler.sh $CLOUD_RUN_URL YOUR_PROJECT_ID asia-east1
```

#### 方式 B: 手動建立

```bash
gcloud scheduler jobs create http qrl-trading-api-trigger \
  --schedule="*/3 * * * *" \
  --uri="${CLOUD_RUN_URL}/execute" \
  --http-method=POST \
  --location=asia-east1 \
  --description="QRL/USDT 囤幣機器人 - 每 3 分鐘執行" \
  --time-zone="Asia/Taipei" \
  --attempt-deadline=180s \
  --max-retry-attempts=3 \
  --min-backoff=30s \
  --max-backoff=120s \
  --oidc-service-account-email=YOUR_PROJECT_ID@appspot.gserviceaccount.com
```

## 🔍 監控與管理

### 查看排程狀態

```bash
# 查看作業詳情
gcloud scheduler jobs describe qrl-trading-api-trigger --location=asia-east1

# 查看最近執行記錄
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=qrl-trading-api-trigger" \
  --limit=20 \
  --format=json
```

### 手動觸發（測試用）

```bash
# 立即執行一次
gcloud scheduler jobs run qrl-trading-api-trigger --location=asia-east1

# 檢查執行結果
curl https://YOUR_CLOUD_RUN_URL/status
```

### 暫停與恢復

```bash
# 暫停排程（例如：維護期間）
gcloud scheduler jobs pause qrl-trading-api-trigger --location=asia-east1

# 恢復排程
gcloud scheduler jobs resume qrl-trading-api-trigger --location=asia-east1
```

### 查看執行記錄

```bash
# 查看 Cloud Scheduler 日誌
gcloud logging read "resource.type=cloud_scheduler_job" \
  --limit=50 \
  --format="table(timestamp,jsonPayload.message)"

# 查看 Cloud Run 執行日誌
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=qrl-trading-api" \
  --limit=50 \
  --format="table(timestamp,jsonPayload.message)"
```

## ⚙️ 配置調整

### 修改執行頻率

```bash
# 更新為每 5 分鐘執行
gcloud scheduler jobs update http qrl-trading-api-trigger \
  --schedule="*/5 * * * *" \
  --location=asia-east1

# 更新為每小時執行
gcloud scheduler jobs update http qrl-trading-api-trigger \
  --schedule="0 * * * *" \
  --location=asia-east1

# 更新為每天特定時間執行（例如：每天 9:00, 12:00, 15:00, 18:00）
gcloud scheduler jobs update http qrl-trading-api-trigger \
  --schedule="0 9,12,15,18 * * *" \
  --location=asia-east1
```

### Cron 表達式參考

```
格式: 分鐘 小時 日期 月份 星期
      *    *    *    *    *

範例:
*/3 * * * *         每 3 分鐘
*/5 * * * *         每 5 分鐘
0 * * * *           每小時整點
0 */4 * * *         每 4 小時
0 9,12,15,18 * * *  每天 9:00, 12:00, 15:00, 18:00
0 9-17 * * 1-5      週一到週五，每天 9:00-17:00 每小時執行
```

### 重試策略調整

```bash
# 更新重試設定
gcloud scheduler jobs update http qrl-trading-api-trigger \
  --max-retry-attempts=5 \
  --min-backoff=60s \
  --max-backoff=300s \
  --location=asia-east1
```

## 📊 成本估算

### Cloud Scheduler 費用（每月）

```
免費額度: 每月 3 個作業免費
超出費用: $0.10 USD/作業/月

QRL 機器人使用：
- 作業數量: 1 個
- 月費用: $0（在免費額度內）
```

### Cloud Run 調用費用（每月）

```
3 分鐘間隔執行:
- 每小時: 20 次
- 每天: 480 次
- 每月: 14,400 次

預估成本（假設每次執行 10 秒）:
- 請求費用: 14,400 × $0.0000004 = $0.0058
- CPU 時間: 14,400 × 10s × $0.000024 = $3.46
- 記憶體: 14,400 × 10s × 512MB × $0.0000025 = $0.18
- 總計: ~$3.64/月

相比每分鐘執行（約 $10.92/月），節省 67% 成本
```

## 🛡️ 安全性建議

### 1. 使用服務帳戶

```bash
# 創建專用服務帳戶
gcloud iam service-accounts create qrl-trading-scheduler \
  --display-name="QRL Trading Scheduler"

# 授予 Cloud Run Invoker 權限
gcloud run services add-iam-policy-binding qrl-trading-api \
  --member="serviceAccount:qrl-trading-scheduler@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=asia-east1

# 更新排程作業使用此服務帳戶
gcloud scheduler jobs update http qrl-trading-api-trigger \
  --oidc-service-account-email=qrl-trading-scheduler@PROJECT_ID.iam.gserviceaccount.com \
  --location=asia-east1
```

### 2. 驗證請求來源（在 Cloud Run 中）

在 `main.py` 中添加驗證：

```python
from google.auth.transport import requests
from google.oauth2 import id_token

def verify_scheduler_request():
    """驗證請求來自 Cloud Scheduler"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    
    try:
        token = auth_header.split(' ')[1]
        id_info = id_token.verify_oauth2_token(
            token, requests.Request()
        )
        return id_info.get('email') == 'qrl-trading-scheduler@PROJECT_ID.iam.gserviceaccount.com'
    except Exception:
        return False
```

### 3. 監控異常執行

```bash
# 設定告警（執行失敗超過 3 次）
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="QRL Scheduler 失敗告警" \
  --condition-display-name="連續失敗 3 次" \
  --condition-threshold-value=3 \
  --condition-threshold-duration=600s
```

## 🔧 故障排除

### 問題 1: 排程未執行

**檢查步驟:**
```bash
# 1. 確認作業狀態
gcloud scheduler jobs describe qrl-trading-api-trigger --location=asia-east1

# 2. 檢查是否暫停
# 輸出中查看 state: ENABLED

# 3. 查看錯誤日誌
gcloud logging read "resource.type=cloud_scheduler_job AND severity>=ERROR" --limit=10
```

### 問題 2: 執行失敗（HTTP 錯誤）

**檢查步驟:**
```bash
# 1. 測試 Cloud Run 端點
curl -X POST https://YOUR_CLOUD_RUN_URL/execute

# 2. 檢查服務帳戶權限
gcloud run services get-iam-policy qrl-trading-api --region=asia-east1

# 3. 手動觸發測試
gcloud scheduler jobs run qrl-trading-api-trigger --location=asia-east1
```

### 問題 3: 逾時錯誤

**解決方案:**
```bash
# 增加逾時時間
gcloud scheduler jobs update http qrl-trading-api-trigger \
  --attempt-deadline=300s \
  --location=asia-east1
```

## 📚 相關資源

- [Cloud Scheduler 官方文檔](https://cloud.google.com/scheduler/docs)
- [Cron 表達式語法](https://cloud.google.com/scheduler/docs/configuring/cron-job-schedules)
- [Cloud Run 觸發器](https://cloud.google.com/run/docs/triggering/using-scheduler)
- [費用計算器](https://cloud.google.com/products/calculator)

---

**最後更新**: 2025-12-27  
**版本**: 1.0.0
