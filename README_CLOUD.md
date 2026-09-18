# Tamil Video Generator - Complete Guide (Local + Cloud)

A fully automated system to generate and publish Tamil history and fun facts videos to YouTube daily (twice per day). **Now with full Google Cloud Platform support for serverless deployment!**

## 🎯 Two Deployment Options

### Option 1: Local Machine (Traditional)
- Run on your computer
- Full control over resources
- Requires system dependencies (FFmpeg, ImageMagick)
- See [README.md](README.md) and [SETUP.md](SETUP.md)

### Option 2: Google Cloud Platform (Recommended)
- Fully serverless and automated
- No local dependencies needed
- Automatic scaling
- Pay only for what you use (~$10-20/month)
- **See [GCP_QUICKSTART.md](GCP_QUICKSTART.md) for quick setup**

## 🚀 Quick Start - Google Cloud Platform

### 1. Prerequisites
```bash
# Install gcloud CLI
brew install google-cloud-sdk  # macOS
# OR download from https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud auth application-default login
```

### 2. Automated Setup (Recommended)
```bash
cd ~/tamil_video_generator
chmod +x setup_gcp.sh
./setup_gcp.sh
```

This script automatically:
- ✅ Creates GCP project
- ✅ Enables required APIs
- ✅ Creates service account
- ✅ Sets up Cloud Storage
- ✅ Builds Docker image
- ✅ Deploys to Cloud Run
- ✅ Creates Cloud Scheduler jobs

### 3. Upload YouTube Credentials
```bash
gsutil cp youtube_credentials.json gs://tamil-video-generator-bucket/
```

### 4. Test
```bash
curl -X POST https://YOUR-CLOUD-RUN-URL/generate
```

That's it! Videos will be generated automatically at 8 AM and 8 PM.

## 📊 Architecture Comparison

### Local Deployment
```
Your Computer
├─ Content Generation
├─ TTS Processing
├─ Video Creation
├─ YouTube Upload
└─ Local Storage
```

### Cloud Deployment
```
Google Cloud Platform
├─ Cloud Run (Video Generation)
├─ Cloud Storage (Videos, Audio, Images)
├─ Cloud Scheduler (Cron Jobs - 2x daily)
├─ Cloud TTS (High-quality speech)
└─ YouTube API (Publishing)
```

## 🔄 How It Works

### Local Version
1. Run scheduler on your machine
2. Generates video every 12 hours
3. Stores files locally
4. Publishes to YouTube

### Cloud Version
1. Cloud Scheduler triggers at 8 AM & 8 PM
2. Cloud Run generates video (serverless)
3. Stores in Cloud Storage (auto-cleanup after 14 days)
4. Publishes to YouTube
5. No local machine needed!

## 💰 Cost Comparison

### Local Deployment
- **Electricity**: $20-50/month
- **Internet**: Included
- **Hardware**: One-time cost
- **Total**: $20-50/month

### Cloud Deployment
- **Cloud Run**: $5-10/month
- **Cloud Storage**: $1-2/month
- **Cloud TTS**: $5-10/month
- **Cloud Scheduler**: Free
- **Total**: $10-20/month

## 📁 New Cloud Files

```
tamil_video_generator/
├── cloud_storage.py           # Cloud Storage integration
├── cloud_tts.py              # Google Cloud TTS
├── cloud_scheduler.py        # Cloud Run handler
├── cloud_run_app.py          # Flask app for Cloud Run
├── Dockerfile.cloudrun       # Cloud Run Docker image
├── requirements-cloud.txt    # Cloud dependencies
├── setup_gcp.sh             # Automated GCP setup
├── GCP_DEPLOYMENT.md        # Detailed GCP guide
├── GCP_QUICKSTART.md        # Quick start guide
└── README_CLOUD.md          # This file
```

## 🎬 Features

### Content Generation
- ✅ 20+ Tamil history and culture facts
- ✅ Intelligent content selection
- ✅ Automatic script generation
- ✅ Metadata and tags

### Audio Production
- ✅ Google Cloud TTS (high quality)
- ✅ Multiple Tamil voices
- ✅ Adjustable speaking rate
- ✅ Background music support

### Video Creation
- ✅ Mixed video styles (3 types)
- ✅ Free stock images
- ✅ Professional effects
- ✅ 1080p @ 30fps

### YouTube Integration
- ✅ Automated upload
- ✅ OAuth 2.0 authentication
- ✅ Metadata management
- ✅ Playlist support

### Cloud Features
- ✅ Serverless execution
- ✅ Automatic scaling
- ✅ Auto-cleanup (14 days)
- ✅ Detailed logging
- ✅ Cost monitoring

## 🔧 Configuration

### Cloud Environment Variables
```bash
GCP_PROJECT_ID          # Your GCP project
GCP_BUCKET_NAME         # Cloud Storage bucket
VIDEO_RESOLUTION        # 1920x1080 (default)
VIDEO_FPS              # 30 (default)
VIDEO_DURATION_MAX     # 20 minutes (default)
TTS_VOICE              # ta-IN-Standard-A (default)
TTS_SPEAKING_RATE      # 1.0 (default)
```

### Customize Schedule
```bash
# Change morning time to 6 AM
gcloud scheduler jobs update tamil-video-morning \
  --schedule="0 6 * * *"

# Change evening time to 6 PM
gcloud scheduler jobs update tamil-video-evening \
  --schedule="0 18 * * *"
```

## 📊 Monitoring

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### Check Status
```bash
curl https://YOUR-CLOUD-RUN-URL/status
```

### View Configuration
```bash
curl https://YOUR-CLOUD-RUN-URL/config
```

### Check Bucket Size
```bash
gsutil du -s gs://tamil-video-generator-bucket/
```

## 🧹 Cleanup

### Manual Cleanup
```bash
# Delete files older than 14 days
curl -X POST https://YOUR-CLOUD-RUN-URL/cleanup
```

### Automatic Cleanup
- Enabled by default
- Deletes files older than 14 days
- Runs weekly on Sunday at 2 AM

## 🐛 Troubleshooting

### Cloud Run not responding
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 100
```

### Scheduler jobs not running
```bash
gcloud scheduler jobs describe tamil-video-morning
gcloud scheduler jobs run tamil-video-morning  # Manual trigger
```

### YouTube upload failing
```bash
# Check if credentials are uploaded
gsutil ls gs://tamil-video-generator-bucket/youtube_credentials.json
```

## 📚 Documentation

- **[GCP_QUICKSTART.md](GCP_QUICKSTART.md)** - 10-minute setup
- **[GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)** - Detailed guide
- **[README.md](README.md)** - Local deployment
- **[SETUP.md](SETUP.md)** - Local installation
- **[API.md](API.md)** - Developer documentation

## 🔐 Security

### Cloud Security Features
- ✅ OAuth 2.0 authentication
- ✅ Service account isolation
- ✅ Encrypted storage
- ✅ Audit logging
- ✅ IAM permissions

### Best Practices
1. Use service accounts (not personal credentials)
2. Enable Cloud Audit Logs
3. Encrypt Cloud Storage
4. Restrict IAM permissions
5. Rotate keys regularly

## 📈 Scaling

### Increase Resources
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

### For Cloud Deployment
1. Read [GCP_QUICKSTART.md](GCP_QUICKSTART.md)
2. Run `./setup_gcp.sh`
3. Upload YouTube credentials
4. Test with `curl -X POST $CLOUD_RUN_URL/generate`
5. Monitor with `gcloud logging read`

### For Local Deployment
1. Read [SETUP.md](SETUP.md)
2. Install dependencies
3. Run `python main.py --mode generate`
4. Run `python main.py --mode start`

## 💡 Tips

### Cost Optimization
- Use auto-cleanup (14 days)
- Reduce video resolution to 720p
- Lower FPS to 24
- Use cheaper Cloud Run region

### Performance Optimization
- Increase Cloud Run memory to 4GB
- Enable min-instances for faster response
- Use Cloud CDN for video delivery

### Monitoring
- Set up Cloud Logging alerts
- Monitor Cloud Run metrics
- Track Cloud Storage usage
- Review Cloud Scheduler job history

## 🆘 Support

### Cloud Issues
- Check [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md) troubleshooting
- Review Cloud Logging
- Verify IAM permissions
- Check Cloud Storage configuration

### Local Issues
- Check [SETUP.md](SETUP.md) troubleshooting
- Review `video_generator.log`
- Run `./verify_installation.sh`
- Check system dependencies

## 📞 Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Cloud Run Guide](https://cloud.google.com/run/docs)
- [Cloud Scheduler Guide](https://cloud.google.com/scheduler/docs)
- [Cloud Storage Guide](https://cloud.google.com/storage/docs)
- [YouTube API Documentation](https://developers.google.com/youtube)

## 🎉 Summary

You now have **two options** for running your Tamil Video Generator:

### Local
- Full control
- Requires system setup
- See [README.md](README.md)

### Cloud (Recommended)
- Fully automated
- No dependencies
- Pay only for usage
- See [GCP_QUICKSTART.md](GCP_QUICKSTART.md)

**Choose cloud for the easiest, most scalable solution!**

---

**Happy video generation! 🎬📹**

*Choose your deployment method and start generating videos today!*
