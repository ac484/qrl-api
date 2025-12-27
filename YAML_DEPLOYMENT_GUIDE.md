# YAML 配置文件部署指南

本指南說明如何使用 YAML 配置文件自動化部署 Cloud Scheduler jobs。

## 📁 配置文件說明

### 1. `scheduler-config.yaml`
- **用途**: 聲明式配置 Cloud Scheduler jobs
- **格式**: Kubernetes-style YAML（Config Connector）
- **內容**: 3 個 Cloud Scheduler job 的完整配置

### 2. `cloudbuild-scheduler.yaml`
- **用途**: Cloud Build 自動化部署流程
- **格式**: Cloud Build 配置文件
- **內容**: 8 個步驟的自動化部署流程

## 🚀 部署方法

### 方法 1: 使用 Cloud Build（推薦）

這是最簡單的自動化方法。

#### 步驟 1: 提交 Cloud Build

```bash
gcloud builds submit --config=cloudbuild-scheduler.yaml
```

這個命令會：
1. ✅ 啟用必要的 API（Cloud Scheduler, App Engine）
2. ✅ 檢查並創建 App Engine 應用（如需要）
3. ✅ 刪除現有的舊 jobs（如有）
4. ✅ 創建 3 個新的 Cloud Scheduler jobs
5. ✅ 列出所有 jobs 進行驗證
6. ✅ 測試每個 job 確保運作正常

#### 步驟 2: 查看部署日誌

```bash
# 在 Cloud Console 查看
https://console.cloud.google.com/cloud-build/builds

# 或使用 gcloud 命令
gcloud builds log <BUILD_ID>
```

#### 步驟 3: 驗證部署

```bash
# 列出所有 scheduler jobs
gcloud scheduler jobs list --location=asia-southeast1

# 查看特定 job 詳情
gcloud scheduler jobs describe qrl-sync-balance-job --location=asia-southeast1
```

### 方法 2: 使用 Config Connector（進階）

如果您的 GKE 集群已安裝 Config Connector：

#### 步驟 1: 編輯 `scheduler-config.yaml`

將 `YOUR_PROJECT_ID` 替換為您的實際專案 ID：

```bash
sed -i 's/YOUR_PROJECT_ID/你的專案ID/g' scheduler-config.yaml
```

#### 步驟 2: 應用配置

```bash
kubectl apply -f scheduler-config.yaml
```

#### 步驟 3: 驗證資源

```bash
kubectl get cloudschedulerjob
```

### 方法 3: 使用 Terraform（企業級）

將 YAML 轉換為 Terraform HCL 格式（可選）：

```hcl
resource "google_cloud_scheduler_job" "sync_balance" {
  name             = "qrl-sync-balance-job"
  description      = "Sync MEXC account balance to Redis every minute"
  schedule         = "* * * * *"
  time_zone        = "Asia/Taipei"
  region           = "asia-southeast1"
  attempt_deadline = "320s"

  retry_config {
    retry_count          = 3
    max_retry_duration   = "0s"
    min_backoff_duration = "5s"
    max_backoff_duration = "3600s"
    max_doublings        = 5
  }

  http_target {
    uri         = "https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/sync-balance"
    http_method = "POST"
    
    headers = {
      "X-CloudScheduler" = "true"
      "Content-Type"     = "application/json"
    }
    
    body = base64encode("{}")
  }
}
```

## 📊 自動化 CI/CD

### 使用 Cloud Build Trigger

創建 Cloud Build 觸發器，在代碼推送時自動部署：

```bash
gcloud builds triggers create github \
  --repo-name=qrl-api \
  --repo-owner=7Spade \
  --branch-pattern=^main$ \
  --build-config=cloudbuild-scheduler.yaml \
  --description="Deploy Cloud Scheduler jobs on push to main"
```

### 使用 GitHub Actions

創建 `.github/workflows/deploy-scheduler.yml`：

```yaml
name: Deploy Cloud Scheduler Jobs

on:
  push:
    branches: [ main ]
    paths:
      - 'cloudbuild-scheduler.yaml'
      - 'scheduler-config.yaml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - name: Deploy with Cloud Build
        run: gcloud builds submit --config=cloudbuild-scheduler.yaml
```

## 🔧 配置文件定製

### 修改執行頻率

編輯 `cloudbuild-scheduler.yaml` 或 `scheduler-config.yaml`：

```yaml
# 原本：每分鐘
schedule: "* * * * *"

# 改為：每 5 分鐘
schedule: "*/5 * * * *"

# 改為：每小時
schedule: "0 * * * *"

# 改為：每天凌晨 2 點
schedule: "0 2 * * *"
```

### 修改目標 URL

如果您的 Cloud Run URL 改變：

```bash
# 方法 1: 使用 sed 批量替換
sed -i 's|https://qrl-trading-api-545492969490.asia-southeast1.run.app|https://your-new-url.run.app|g' cloudbuild-scheduler.yaml

# 方法 2: 使用 Cloud Build 替代變數
gcloud builds submit --config=cloudbuild-scheduler.yaml \
  --substitutions=_CLOUD_RUN_URL=https://your-new-url.run.app
```

### 修改時區

```yaml
# 編輯 cloudbuild-scheduler.yaml
substitutions:
  _TIMEZONE: 'America/New_York'  # 紐約時間
  _TIMEZONE: 'Europe/London'     # 倫敦時間
  _TIMEZONE: 'Asia/Tokyo'        # 東京時間
```

## 🧪 測試和驗證

### 手動觸發 Cloud Build

```bash
# 使用預設配置
gcloud builds submit --config=cloudbuild-scheduler.yaml

# 使用自定義變數
gcloud builds submit --config=cloudbuild-scheduler.yaml \
  --substitutions=_CLOUD_RUN_URL=https://test-url.run.app,_REGION=us-central1
```

### 驗證 Jobs 創建成功

```bash
# 列出所有 jobs
gcloud scheduler jobs list --location=asia-southeast1

# 輸出應包含：
# qrl-sync-balance-job
# qrl-update-price-job
# qrl-update-cost-job
```

### 手動執行 Job 測試

```bash
# 測試餘額同步
gcloud scheduler jobs run qrl-sync-balance-job --location=asia-southeast1

# 查看執行日誌
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=qrl-sync-balance-job" --limit=10 --format=json
```

### 檢查 Cloud Run 日誌

```bash
# 查看任務執行結果
gcloud logging read "resource.type=cloud_run_revision AND textPayload=~'Task completed'" --limit=20
```

## 🔄 更新和維護

### 更新 Job 配置

1. 編輯 `cloudbuild-scheduler.yaml`
2. 重新提交：
   ```bash
   gcloud builds submit --config=cloudbuild-scheduler.yaml
   ```
3. Cloud Build 會自動刪除舊 jobs 並創建新的

### 暫停所有 Jobs

```bash
gcloud scheduler jobs pause qrl-sync-balance-job --location=asia-southeast1
gcloud scheduler jobs pause qrl-update-price-job --location=asia-southeast1
gcloud scheduler jobs pause qrl-update-cost-job --location=asia-southeast1
```

### 恢復所有 Jobs

```bash
gcloud scheduler jobs resume qrl-sync-balance-job --location=asia-southeast1
gcloud scheduler jobs resume qrl-update-price-job --location=asia-southeast1
gcloud scheduler jobs resume qrl-update-cost-job --location=asia-southeast1
```

### 刪除所有 Jobs

```bash
gcloud scheduler jobs delete qrl-sync-balance-job --location=asia-southeast1
gcloud scheduler jobs delete qrl-update-price-job --location=asia-southeast1
gcloud scheduler jobs delete qrl-update-cost-job --location=asia-southeast1
```

## 💰 成本監控

### 查看 Cloud Scheduler 使用情況

```bash
# 前往 Cloud Console
https://console.cloud.google.com/cloudscheduler

# 查看計費
https://console.cloud.google.com/billing
```

### 預估月費用

- **Cloud Scheduler**: 前 3 個 jobs 免費，之後 $0.10/job/月
- **Cloud Run**: 
  - 3 jobs × 60 次/小時 × 24 小時 × 30 天 = 129,600 次/月
  - 每次 ~200ms
  - 預估：**$0.15-0.25/月**

## 📝 最佳實踐

1. **使用 Cloud Build 觸發器** 實現自動化 CI/CD
2. **版本控制** 所有 YAML 配置文件在 Git
3. **環境隔離** 使用不同的專案或區域分隔開發/生產環境
4. **監控告警** 設置 Cloud Monitoring 告警監控 job 失敗
5. **定期審查** 檢查 job 執行日誌和成本

## 🆘 疑難排解

### Cloud Build 失敗

```bash
# 查看詳細日誌
gcloud builds log <BUILD_ID> --stream

# 常見問題：
# 1. API 未啟用 → Cloud Build 會自動啟用
# 2. 權限不足 → 確保 Cloud Build service account 有 Cloud Scheduler Admin 權限
# 3. App Engine 未創建 → Cloud Build 會自動創建
```

### Job 創建失敗

```bash
# 檢查是否已存在
gcloud scheduler jobs list --location=asia-southeast1

# 如果存在，手動刪除後重試
gcloud scheduler jobs delete <JOB_NAME> --location=asia-southeast1
```

### Job 執行失敗

```bash
# 查看 job 狀態
gcloud scheduler jobs describe <JOB_NAME> --location=asia-southeast1

# 查看執行歷史
gcloud logging read "resource.type=cloud_scheduler_job" --limit=20
```

## 📚 相關文檔

- [Cloud Scheduler 官方文檔](https://cloud.google.com/scheduler/docs)
- [Cloud Build 配置參考](https://cloud.google.com/build/docs/build-config-file-schema)
- [Config Connector 文檔](https://cloud.google.com/config-connector/docs/overview)

## 🎉 快速開始命令

最簡單的一鍵部署：

```bash
# Clone 倉庫
git clone https://github.com/7Spade/qrl-api.git
cd qrl-api

# 部署 Cloud Scheduler jobs
gcloud builds submit --config=cloudbuild-scheduler.yaml

# 完成！
```

部署完成後，3 個 Cloud Scheduler jobs 會自動開始執行，您的儀表板將實時更新餘額和價格數據。
