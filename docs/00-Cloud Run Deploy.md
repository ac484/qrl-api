gcloud scheduler jobs create http 01-min-job --schedule="* * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/01-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Sync MEXC account balance to Redis every 1 minute"

gcloud scheduler jobs create http 05-min-job --schedule="*/5 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/05-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Update QRL/USDT price every 5 minutes"

gcloud scheduler jobs create http 15-min-job --schedule="*/15 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/15-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Update cost and PnL every 15 minutes"



gcloud run revisions list --project qrl-api --service qrl-trading-api --platform managed --region asia-southeast1 --format "table(REVISION, TRAFFIC, CREATED, LAST_DEPLOYED, CONDITIONS)"

gcloud run revisions list --project qrl-api --service qrl-trading-api --platform managed --region asia-southeast1 --format "value(REVISION)" | Where-Object {$_ -ne "qrl-trading-api-00071-ljp"} | ForEach-Object { gcloud run revisions delete $_ --project qrl-api --region asia-southeast1 --platform managed --quiet }


gcloud builds submit --config=cloudbuild.yaml .

gcloud builds submit --tag gcr.io/qrl-api/qrl-trading-api . && gcloud run deploy qrl-trading-api --image gcr.io/qrl-api/qrl-trading-api --platform managed --region asia-east1 --allow-unauthenticated

# ==============================
# QRL Trading API - One-Click Deployment (PowerShell)
# ==============================

# ===== 0️⃣ 變數設定 =====
$PROJECT_ID = "qrl-api"
$REGION = "asia-southeast1"
$SERVICE_NAME = "qrl-trading-api"
$IMAGE_URI = "$REGION-docker.pkg.dev/$PROJECT_ID/qrl-trading-api/$SERVICE_NAME:latest"
$DOCKERFILE_DIR = "."  # Docker build context

# ===== 1️⃣ 建立 Secret（如果不存在） =====
$secrets = @("mexc-api-key","mexc-secret-key","redis-url")

foreach ($s in $secrets) {
    if (-not (gcloud secrets describe $s -q 2>$null)) {
        Write-Host "Creating secret: $s"
        gcloud secrets create $s --replication-policy="automatic"
    } else {
        Write-Host "Secret $s already exists. Skipping creation."
    }
}

# ===== 2️⃣ 從 .env 讀取值加入 Secret =====
$MEXC_API_KEY = (Select-String -Path .env -Pattern '^MEXC_API_KEY=').ToString().Split('=')[1].Trim()
$MEXC_SECRET_KEY = (Select-String -Path .env -Pattern '^MEXC_SECRET_KEY=').ToString().Split('=')[1].Trim()
$REDIS_URL = (Select-String -Path .env -Pattern '^REDIS_URL=').ToString().Split('=')[1].Trim()

Write-Host "Updating secrets with .env values..."
echo $MEXC_API_KEY | gcloud secrets versions add mexc-api-key --data-file=-
echo $MEXC_SECRET_KEY | gcloud secrets versions add mexc-secret-key --data-file=-
echo $REDIS_URL | gcloud secrets versions add redis-url --data-file=-

# ===== 3️⃣ 授權 Cloud Run Service Account 讀取 Secret =====
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

foreach ($s in $secrets) {
    Write-Host "Granting Secret Accessor role for $s to Cloud Run service account..."
    gcloud secrets add-iam-policy-binding $s `
        --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" `
        --role="roles/secretmanager.secretAccessor"
}

# ===== 4️⃣ Build Docker image =====
Write-Host "Building Docker image..."
gcloud builds submit $DOCKERFILE_DIR `
    --tag $IMAGE_URI

# ===== 5️⃣ Deploy Cloud Run =====
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME `
    --image=$IMAGE_URI `
    --region=$REGION `
    --platform=managed `
    --allow-unauthenticated `
    --memory=512Mi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=10 `
    --concurrency=80 `
    --timeout=300s `
    --set-secrets "MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest,REDIS_URL=redis-url:latest"

Write-Host "✅ Deployment finished. Cloud Run service [$SERVICE_NAME] should be up!"
