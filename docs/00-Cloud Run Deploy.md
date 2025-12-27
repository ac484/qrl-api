# ==============================
# QRL Trading API - Cloud Run Deployment
# ==============================

# ===== 1️⃣ 建立 Secret（只建立一次） =====
$secrets = @("mexc-api-key","mexc-api-secret","redis-url")

foreach ($s in $secrets) {
    if (-not (gcloud secrets describe $s -q 2>$null)) {
        gcloud secrets create $s --replication-policy="automatic"
        Write-Host "Secret $s created."
    } else {
        Write-Host "Secret $s already exists. Skipping creation."
    }
}

# ===== 2️⃣ 從 .env 讀取值加入 Secret =====
$MEXC_API_KEY = (Select-String -Path .env -Pattern '^MEXC_API_KEY=').ToString().Split('=')[1].Trim()
$MEXC_SECRET_KEY = (Select-String -Path .env -Pattern '^MEXC_SECRET_KEY=').ToString().Split('=')[1].Trim()
$REDIS_URL = (Select-String -Path .env -Pattern '^REDIS_URL=').ToString().Split('=')[1].Trim()

echo $MEXC_API_KEY | gcloud secrets versions add mexc-api-key --data-file=-
echo $MEXC_SECRET_KEY | gcloud secrets versions add mexc-api-secret --data-file=-
echo $REDIS_URL | gcloud secrets versions add redis-url --data-file=-

# ===== 3️⃣ 授權 Cloud Build 讀取 Secret =====
$PROJECT_NUMBER = gcloud projects describe qrl-api --format='value(projectNumber)'

foreach ($s in $secrets) {
    # 授權給 Cloud Build service account
    gcloud secrets add-iam-policy-binding $s `
        --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com `
        --role='roles/secretmanager.secretAccessor'
    # 授權給 Cloud Run service account (Compute default)
    gcloud secrets add-iam-policy-binding $s `
        --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com `
        --role='roles/secretmanager.secretAccessor'
}

# ===== 4️⃣ 部署 Cloud Run =====
gcloud run deploy qrl-trading-api `
  --image=asia-southeast1-docker.pkg.dev/qrl-api/qrl-trading-api/qrl-trading-api:latest `
  --region=asia-southeast1 `
  --platform=managed `
  --allow-unauthenticated `
  --set-env-vars "DEBUG=False,TRADING_PAIR=QRL-USDT,MAX_DAILY_TRADES=8,MEXC_SUBACCOUNT=your_subaccount_name,MEXC_BASE_URL=https://api.mexc.com,CORE_POSITION_PERCENT=70.0,SWING_POSITION_PERCENT=20.0,ACTIVE_POSITION_PERCENT=10.0,MIN_USDT_RESERVE_PERCENT=15.0,MAX_USDT_RESERVE_PERCENT=25.0,USDT_USAGE_PERCENT=60.0,LONG_MA_PERIOD=20,DCA_DIP_THRESHOLD=0.98,DCA_INTERVAL_HOURS=24,ACTIVE_SELL_THRESHOLD=1.05,SWING_SELL_THRESHOLD=1.15,ACTIVE_SELL_PERCENT=50.0,SWING_SELL_PERCENT=30.0,BUYBACK_DROP_PERCENT=5.0,MAX_DAILY_LOSS_PERCENT=3.0,MIN_USDT_FOR_TRADE=10.0,ALLOW_BUY_ABOVE_COST=False,MIN_SELL_PROFIT_PERCENT=3.0" `
  --set-secrets "MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-api-secret:latest,REDIS_URL=redis-url:latest"

Write-Host "✅ Deployment script finished. Cloud Run should be up!"
