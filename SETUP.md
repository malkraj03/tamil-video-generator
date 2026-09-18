# Quick Setup Guide

## Step 1: Install System Dependencies

### macOS
```bash
brew install ffmpeg imagemagick python@3.10
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg imagemagick python3.10 python3.10-venv
```

### Windows
1. Download FFmpeg: https://ffmpeg.org/download.html
2. Download ImageMagick: https://imagemagick.org/script/download.php
3. Download Python 3.10: https://www.python.org/downloads/

## Step 2: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt
```

## Step 3: YouTube API Setup

### 3.1 Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click "Select a Project" → "New Project"
3. Enter project name: "Tamil Video Generator"
4. Click "Create"

### 3.2 Enable YouTube API
1. Search for "YouTube Data API v3"
2. Click on it
3. Click "Enable"

### 3.3 Create OAuth Credentials
1. Go to "Credentials" in left sidebar
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Desktop application"
4. Download JSON file
5. Rename to `credentials.json`
6. Place in project root directory

### 3.4 Test Authentication
```bash
python main.py --mode generate
```
This will:
- Open a browser for YouTube login
- Ask for permissions
- Save authentication token
- Generate your first test video

## Step 4: Configure Schedule

Edit `config.json`:

```json
{
  "schedule_times": ["08:00", "20:00"],
  "timezone": "Asia/Kolkata"
}
```

Change times to your preferred schedule (24-hour format).

## Step 5: Start the Application

### Option A: Local Run
```bash
python main.py --mode start
```

### Option B: Docker
```bash
docker-compose up -d
```

### Option C: Background Service (Linux/macOS)

Create `~/Library/LaunchAgents/com.tamil.videogenerator.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tamil.videogenerator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/main.py</string>
        <string>--mode</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then run:
```bash
launchctl load ~/Library/LaunchAgents/com.tamil.videogenerator.plist
```

## Step 6: Monitor Progress

Check status:
```bash
python main.py --mode status
```

View recent videos:
```bash
python main.py --mode videos
```

Check logs:
```bash
tail -f video_generator.log
```

## Troubleshooting

### Issue: "FFmpeg not found"
**Solution**: Reinstall FFmpeg
```bash
# macOS
brew reinstall ffmpeg

# Ubuntu
sudo apt-get install --reinstall ffmpeg
```

### Issue: "No module named moviepy"
**Solution**: Reinstall dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Issue: YouTube authentication fails
**Solution**:
1. Delete `token.pickle`
2. Delete `credentials.json`
3. Re-download credentials from Google Cloud Console
4. Run `python main.py --mode generate` again

### Issue: Videos not being generated
**Solution**:
1. Check `video_generator.log`
2. Verify disk space: `df -h`
3. Check internet connection
4. Verify YouTube API is enabled

### Issue: Audio quality is poor
**Solution**:
1. Adjust TTS rate in `tts_generator.py`
2. Try different TTS engines
3. Add background music

## Performance Tips

1. **Faster Generation**
   - Reduce resolution to 720p in config.json
   - Lower FPS to 24
   - Disable background music

2. **Better Quality**
   - Use 4K resolution (3840x2160)
   - Increase FPS to 60
   - Add background music

3. **Optimize Storage**
   - Run cleanup: `python main.py --mode cleanup --days 30`
   - Move old videos to external storage
   - Compress videos after upload

## Next Steps

1. ✅ Test with `python main.py --mode generate`
2. ✅ Verify video uploads to YouTube
3. ✅ Adjust schedule times in config.json
4. ✅ Start scheduler: `python main.py --mode start`
5. ✅ Monitor logs regularly
6. ✅ Add more content to database as needed

## Getting Help

1. Check `video_generator.log` for detailed errors
2. Review README.md for more information
3. Check YouTube API documentation
4. Verify FFmpeg installation

## Security Notes

⚠️ **Important**:
- Keep `credentials.json` secure
- Don't commit credentials to git
- Use environment variables for sensitive data
- Regularly rotate API tokens
- Monitor API usage in Google Cloud Console

---

**You're all set! Your automated Tamil video generator is ready to go! 🎉**
