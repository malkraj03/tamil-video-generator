#!/bin/bash

# Tamil Video Generator - GCP Setup Script
# Automates GCP project setup and deployment

set -e

echo "=========================================="
echo "Tamil Video Generator - GCP Setup"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
PROJECT_NAME="tamil-video-generator"
REGION="us-central1"
BUCKET_NAME="tamil-video-generator-bucket"
SERVICE_ACCOUNT_NAME="tamil-video-generator"
CLOUD_RUN_SERVICE="tamil-video-generator"

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"
command -v gcloud &> /dev/null || { echo -e "${RED}gcloud CLI not found${NC}"; exit 1; }
command -v gsutil &> /dev/null || { echo -e "${RED}gsutil not found${NC}"; exit 1; }
echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Step 1: Create GCP Project
echo -e "${BLUE}Step 1: Creating GCP Project...${NC}"
if gcloud projects describe $PROJECT_NAME &> /dev/null; then
    echo -e "${YELLOW}Project already exists${NC}"
else
    gcloud projects create $PROJECT_NAME --name="Tamil Video Generator"
    echo -e "${GREEN}✓ Project created${NC}"
fi
gcloud config set project $PROJECT_NAME
echo ""

# Step 2: Enable APIs
echo -e "${BLUE}Step 2: Enabling required APIs...${NC}"
gcloud services enable \
  run.googleapis.com \
  scheduler.googleapis.com \
  storage-api.googleapis.com \
  texttospeech.googleapis.com \
  youtube.googleapis.com \
  logging.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudbuild.googleapis.com
echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Step 3: Create Service Account
echo -e "${BLUE}Step 3: Creating Service Account...${NC}"
if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_NAME}@${PROJECT_NAME}.iam.gserviceaccount.com &> /dev/null; then
    echo -e "${YELLOW}Service account already exists${NC}"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
      --display-name="Tamil Video Generator Service Account"
    echo -e "${GREEN}✓ Service account created${NC}"
fi

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_NAME}.iam.gserviceaccount.com"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Step 4: Grant Permissions
echo -e "${BLUE}Step 4: Granting permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_NAME \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/storage.admin \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_NAME \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/run.admin \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_NAME \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/scheduler.admin \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_NAME \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/texttospeech.admin \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_NAME \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/logging.logWriter \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_NAME \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/iam.serviceAccountUser \
  --quiet

echo -e "${GREEN}✓ Permissions granted${NC}"
echo ""

# Step 5: Create Service Account Key
echo -e "${BLUE}Step 5: Creating Service Account Key...${NC}"
KEY_FILE="$HOME/gcp-key.json"
if [ ! -f "$KEY_FILE" ]; then
    gcloud iam service-accounts keys create $KEY_FILE \
      --iam-account=$SERVICE_ACCOUNT_EMAIL
    echo -e "${GREEN}✓ Key created: $KEY_FILE${NC}"
else
    echo -e "${YELLOW}Key already exists: $KEY_FILE${NC}"
fi
echo ""

# Step 6: Create Cloud Storage Bucket
echo -e "${BLUE}Step 6: Creating Cloud Storage Bucket...${NC}"
if gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
    echo -e "${YELLOW}Bucket already exists${NC}"
else
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo -e "${GREEN}✓ Bucket created${NC}"
fi

# Set lifecycle policy
cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 14}
      }
    ]
  }
}
EOF

gsutil lifecycle set /tmp/lifecycle.json gs://$BUCKET_NAME
echo -e "${GREEN}✓ Lifecycle policy set (auto-delete after 14 days)${NC}"
echo ""

# Step 7: Build and Deploy to Cloud Run
echo -e "${BLUE}Step 7: Building Docker image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_NAME/$CLOUD_RUN_SERVICE \
  -f Dockerfile.cloudrun .
echo -e "${GREEN}✓ Docker image built${NC}"
echo ""

echo -e "${BLUE}Step 8: Deploying to Cloud Run...${NC}"
gcloud run deploy $CLOUD_RUN_SERVICE \
  --image gcr.io/$PROJECT_NAME/$CLOUD_RUN_SERVICE \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --timeout 3600 \
  --service-account $SERVICE_ACCOUNT_EMAIL \
  --set-env-vars \
    GCP_PROJECT_ID=$PROJECT_NAME,\
    GCP_BUCKET_NAME=$BUCKET_NAME,\
    GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-key.json,\
    VIDEO_RESOLUTION=1920x1080,\
    VIDEO_FPS=30,\
    VIDEO_DURATION_MAX=20,\
    TTS_VOICE=ta-IN-Standard-A,\
    TTS_SPEAKING_RATE=1.0,\
    DATABASE_PATH=/tmp/videos.db \
  --allow-unauthenticated \
  --quiet

echo -e "${GREEN}✓ Deployed to Cloud Run${NC}"
echo ""

# Step 9: Get Cloud Run URL
echo -e "${BLUE}Step 9: Getting Cloud Run URL...${NC}"
CLOUD_RUN_URL=$(gcloud run services describe $CLOUD_RUN_SERVICE \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo -e "${GREEN}✓ Cloud Run URL: $CLOUD_RUN_URL${NC}"
echo ""

# Step 10: Create Cloud Scheduler Jobs
echo -e "${BLUE}Step 10: Creating Cloud Scheduler jobs...${NC}"

# Morning job
if gcloud scheduler jobs describe tamil-video-morning &> /dev/null; then
    echo -e "${YELLOW}Morning job already exists${NC}"
else
    gcloud scheduler jobs create http tamil-video-morning \
      --schedule="0 8 * * *" \
      --timezone="Asia/Kolkata" \
      --uri="$CLOUD_RUN_URL/generate" \
      --http-method=POST \
      --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
      --oidc-token-audience="$CLOUD_RUN_URL" \
      --quiet
    echo -e "${GREEN}✓ Morning job created (8:00 AM)${NC}"
fi

# Evening job
if gcloud scheduler jobs describe tamil-video-evening &> /dev/null; then
    echo -e "${YELLOW}Evening job already exists${NC}"
else
    gcloud scheduler jobs create http tamil-video-evening \
      --schedule="0 20 * * *" \
      --timezone="Asia/Kolkata" \
      --uri="$CLOUD_RUN_URL/generate" \
      --http-method=POST \
      --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
      --oidc-token-audience="$CLOUD_RUN_URL" \
      --quiet
    echo -e "${GREEN}✓ Evening job created (8:00 PM)${NC}"
fi

# Cleanup job
if gcloud scheduler jobs describe tamil-video-cleanup &> /dev/null; then
    echo -e "${YELLOW}Cleanup job already exists${NC}"
else
    gcloud scheduler jobs create http tamil-video-cleanup \
      --schedule="0 2 * * 0" \
      --timezone="Asia/Kolkata" \
      --uri="$CLOUD_RUN_URL/cleanup" \
      --http-method=POST \
      --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
      --oidc-token-audience="$CLOUD_RUN_URL" \
      --quiet
    echo -e "${GREEN}✓ Cleanup job created (Weekly Sunday 2:00 AM)${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✓ GCP Setup Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "  Project ID: $PROJECT_NAME"
echo "  Region: $REGION"
echo "  Bucket: gs://$BUCKET_NAME"
echo "  Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "  Cloud Run URL: $CLOUD_RUN_URL"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Upload YouTube credentials:"
echo "     gsutil cp youtube_credentials.json gs://$BUCKET_NAME/"
echo ""
echo "  2. Test video generation:"
echo "     curl -X POST $CLOUD_RUN_URL/generate"
echo ""
echo "  3. Check status:"
echo "     curl $CLOUD_RUN_URL/status"
echo ""
echo "  4. View logs:"
echo "     gcloud logging read 'resource.type=cloud_run_revision' --limit 50"
echo ""
echo "  5. Manually trigger jobs:"
echo "     gcloud scheduler jobs run tamil-video-morning"
echo "     gcloud scheduler jobs run tamil-video-evening"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  See GCP_DEPLOYMENT.md for detailed information"
echo ""
echo "=========================================="
