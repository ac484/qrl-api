# 刪除舊的 Scheduler jobs（如果存在）
gcloud scheduler jobs delete 01-min-job --location=asia-southeast1 --quiet
gcloud scheduler jobs delete 05-min-job --location=asia-southeast1 --quiet
gcloud scheduler jobs delete 15-min-job --location=asia-southeast1 --quiet

# 建立新的 Scheduler jobs
gcloud scheduler jobs create http 01-min-job --schedule="* * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/01-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Sync MEXC account balance to Redis every 1 minute"

gcloud scheduler jobs create http 05-min-job --schedule="*/5 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/05-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Update QRL/USDT price every 5 minutes"

gcloud scheduler jobs create http 15-min-job --schedule="*/15 * * * *" --uri="https://qrl-trading-api-545492969490.asia-southeast1.run.app/tasks/15-min-job" --http-method=POST --headers="X-CloudScheduler=true,Content-Type=application/json" --time-zone="Asia/Taipei" --description="Update cost and PnL every 15 minutes"
