## 03 部署與驗證（本地 / Docker / Cloud Run）

**目標**：最少步驟完成部署並驗證。詳細指令請見原檔 `CONSOLIDATED_DEPLOYMENT.md`。

### 前置
- 帳號：MEXC（Spot Trading 權限）、GCP（Cloud Run + Scheduler + Secret Manager）、Redis（本地/雲端/ Memorystore）。
- 軟體：Python 3.11+、Docker（可選）、gcloud CLI。

### 本地開發
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填 API/SECRET/REDIS_URL
uvicorn main:app --reload --port 8080
```
驗證：
```bash
curl http://localhost:8080/health
curl http://localhost:8080/market/price/QRLUSDT
```

### Docker
```bash
docker build -t qrl-trading-api .
docker run -d -p 8080:8080 \
  -e MEXC_API_KEY=xxx \
  -e MEXC_SECRET_KEY=xxx \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  qrl-trading-api
```
可選 docker-compose：Redis + API，REDIS_URL 設為 `redis://redis:6379/0`。

### Cloud Run（摘要）
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT
gcloud services enable run.googleapis.com cloudscheduler.googleapis.com secretmanager.googleapis.com cloudbuild.googleapis.com redis.googleapis.com

# 建立秘密並授權 Cloud Run
echo -n "key" | gcloud secrets create mexc-api-key --data-file=-
echo -n "secret" | gcloud secrets create mexc-secret-key --data-file=-
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT --format='value(projectNumber)')
for s in mexc-api-key mexc-secret-key; do
  gcloud secrets add-iam-policy-binding $s \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done

# 部署
gcloud run deploy qrl-api --source . --region asia-southeast1 \
  --memory 512Mi --cpu 1 --timeout 60s \
  --set-env-vars="TRADING_SYMBOL=QRLUSDT,DRY_RUN=false" \
  --set-secrets="MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest" \
  --no-allow-unauthenticated
```

### Cloud Scheduler（摘要）
以 OIDC 呼叫 Cloud Run（建議），每分鐘/3 分鐘/5 分鐘觸發：
```bash
SERVICE_URL=$(gcloud run services describe qrl-api --region=asia-southeast1 --format='value(status.url)')
gcloud iam service-accounts create scheduler-sa
gcloud run services add-iam-policy-binding qrl-api --region=asia-southeast1 \
  --member="serviceAccount:scheduler-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud scheduler jobs create http sync-balance --location=asia-southeast1 \
  --schedule="*/3 * * * *" \
  --uri="${SERVICE_URL}/tasks/sync-balance" \
  --http-method=POST \
  --oidc-service-account-email="scheduler-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --headers="Content-Type=application/json" \
  --message-body='{}'
# 依樣建立 update-price (每分鐘) / update-cost (每 5 分鐘)
```

### Redis 選項
- 本地 Docker：`docker run -d -p 6379:6379 redis:7-alpine`
- Redis Cloud：使用平台提供的 `redis://:pwd@host:port/0`
- Memorystore：建立後透過 VPC Connector 連線並更新 Cloud Run。

### 驗證與日誌
```bash
curl ${SERVICE_URL}/health
gcloud logging read "resource.type=cloud_run_revision" --limit=20
redis-cli TTL bot:QRLUSDT:price:latest   # 期望 -1
redis-cli GET mexc:raw:account_info:latest
```

### 常見部署陷阱
- Scheduler 401：確認 OIDC audience = SERVICE_URL，並已授予 `roles/run.invoker`。  
- 價格缺失：確定 Redis 永久層 key 無 TTL；快取層 TTL 30s 為正常。  
- 成本偏高：使用 Redis Cloud 免費層或降低 Job 頻率可省費用（詳見 08）。  
