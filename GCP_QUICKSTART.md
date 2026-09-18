# Google Cloud Platform - Quick Start Guide

## 🚀 Deploy in 10 Minutes

### Prerequisites
- Google Cloud Account (https://cloud.google.com)
- gcloud CLI installed
- YouTube channel and API credentials
- Billing enabled on GCP

### Step 1: Install gcloud CLI (if not installed)
```bash
# macOS
brew install google-cloud-sdk

# Ubuntu/Debian
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows
# Download from https://cloud.google.com/sdk/docs/install
```

### Step 2: Authenticate with GCP
```bash
gcloud auth login
gcloud auth application-default login
```

### Step 3: Run Automated Setup (Recommended)
```bash
cd ~/tamil_video_generator
chmod +x setup_gcp.sh
./setup_gcp.sh
```

This script will:
- ✅ Create GCP project
- ✅ Enable required APIs
- ✅ Create service account
- ✅ Grant permissions
- ✅ Create Cloud Storage bucket
- ✅ Build and deploy to Cloud Run
- ✅ Create Cloud Scheduler jobs

### Step 4: Upload YouTube Credentials
```bash
# Get your YouTube credentials from Google Cloud Console
# Save as youtube_credentials.json

gsutil cp youtube_credentials.json gs://tamil-video-generator-bucket/
```

### Step 5: Test the Deployment
```bash
# Get Cloud Run URL from setup output
CLOUD_RUN_URL="https://your-cloud-run-url"

# Test video generation
curl -X POST $CLOUD_RUN_URL/generate

# Check status
curl $CLOUD_RUN_URL/status

# View configuration
curl $CLOUD_RUN_URL/config
```

### Step 6: Monitor
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Check scheduler jobs
gcloud scheduler jobs list

# View bucket contents
gsutil ls -r gs://tamil-video-generator-bucket/
```

## 📊 Architecture

```
Cloud Scheduler (8 AM & 8 PM)
        ↓
Cloud Run (Serverless)
        ↓
Cloud Storage (Videos, Audio, Images)
        ↓
YouTube (Published Videos)
```

## 💰 Estimated Costs

| Service | Free Tier | Estimated Cost |
|---------|-----------|---|
| Cloud Run | 2M requests/month | $5-10 |
| Cloud Storage | 5 GB/month | $1-2 |
| Cloud TTS | 1M chars/month | $5-10 |
| Cloud Scheduler | 3 jobs free | $0 |
| **Total** | - | **$10-20/month** |

## 🔧 Customize Schedule

### Change Morning Time
```bash
gcloud scheduler jobs update tamil-video-morning \
  --schedule="0 6 * * *"  # 6:00 AM
```

### Change Evening Time
```bash
gcloud scheduler jobs update tamil-video-evening \
  --schedule="0 18 * * *"  # 6:00 PM
```

### Change Timezone
```bash
gcloud scheduler jobs update tamil-video-morning \
  --timezone="America/New_York"
```

## 📝 Configuration

Edit environment variables in Cloud Run:

```bash
gcloud run deploy tamil-video-generator \
  --update-env-vars \
    VIDEO_RESOLUTION=1280x720,\
    VIDEO_FPS=24,\
    TTS_SPEAKING_RATE=0.9
```

## 🧹 Cleanup

### Delete Everything
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
gcloud iam service-accounts delete \
  tamil-video-generator@PROJECT_ID.iam.gserviceaccount.com

# Delete project
gcloud projects delete tamil-video-generator
```

## 🐛 Troubleshooting

### Cloud Run not responding
```bash
# Check service status
gcloud run services describe tamil-video-generator

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 100

# Redeploy
gcloud run deploy tamil-video-generator --image gcr.io/PROJECT_ID/tamil-video-generator
```

### Scheduler jobs not running
```bash
# Check job status
gcloud scheduler jobs describe tamil-video-morning

# Manually trigger
gcloud scheduler jobs run tamil-video-morning

# View job execution history
gcloud logging read "resource.type=cloud_scheduler_job" --limit 50
```

### Out of storage
```bash
# Check bucket size
gsutil du -s gs://tamil-video-generator-bucket/

# Manually cleanup
gsutil -m rm -r gs://tamil-video-generator-bucket/videos/*
```

### YouTube upload failing
```bash
# Check if credentials are uploaded
gsutil ls gs://tamil-video-generator-bucket/youtube_credentials.json

# View error logs
gcloud logging read "severity=ERROR" --limit 50
```

## 📊 Monitoring

### View Real-time Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --format "table(timestamp, severity, jsonPayload.message)"
```

### Check Metrics
```bash
# Cloud Run metrics
gcloud monitoring metrics-descriptors list --filter="metric.type:run*"

# View specific metric
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"'
```

### Set Up Alerts
```bash
# Create alert policy (via Cloud Console)
# Go to Monitoring → Alerting → Create Policy
```

## 🔐 Security

### Best Practices
1. ✅ Use service accounts (not personal credentials)
2. ✅ Enable Cloud Audit Logs
3. ✅ Encrypt Cloud Storage
4. ✅ Use VPC if needed
5. ✅ Restrict IAM permissions
6. ✅ Rotate service account keys regularly

### View Audit Logs
```bash
gcloud logging read "protoPayload.methodName=storage.buckets.update" --limit 10
```

## 📈 Scaling

### Increase Cloud Run Memory
```bash
gcloud run deploy tamil-video-generator \
  --memory 4Gi \
  --timeout 3600
```

### Set Min/Max Instances
```bash
gcloud run deploy tamil-video-generator \
  --min-instances 1 \
  --max-instances 10
```

## 🎯 Next Steps

1. ✅ Run `./setup_gcp.sh`
2. ✅ Upload YouTube credentials
3. ✅ Test with `curl -X POST $CLOUD_RUN_URL/generate`
4. ✅ Monitor logs with `gcloud logging read`
5. ✅ Verify videos on YouTube
6. ✅ Adjust schedule as needed

## 📚 Additional Resources

- [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) - Detailed guide
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Cloud TTS Documentation](https://cloud.google.com/text-to-speech/docs)

## 💬 Support

For issues:
1. Check logs: `gcloud logging read`
2. Review GCP_DEPLOYMENT.md troubleshooting section
3. Check Cloud Run service status
4. Verify IAM permissions
5. Check Cloud Storage bucket configuration

---

**Your Tamil Video Generator is now running on Google Cloud Platform!**

Videos will be generated automatically at 8:00 AM and 8:00 PM (Asia/Kolkata timezone).
