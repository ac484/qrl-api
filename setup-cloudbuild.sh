#!/bin/bash
# Quick setup script for Cloud Build deployment
# Usage: ./setup-cloudbuild.sh PROJECT_ID REGION

set -e

PROJECT_ID=${1:-$(gcloud config get-value project)}
REGION=${2:-asia-southeast1}

echo "🚀 Setting up Cloud Build for project: $PROJECT_ID"
echo "📍 Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "✅ Enabling required GCP APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create Artifact Registry repository
echo "✅ Creating Artifact Registry repository..."
gcloud artifacts repositories create qrl-trading-api \
  --repository-format=docker \
  --location=$REGION \
  --description="QRL Trading Bot Docker images" \
  2>/dev/null || echo "Repository already exists"

# Grant Cloud Build service account permissions
echo "✅ Granting Cloud Build permissions..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin" \
  --no-user-output-enabled 2>/dev/null || true

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser" \
  --no-user-output-enabled 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Create secrets in Secret Manager:"
echo "   echo -n 'YOUR_MEXC_API_KEY' | gcloud secrets create mexc-api-key --data-file=-"
echo "   echo -n 'YOUR_MEXC_API_SECRET' | gcloud secrets create mexc-api-secret --data-file=-"
echo ""
echo "2. Update cloudbuild.yaml with your Redis URL and other settings"
echo ""
echo "3. Deploy with:"
echo "   gcloud builds submit --config cloudbuild.yaml"
echo ""
echo "🎉 You're ready to deploy!"
