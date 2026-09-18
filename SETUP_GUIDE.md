# Tamil Video Generator - Complete Setup Guide

This guide will help you set up the automated Tamil video generator that runs in the cloud (GitHub Actions) for FREE and publishes videos to YouTube twice a day.

## Architecture Overview

```
GitHub Actions (FREE cloud) runs twice daily at 8:00 AM & 8:00 PM IST
    |
    v
Content Generator --> edge-tts (FREE Tamil TTS) --> Video Creator (Pillow + moviepy)
    |
    v
YouTube Data API --> Uploads video to your YouTube channel
```

**Everything is FREE:**
- GitHub Actions: Free for public repos (unlimited minutes)
- edge-tts: Free Microsoft TTS with excellent Tamil voices
- Pillow + moviepy + ffmpeg: Free video creation
- YouTube Data API: Free (10,000 units/day, each upload = 1,600 units)

---

## Step-by-Step Setup

### STEP 1: Create a YouTube Channel (if you don't have one)

1. Go to [YouTube](https://www.youtube.com)
2. Sign in with your Google account
3. Click your profile picture -> "Create a channel"
4. Set channel name (e.g., "Tamil History & Fun Facts")
5. Done!

---

### STEP 2: Create Google Cloud Project & Enable YouTube API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top -> "New Project"
3. Project name: `tamil-video-generator` -> Click "Create"
4. Select the project you just created
5. Go to **APIs & Services** -> **Library** (left sidebar)
6. Search for **"YouTube Data API v3"**
7. Click on it -> Click **"ENABLE"**

---

### STEP 3: Configure OAuth Consent Screen

1. In Google Cloud Console, go to **APIs & Services** -> **OAuth consent screen**
2. Select **"External"** -> Click "Create"
3. Fill in:
   - App name: `Tamil Video Generator`
   - User support email: Your email
   - Developer contact: Your email
4. Click **"Save and Continue"**
5. On Scopes page, click **"Save and Continue"** (skip this)
6. On Test users page, click **"Add Users"**
7. Add YOUR Google email (the one with the YouTube channel)
8. Click **"Save and Continue"** -> **"Back to Dashboard"**

---

### STEP 4: Create OAuth Credentials

1. Go to **APIs & Services** -> **Credentials**
2. Click **"+ Create Credentials"** -> **"OAuth client ID"**
3. Application type: **"Desktop app"**
4. Name: `Tamil Video Generator`
5. Click **"Create"**
6. Click **"Download JSON"** (the download icon)
7. Save the downloaded file as `credentials.json` in the project folder

---

### STEP 5: Get YouTube Refresh Token (Run Locally Once)

This step must be done on your local machine (it opens a browser).

```bash
# Navigate to the project
cd tamil_video_generator

# Install dependencies
pip install -r requirements.txt

# Run the auth setup script
python auth_setup.py
```

A browser window will open:
1. Sign in with your Google account (the one with the YouTube channel)
2. Click "Continue" (you may see a warning about unverified app - click "Advanced" -> "Go to Tamil Video Generator")
3. Grant ALL permissions
4. The script will print 3 values:

```
YOUTUBE_CLIENT_ID=xxxxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxxxx
YOUTUBE_REFRESH_TOKEN=1//xxxxx
```

**Copy these 3 values - you'll need them in the next step!**

---

### STEP 6: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click **"+"** -> **"New repository"**
3. Repository name: `tamil-video-generator`
4. Set to **Public** (required for free GitHub Actions)
5. Click **"Create repository"**

---

### STEP 7: Push Code to GitHub

Run these commands in your terminal:

```bash
cd tamil_video_generator

# Initialize git
git init
git add .
git commit -m "Initial commit: Tamil video generator"

# Add your GitHub repo as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/tamil-video-generator.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

### STEP 8: Add YouTube Secrets to GitHub

1. Go to your GitHub repository page
2. Click **"Settings"** tab (top menu)
3. Click **"Secrets and variables"** -> **"Actions"** (left sidebar)
4. Click **"New repository secret"** and add each:

| Secret Name | Value |
|---|---|
| `YOUTUBE_CLIENT_ID` | The client ID from Step 5 |
| `YOUTUBE_CLIENT_SECRET` | The client secret from Step 5 |
| `YOUTUBE_REFRESH_TOKEN` | The refresh token from Step 5 |

---

### STEP 9: Test the Workflow

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Click **"Generate Tamil Video & Upload to YouTube"** (left sidebar)
4. Click **"Run workflow"** (dropdown button on right)
5. Optionally set:
   - Duration: `300` (5 minutes)
   - Resolution: `1280x720`
   - Skip upload: `true` (for first test without uploading)
6. Click **"Run workflow"**
7. Click on the running workflow to see progress

**First test:** Run with `skip_upload: true` to verify video generation works.
**Second test:** Run with `skip_upload: false` to test YouTube upload.

---

### STEP 10: Verify Automatic Schedule

The workflow is configured to run automatically:
- **8:00 AM IST** (2:30 AM UTC) - Morning video
- **8:00 PM IST** (2:30 PM UTC) - Evening video

You can verify by checking the "Actions" tab daily.

---

## How It Works

```
1. GitHub Actions triggers at scheduled time
2. Ubuntu runner starts with Python, ffmpeg, Tamil fonts
3. Content Generator picks random Tamil facts (tracks what's been used)
4. edge-tts converts Tamil text to speech (Microsoft Neural voices)
5. Video Creator generates gradient backgrounds with text overlays
6. moviepy assembles images + audio into MP4 video
7. YouTube API uploads the video to your channel
8. Runner cleans up and shuts down
```

---

## Customization

### Change Video Schedule
Edit `.github/workflows/generate_video.yml`:
```yaml
schedule:
  - cron: '30 2 * * *'   # Change first time (UTC)
  - cron: '30 14 * * *'  # Change second time (UTC)
```

Use [crontab.guru](https://crontab.guru/) to convert times.

### Change Video Duration
Edit the workflow or pass via manual trigger:
- Default: 300 seconds (5 minutes)
- For longer videos: 600 (10 min), 900 (15 min)

### Change Voice
Available voices (all free):
| Key | Voice | Language |
|-----|-------|----------|
| `male_in` | ValluvarNeural | Indian Tamil Male |
| `female_in` | PallaviNeural | Indian Tamil Female |
| `male_lk` | KumarNeural | Sri Lankan Tamil Male |
| `female_lk` | SaranyaNeural | Sri Lankan Tamil Female |

Edit the `--voice` argument in the workflow file.

### Add More Content
Edit `content_database.py` to add more facts to any category.

---

## Troubleshooting

### "YouTube upload failed"
- Check that all 3 secrets are set correctly in GitHub
- The refresh token may have expired. Re-run `python auth_setup.py` locally
- Check YouTube Data API quota in Google Cloud Console

### "Video generation failed"
- Check the GitHub Actions logs (Actions tab -> click on the failed run)
- Try running locally first: `python generate_once.py --skip-upload`

### "No Tamil fonts found"
- The workflow installs `fonts-noto` automatically
- If testing locally on Mac: fonts may not render Tamil perfectly, but the cloud version (Ubuntu) will

### "OAuth consent screen - unverified app"
- This is normal for personal projects
- Click "Advanced" -> "Go to Tamil Video Generator (unsafe)"
- Your app only accesses your own YouTube channel

### Refresh token expired
- Google OAuth tokens for "Testing" apps expire after 7 days
- To fix: Go to Google Cloud Console -> OAuth consent screen -> Publish the app
- Then re-run `python auth_setup.py` to get a new permanent token

---

## Cost Summary

| Service | Cost | Limit |
|---------|------|-------|
| GitHub Actions | FREE | Unlimited for public repos |
| edge-tts | FREE | No limit |
| YouTube Data API | FREE | 10,000 units/day (~6 uploads) |
| Pillow/moviepy/ffmpeg | FREE | Open source |
| **Total** | **$0/month** | |

---

## Future Upgrades (When Ready to Pay)

1. **Better TTS**: Google Cloud TTS ($4/1M chars) or ElevenLabs
2. **AI Content**: Use Gemini API or GPT to generate fresh content
3. **Stock Images**: Pexels API (free) or Shutterstock (paid)
4. **Thumbnails**: Use Canva API or AI-generated thumbnails
5. **Private Repo**: GitHub Pro ($4/month) for private repos

---

## Files Overview

| File | Purpose |
|------|---------|
| `generate_once.py` | Main script for CI/CD (generates 1 video) |
| `auth_setup.py` | Local script to get YouTube tokens |
| `content_generator.py` | Selects Tamil content for videos |
| `content_database.py` | Tamil facts database (10 categories) |
| `tts_generator.py` | Text-to-speech using edge-tts |
| `video_creator.py` | Creates video with Pillow + moviepy |
| `youtube_uploader.py` | Uploads to YouTube |
| `database.py` | SQLite for tracking (local use) |
| `.github/workflows/generate_video.yml` | GitHub Actions schedule |
