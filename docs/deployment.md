# 部署指南 (Deployment Guide)

## 自動化部署 Cloud Build

### 前置準備

1. **啟用必要的 GCP API**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

2. **創建 Artifact Registry 儲存庫**
```bash
gcloud artifacts repositories create qrl-trading-api \
  --repository-format=docker \
  --location=asia-southeast1 \
  --description="QRL Trading Bot Docker images"
```

3. **設置 Secret Manager（儲存敏感資料）**
```bash
# 創建 MEXC API Key secret
echo -n "YOUR_MEXC_API_KEY" | gcloud secrets create mexc-api-key --data-file=-

# 創建 MEXC API Secret
echo -n "YOUR_MEXC_API_SECRET" | gcloud secrets create mexc-api-secret --data-file=-

# 授予 Cloud Run 訪問權限
gcloud secrets add-iam-policy-binding mexc-api-key \
  --member="serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding mexc-api-secret \
  --member="serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 方式一：手動觸發構建（推薦用於測試）

```bash
# 基本構建
gcloud builds submit --config cloudbuild.yaml

# 自定義參數構建
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=asia-southeast1,_REDIS_URL=redis://your-redis-url:6379/0
```

### 方式二：設置自動觸發器（推薦用於生產）

#### 使用 GitHub 自動觸發

1. **連接 GitHub 儲存庫**
```bash
# 在 GCP Console 中連接 GitHub
# https://console.cloud.google.com/cloud-build/triggers
```

2. **創建觸發器**
```bash
gcloud builds triggers create github \
  --name="qrl-api-deploy" \
  --repo-name="qrl-api" \
  --repo-owner="7Spade" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --substitutions=_REGION=asia-southeast1,_REDIS_URL="redis://your-redis-url:6379/0"
```

#### 使用 Cloud Source Repositories 自動觸發

```bash
gcloud builds triggers create cloud-source-repositories \
  --name="qrl-api-deploy" \
  --repo="qrl-api" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml"
```

### 配置環境變數

編輯 `cloudbuild.yaml` 中的 `substitutions` 區塊：

```yaml
substitutions:
  _REGION: 'asia-southeast1'           # 你的區域
  _REDIS_URL: 'redis://your-url:6379'  # 你的 Redis URL
  _TRADING_PAIR: 'QRL-USDT'            # 交易對
  _MAX_DAILY_TRADES: '8'               # 每日最大交易次數
```

### 部署後驗證

1. **檢查 Cloud Run 服務**
```bash
gcloud run services describe qrl-trading-api --region=asia-southeast1
```

2. **查看服務 URL**
```bash
gcloud run services describe qrl-trading-api \
  --region=asia-southeast1 \
  --format='value(status.url)'
```

3. **測試端點**
```bash
# 健康檢查
curl https://YOUR_SERVICE_URL/health

# API 文檔
curl https://YOUR_SERVICE_URL/docs

# 儀表板
curl https://YOUR_SERVICE_URL/
```

### 設置 Cloud Scheduler（自動執行交易）

部署完成後，設置定時任務：

```bash
# 獲取 Cloud Run URL
SERVICE_URL=$(gcloud run services describe qrl-trading-api \
  --region=asia-southeast1 \
  --format='value(status.url)')

# 創建 Cloud Scheduler 任務（每 3 分鐘執行一次）
gcloud scheduler jobs create http qrl-trading-api-trigger \
  --schedule="*/3 * * * *" \
  --uri="${SERVICE_URL}/execute" \
  --http-method=POST \
  --location=asia-east1 \
  --description="QRL Trading Bot - executes every 3 minutes" \
  --attempt-deadline=180s \
  --max-retry-attempts=3 \
  --oidc-service-account-email="${PROJECT_ID}-compute@developer.gserviceaccount.com"
```

## 監控和日誌

### 查看構建日誌
```bash
gcloud builds list --limit=5
gcloud builds log BUILD_ID
```

### 查看應用日誌
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=qrl-trading-api" \
  --limit=50 \
  --format=json
```

### 監控指標
- Cloud Console: https://console.cloud.google.com/run
- 查看請求數、延遲、錯誤率等指標

## 故障排除

### 構建失敗
```bash
# 查看詳細構建日誌
gcloud builds log BUILD_ID --stream

# 檢查 Dockerfile 語法
docker build -t test .
```

### 部署失敗
```bash
# 查看 Cloud Run 修訂版本
gcloud run revisions list --service=qrl-trading-api --region=asia-southeast1

# 查看特定修訂版本日誌
gcloud run revisions describe REVISION_NAME --region=asia-southeast1
```

### 應用錯誤
```bash
# 實時查看日誌
gcloud logging tail "resource.type=cloud_run_revision" \
  --filter="resource.labels.service_name=qrl-trading-api"
```

## 清理資源

```bash
# 刪除 Cloud Run 服務
gcloud run services delete qrl-trading-api --region=asia-southeast1

# 刪除 Cloud Scheduler 任務
gcloud scheduler jobs delete qrl-trading-api-trigger --location=asia-east1

# 刪除容器映像
gcloud artifacts docker images delete \
  asia-southeast1-docker.pkg.dev/PROJECT_ID/qrl-trading-api/qrl-trading-api:latest
```

## 成本優化

1. **設置最小實例為 0**（已在 cloudbuild.yaml 配置）
2. **限制最大實例數為 1**（單一交易機器人）
3. **使用適當的記憶體配置**（512Mi 足夠）
4. **啟用請求超時**（300 秒）

## 安全最佳實踐

1. ✅ 使用 Secret Manager 儲存 API 密鑰
2. ✅ 不在程式碼中硬編碼密碼
3. ✅ 限制 Cloud Run 服務帳號權限
4. ✅ 定期輪換 API 密鑰
5. ✅ 啟用 Cloud Armor（如需要 DDoS 防護）

## 更新策略

### 滾動更新（零停機時間）
Cloud Build 會自動進行滾動更新，新版本逐步替換舊版本。

### 快速回滾
```bash
# 列出所有修訂版本
gcloud run revisions list --service=qrl-trading-api --region=asia-southeast1

# 回滾到特定版本
gcloud run services update-traffic qrl-trading-api \
  --to-revisions=REVISION_NAME=100 \
  --region=asia-southeast1
```
