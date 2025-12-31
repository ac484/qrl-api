## 03 部署與驗證（本地 / Docker / Cloud Run）

**目標**：最少步驟完成部署與排程，並保留維運與清理指令。

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

# 部署（Secrets 需先建立，見下一節）
gcloud run deploy qrl-api --source . --region asia-southeast1 \
  --memory 512Mi --cpu 1 --timeout 60s \
  --set-env-vars="TRADING_SYMBOL=QRLUSDT,DRY_RUN=false" \
  --set-secrets="MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest" \
  --no-allow-unauthenticated
```

### Secret Manager 快速設定（從 .env 匯入）
```bash
PROJECT_ID="qrl-api"
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

for s in mexc-api-key mexc-secret-key redis-url; do
  gcloud secrets describe "$s" --project="$PROJECT_ID" >/dev/null 2>&1 || \
    gcloud secrets create "$s" --project="$PROJECT_ID" --replication-policy="automatic"

done

for key in MEXC_API_KEY MEXC_SECRET_KEY REDIS_URL; do
  value=$(grep "^${key}=" .env | cut -d'=' -f2-)
  secret_name=$(echo "$key" | tr 'A-Z' 'a-z' | tr '_' '-')
  echo -n "$value" | gcloud secrets versions add "$secret_name" --data-file=- --project="$PROJECT_ID"

done

for s in mexc-api-key mexc-secret-key redis-url; do
  gcloud secrets add-iam-policy-binding "$s" \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID"

done
```

### Cloud Scheduler（OIDC 推薦）
以 OIDC 呼叫 Cloud Run（建議），每分鐘/5 分鐘/15 分鐘觸發：
```bash
SERVICE_URL=$(gcloud run services describe qrl-api --region=asia-southeast1 --format='value(status.url)')
gcloud iam service-accounts create scheduler-sa

gcloud run services add-iam-policy-binding qrl-api --region=asia-southeast1 \
  --member="serviceAccount:scheduler-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud scheduler jobs create http 01-min-job --location=asia-southeast1 \
  --schedule="* * * * *" \
  --uri="${SERVICE_URL}/tasks/01-min-job" \
  --http-method=POST \
  --oidc-service-account-email="scheduler-sa@YOUR_PROJECT.iam.gserviceaccount.com" \
  --oidc-token-audience="${SERVICE_URL}" \
  --headers="Content-Type=application/json" \
  --message-body='{}'
# 05-min-job: --schedule="*/5 * * * *"，15-min-job: --schedule="*/15 * * * *"
```

若服務允許公開存取，可改用固定 URI + 自訂標頭：
```bash
gcloud scheduler jobs create http 05-min-job --schedule="*/5 * * * *" \
  --uri="https://<your-service>.run.app/tasks/05-min-job" \
  --http-method=POST \
  --headers="X-CloudScheduler=true,Content-Type=application/json" \
  --time-zone="Asia/Taipei" \
  --description="Update QRL/USDT price every 5 minutes"
```

重建排程前，先刪除舊任務：
```bash
gcloud scheduler jobs delete 01-min-job --location=asia-southeast1 --quiet || true
gcloud scheduler jobs delete 05-min-job --location=asia-southeast1 --quiet || true
gcloud scheduler jobs delete 15-min-job --location=asia-southeast1 --quiet || true
```

### 部署與維運指令集
```bash
# 由 cloudbuild.yaml 建置並部署
gcloud builds submit --config=cloudbuild.yaml .

# 直接 build 並指定映像部署（手動）
gcloud builds submit --tag gcr.io/${PROJECT_ID}/qrl-trading-api . && \
  gcloud run deploy qrl-trading-api \
    --image gcr.io/${PROJECT_ID}/qrl-trading-api \
    --platform managed --region asia-east1 --allow-unauthenticated

# 清理舊版修訂版
gcloud run revisions list --project ${PROJECT_ID} --service qrl-trading-api \
  --platform managed --region asia-southeast1 \
  --format "table(REVISION, TRAFFIC, CREATED, LAST_DEPLOYED, CONDITIONS)"

gcloud run revisions list --project ${PROJECT_ID} --service qrl-trading-api \
  --platform managed --region asia-southeast1 --format "value(REVISION)" \
  | grep -v "$(gcloud run services describe qrl-trading-api --region asia-southeast1 --format='value(status.latestReadyRevisionName)')" \
  | xargs -r -I{} gcloud run revisions delete {} --project ${PROJECT_ID} --region asia-southeast1 --platform managed --quiet
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

### PowerShell 一鍵部署（可選）
```powershell
$PROJECT_ID = "qrl-api"
$REGION = "asia-southeast1"
$SERVICE_NAME = "qrl-trading-api"
$IMAGE_URI = "$REGION-docker.pkg.dev/$PROJECT_ID/qrl-trading-api/$SERVICE_NAME:latest"
$DOCKERFILE_DIR = "."

$secrets = @("mexc-api-key","mexc-secret-key","redis-url")
foreach ($s in $secrets) {
    if (-not (gcloud secrets describe $s -q 2>$null)) {
        gcloud secrets create $s --replication-policy="automatic"
    }
}
$envMap = @{"mexc-api-key"="MEXC_API_KEY";"mexc-secret-key"="MEXC_SECRET_KEY";"redis-url"="REDIS_URL"}
foreach ($pair in $envMap.GetEnumerator()) {
    $val = (Select-String -Path .env -Pattern "^$($pair.Value)=").ToString().Split('=')[1].Trim()
    echo $val | gcloud secrets versions add $($pair.Key) --data-file=-
}
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
foreach ($s in $secrets) {
    gcloud secrets add-iam-policy-binding $s \
        --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor"
}

gcloud builds submit $DOCKERFILE_DIR --tag $IMAGE_URI
gcloud run deploy $SERVICE_NAME --image=$IMAGE_URI --region=$REGION \
  --platform=managed --allow-unauthenticated --memory=512Mi --cpu=1 \
  --min-instances=0 --max-instances=10 --concurrency=80 --timeout=300s \
  --set-secrets "MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest,REDIS_URL=redis-url:latest"
```
