# Google Cloud Platform Deployment Guide

## Overview

This guide explains how to deploy the Tamil Video Generator on Google Cloud Platform (GCP) for fully automated, serverless video generation and publishing.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD PLATFORM                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Cloud Scheduler (Cron Jobs)                                │
│  ├─ 8:00 AM - Trigger video generation                      │
│  └─ 8:00 PM - Trigger video generation                      │
│         ↓                                                     │
│  Cloud Run (Serverless Container)                           │
│  ├─ Generate Tamil content                                  │
│  ├─ Generate speech (Cloud TTS)                             │
│  ├─ Create video                                            │
│  ├─ Upload to YouTube                                       │
│  └─ Upload to Cloud Storage                                 │
│         ↓                                                     │
│  Cloud Storage (Persistent Storage)                         │
│  ├─ videos/ - Generated videos                              │
│  ├─ audio/ - Generated audio files                          │
│  └─ images/ - Thumbnails and images                         │
│         ↓                                                     │
│  Cloud SQL (Optional - for database)                        │
│  └─ Video metadata and statistics                           │
│                                                               │
│  YouTube API                                                 │
│  └─ Automated video publishing                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Google Cloud Account** - https://cloud.google.com
2. **GCP Project** - Create a new project
3. **Billing Enabled** - Enable billing for your project
4. **gcloud CLI** - Install Google Cloud SDK
5. **YouTube Channel** - For publishing videos
6. **YouTube API Credentials** - OAuth 2.0 credentials

## Step 1: Set Up GCP Project

### 1.1 Create Project
```bash
gcloud projects create tamil-video-generator --name="Tamil Video Generator"
gcloud config set project tamil-video-generator
```

### 1.2 Enable Required APIs
```bash
gcloud services enable \
  run.googleapis.com \
  scheduler.googleapis.com \
  storage-api.googleapis.com \
  texttospeech.googleapis.com \
  youtube.googleapis.com \
  logging.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 1.3 Create Service Account
```bash
gcloud iam service-accounts create tamil-video-generator \
  --display-name="Tamil Video Generator Service Account"

# Get service account email
SERVICE_ACCOUNT_EMAIL=$(gcloud iam service-accounts list \
  --filter="displayName:Tamil Video Generator Service Account" \
  --format='value(email)')

echo $SERVICE_ACCOUNT_EMAIL
```

### 1.4 Grant Permissions
```bash
# Cloud Storage
gcloud projects add-iam-policy-binding tamil-video-generator \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/storage.admin

# Cloud Run
gcloud projects add-iam-policy-binding tamil-video-generator \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/run.admin

# Cloud Scheduler
gcloud projects add-iam-policy-binding tamil-video-generator \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/scheduler.admin

# Cloud TTS
gcloud projects add-iam-policy-binding tamil-video-generator \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/texttospeech.admin

# Cloud Logging
gcloud projects add-iam-policy-binding tamil-video-generator \
  --member=serviceAccount:$SERVICE_ACCOUNT_EMAIL \
  --role=roles/logging.logWriter
```

### 1.5 Create Service Account Key
```bash
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=$SERVICE_ACCOUNT_EMAIL

# Keep this file secure!
```

## Step 2: Set Up Cloud Storage

### 2.1 Create Bucket
```bash
gsutil mb -l us-central1 gs://tamil-video-generator-bucket

# Set bucket location (choose closest to you)
# us-central1, europe-west1, asia-south1, etc.
```

### 2.2 Configure Bucket Lifecycle
```bash
cat > lifecycle.json << 'EOF'
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

gsutil lifecycle set lifecycle.json gs://tamil-video-generator-bucket
```

This automatically deletes files older than 14 days.

## Step 3: Prepare YouTube Credentials

### 3.1 Create OAuth Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services → Credentials
3. Click "Create Credentials" → OAuth 2.0 Client ID
4. Choose "Desktop application"
5. Download JSON file
6. Rename to `youtube_credentials.json`

### 3.2 Upload to Cloud Storage
```bash
gsutil cp youtube_credentials.json gs://tamil-video-generator-bucket/
```

## Step 4: Deploy to Cloud Run

### 4.1 Build Docker Image
```bash
# Set project ID
PROJECT_ID=$(gcloud config get-value project)

# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/tamil-video-generator \
  -f Dockerfile.cloudrun .
```

### 4.2 Deploy to Cloud Run
```bash
gcloud run deploy tamil-video-generator \
  --image gcr.io/$PROJECT_ID/tamil-video-generator \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 3600 \
  --service-account $SERVICE_ACCOUNT_EMAIL \
  --set-env-vars \
    GCP_PROJECT_ID=$PROJECT_ID,\
    GCP_BUCKET_NAME=tamil-video-generator-bucket,\
    GOOGLE_APPLICATION_CREDENTIALS=/app/gcp-key.json,\
    VIDEO_RESOLUTION=1920x1080,\
    VIDEO_FPS=30,\
    VIDEO_DURATION_MAX=20,\
    TTS_VOICE=ta-IN-Standard-A,\
    TTS_SPEAKING_RATE=1.0,\
    DATABASE_PATH=/tmp/videos.db \
  --allow-unauthenticated
```

### 4.3 Get Cloud Run URL
```bash
gcloud run services describe tamil-video-generator \
  --platform managed \
  --region us-central1 \
  --format 'value(status.url)'
```

Save this URL - you'll need it for Cloud Scheduler.

## Step 5: Set Up Cloud Scheduler

### 5.1 Create Morning Job (8:00 AM)
```bash
gcloud scheduler jobs create http tamil-video-morning \
  --schedule="0 8 * * *" \
  --timezone="Asia/Kolkata" \
  --uri="https://YOUR-CLOUD-RUN-URL/generate" \
  --http-method=POST \
  --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
  --oidc-token-audience="https://YOUR-CLOUD-RUN-URL"
```

### 5.2 Create Evening Job (8:00 PM)
```bash
gcloud scheduler jobs create http tamil-video-evening \
  --schedule="0 20 * * *" \
  --timezone="Asia/Kolkata" \
  --uri="https://YOUR-CLOUD-RUN-URL/generate" \
  --http-method=POST \
  --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
  --oidc-token-audience="https://YOUR-CLOUD-RUN-URL"
```

### 5.3 Create Cleanup Job (Weekly)
```bash
gcloud scheduler jobs create http tamil-video-cleanup \
  --schedule="0 2 * * 0" \
  --timezone="Asia/Kolkata" \
  --uri="https://YOUR-CLOUD-RUN-URL/cleanup" \
  --http-method=POST \
  --oidc-service-account-email=$SERVICE_ACCOUNT_EMAIL \
  --oidc-token-audience="https://YOUR-CLOUD-RUN-URL"
```

## Step 6: Monitor and Manage

### 6.1 View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=tamil-video-generator" \
  --limit 50 \
  --format json
```

### 6.2 Check Cloud Run Status
```bash
gcloud run services describe tamil-video-generator \
  --platform managed \
  --region us-central1
```

### 6.3 View Scheduler Jobs
```bash
gcloud scheduler jobs list
gcloud scheduler jobs describe tamil-video-morning
```

### 6.4 Check Cloud Storage
```bash
gsutil ls -r gs://tamil-video-generator-bucket/
gsutil du -s gs://tamil-video-generator-bucket/
```

## Step 7: Test Deployment

### 7.1 Manual Trigger
```bash
# Test video generation
curl -X POST https://YOUR-CLOUD-RUN-URL/generate

# Test cleanup
curl -X POST https://YOUR-CLOUD-RUN-URL/cleanup

# Check status
curl https://YOUR-CLOUD-RUN-URL/status

# View config
curl https://YOUR-CLOUD-RUN-URL/config
```

### 7.2 View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 100 \
  --format "table(timestamp, severity, jsonPayload.message)"
```

## Configuration

### Environment Variables
Set these in Cloud Run deployment:

```
GCP_PROJECT_ID          - Your GCP project ID
GCP_BUCKET_NAME         - Cloud Storage bucket name
VIDEO_RESOLUTION        - Video resolution (1920x1080)
VIDEO_FPS               - Frame rate (30)
VIDEO_DURATION_MAX      - Max duration in minutes (20)
TTS_VOICE               - Tamil voice (ta-IN-Standard-A)
TTS_SPEAKING_RATE       - Speech rate (1.0)
DATABASE_PATH           - Database location (/tmp/videos.db)
```

### Customize Schedule
Edit Cloud Scheduler jobs:

```bash
# Update morning job to 6:00 AM
gcloud scheduler jobs update tamil-video-morning \
  --schedule="0 6 * * *"

# Update evening job to 6:00 PM
gcloud scheduler jobs update tamil-video-evening \
  --schedule="0 18 * * *"
```

## Cost Optimization

### 1. Cloud Run Pricing
- **Free tier**: 2 million requests/month
- **Paid**: $0.40 per 1M requests + compute time
- **Estimate**: ~$5-10/month for twice-daily videos

### 2. Cloud Storage Pricing
- **Free tier**: 5 GB/month
- **Paid**: $0.020 per GB
- **Estimate**: ~$1-2/month with auto-cleanup

### 3. Cloud TTS Pricing
- **Free tier**: 1 million characters/month
- **Paid**: $16 per 1M characters
- **Estimate**: ~$5-10/month

### 4. Total Estimated Cost
- **Free tier usage**: ~$0 (within limits)
- **Paid usage**: ~$10-20/month

### 5. Cost Reduction Tips
- Use auto-cleanup (14 days)
- Reduce video resolution to 720p
- Lower FPS to 24
- Use cheaper Cloud Run region

## Troubleshooting

### Cloud Run Deployment Issues

**Issue**: "Permission denied" error
```bash
# Ensure service account has correct permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"
```

**Issue**: "Out of memory" error
```bash
# Increase Cloud Run memory
gcloud run deploy tamil-video-generator \
  --memory 4Gi \
  --region us-central1
```

**Issue**: "Timeout" error
```bash
# Increase timeout
gcloud run deploy tamil-video-generator \
  --timeout 3600 \
  --region us-central1
```

### Cloud Scheduler Issues

**Issue**: Jobs not running
```bash
# Check job status
gcloud scheduler jobs describe tamil-video-morning

# Manually trigger job
gcloud scheduler jobs run tamil-video-morning
```

**Issue**: Wrong timezone
```bash
# List available timezones
gcloud scheduler jobs create http test --help | grep timezone

# Update timezone
gcloud scheduler jobs update tamil-video-morning \
  --timezone="Asia/Kolkata"
```

### Cloud Storage Issues

**Issue**: Files not deleting
```bash
# Check lifecycle configuration
gsutil lifecycle get gs://tamil-video-generator-bucket

# Update lifecycle
gsutil lifecycle set lifecycle.json gs://tamil-video-generator-bucket
```

## Monitoring and Alerts

### 1. Set Up Logging
```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --format json | jq '.[] | {timestamp, severity, message}'
```

### 2. Create Alerts
```bash
# Alert on errors
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Tamil Video Generator Errors" \
  --condition-display-name="High error rate" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

### 3. View Metrics
```bash
# Cloud Run metrics
gcloud monitoring metrics-descriptors list --filter="metric.type:run*"
```

## Backup and Recovery

### 1. Backup Cloud Storage
```bash
# Download all files
gsutil -m cp -r gs://tamil-video-generator-bucket/ ./backup/

# Or use Cloud Storage Transfer Service
```

### 2. Backup Database
```bash
# Download database
gsutil cp gs://tamil-video-generator-bucket/videos.db ./backup/
```

### 3. Restore from Backup
```bash
# Upload files back
gsutil -m cp -r ./backup/* gs://tamil-video-generator-bucket/
```

## Scaling

### 1. Increase Cloud Run Instances
```bash
gcloud run deploy tamil-video-generator \
  --min-instances 1 \
  --max-instances 10 \
  --region us-central1
```

### 2. Use Cloud Tasks for Queue
```bash
# For multiple videos in queue
gcloud tasks queues create tamil-video-queue
```

### 3. Use Pub/Sub for Events
```bash
# For event-driven architecture
gcloud pubsub topics create tamil-video-events
```

## Security Best Practices

1. **Use Service Accounts** - Never use personal credentials
2. **Restrict Permissions** - Use least privilege principle
3. **Encrypt Data** - Enable Cloud Storage encryption
4. **Audit Logs** - Enable Cloud Audit Logs
5. **Secure Secrets** - Use Secret Manager for sensitive data
6. **Network Security** - Use VPC if needed
7. **Monitor Access** - Review IAM bindings regularly

## Cleanup (Delete Resources)

```bash
# Delete Cloud Run service
gcloud run services delete tamil-video-generator

# Delete Cloud Scheduler jobs
gcloud scheduler jobs delete tamil-video-morning
gcloud scheduler jobs delete tamil-video-evening
gcloud scheduler jobs delete tamil-video-cleanup

# Delete Cloud Storage bucket
gsutil -m rm -r gs://tamil-video-generator-bucket

# Delete service account
gcloud iam service-accounts delete $SERVICE_ACCOUNT_EMAIL

# Delete project (optional)
gcloud projects delete tamil-video-generator
```

## Next Steps

1. Deploy to Cloud Run
2. Set up Cloud Scheduler jobs
3. Monitor logs and metrics
4. Test with manual triggers
5. Verify YouTube uploads
6. Adjust schedule as needed
7. Monitor costs

## Support

For issues:
1. Check Cloud Logging
2. Review Cloud Run metrics
3. Check Cloud Scheduler job history
4. Verify IAM permissions
5. Check Cloud Storage bucket configuration

---

**Your Tamil Video Generator is now running on Google Cloud Platform!**
