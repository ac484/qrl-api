gcloud scheduler jobs create http 01-min-job --schedule="*/1 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/01-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="01-min-job"


gcloud scheduler jobs create http 05-min-job --schedule="*/5 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/05-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Sync MEXC account balance to Redis every 5 minute"

gcloud scheduler jobs create http 15-min-job --schedule="*/15 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/15-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Update QRL/USDT price every 15 minutes"

gcloud scheduler jobs create http 30-min-job --schedule="*/30 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/30-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Update cost and PnL every 30 minutes"



gcloud run revisions list --project qrl-api --service qrl-trading-api --platform managed --region asia-southeast1 --format "table(REVISION, TRAFFIC, CREATED, LAST_DEPLOYED, CONDITIONS)"

gcloud run revisions list --project qrl-api --service qrl-trading-api --platform managed --region asia-southeast1 --format "value(REVISION)" | Where-Object {$_ -ne "qrl-trading-api-00144-ljp"} | ForEach-Object { gcloud run revisions delete $_ --project qrl-api --region asia-southeast1 --platform managed --quiet }


gcloud builds submit --config=cloudbuild.yaml .

gcloud builds submit --tag gcr.io/qrl-api/qrl-trading-api . && gcloud run deploy qrl-trading-api --image gcr.io/qrl-api/qrl-trading-api --platform managed --region asia-east1 --allow-unauthenticated


gcloud run deploy qrl-trading-api \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated=false \
  --platform managed


gcloud run services add-iam-policy-binding qrl-trading-api \
  --member="serviceAccount:qrl-api@appspot.gserviceaccount.com" \
  --role="roles/run.invoker" \
  --region=asia-southeast1

gcloud projects add-iam-policy-binding 545492969490 \
  --member="serviceAccount:qrl-api@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud scheduler jobs create http keep-alive-job \
  --schedule="*/30 * * * *" \
  --time-zone="Asia/Taipei" \
  --http-method=POST \
  --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/runtime" \
  --oidc-service-account-email="qrl-api@appspot.gserviceaccount.com" \
  --oidc-token-audience="https://qrl-trading-api-545492969490.asia-southeast1.run.app" \
  --message-body='{"job":"KEEP_ALIVE"}'

gcloud scheduler jobs create http ws-recover-job \
  --schedule="*/30 * * * *" \
  --time-zone="Asia/Taipei" \
  --http-method=POST \
  --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/runtime" \
  --oidc-service-account-email="qrl-api@appspot.gserviceaccount.com" \
  --oidc-token-audience="https://qrl-trading-api-545492969490.asia-southeast1.run.app" \
  --message-body='{"job":"WS_RECOVER"}'

gcloud scheduler jobs create http health-check-job \
  --schedule="*/30 * * * *" \
  --time-zone="Asia/Taipei" \
  --http-method=POST \
  --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/runtime" \
  --oidc-service-account-email="qrl-api@appspot.gserviceaccount.com" \
  --oidc-token-audience="https://qrl-trading-api-545492969490.asia-southeast1.run.app" \
  --message-body='{"job":"HEALTH_CHECK"}'
