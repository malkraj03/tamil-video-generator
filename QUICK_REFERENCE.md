# Quick Reference Guide

## Installation (5 minutes)

```bash
# 1. Setup Python environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install system tools
brew install ffmpeg imagemagick  # macOS
# OR
sudo apt-get install ffmpeg imagemagick  # Ubuntu

# 4. Get YouTube credentials
# - Go to Google Cloud Console
# - Create project, enable YouTube API v3
# - Create OAuth credentials (Desktop app)
# - Download JSON as credentials.json
```

## First Run (10 minutes)

```bash
# Test the system
python test_pipeline.py

# Generate first video (will authenticate with YouTube)
python main.py --mode generate

# Check if video was created
python main.py --mode videos
```

## Daily Operation

```bash
# Start automatic scheduling (runs twice daily)
python main.py --mode start

# Check status anytime
python main.py --mode status

# View recent videos
python main.py --mode videos --limit 5

# Clean old files
python main.py --mode cleanup --days 30
```

## Configuration

Edit `config.json`:

```json
{
  "schedule_times": ["08:00", "20:00"],  // Change daily times
  "video_resolution": "1920x1080",       // 720p or 4K
  "video_fps": 30,                       // 24 or 60
  "video_duration_min": 15,              // Minimum minutes
  "video_duration_max": 20               // Maximum minutes
}
```

## Docker (Single Command)

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| FFmpeg not found | `brew install ffmpeg` |
| YouTube auth fails | Delete `token.pickle`, re-run |
| Videos not generating | Check `video_generator.log` |
| Poor audio quality | Adjust TTS rate in `tts_generator.py` |
| Disk space issues | Run `python main.py --mode cleanup` |

## File Locations

| File | Purpose |
|------|---------|
| `config.json` | Configuration |
| `credentials.json` | YouTube API credentials |
| `token.pickle` | YouTube auth token |
| `videos.db` | Video database |
| `video_generator.log` | Error logs |
| `audio_output/` | Generated audio files |
| `videos/` | Generated video files |

## Command Reference

```bash
# Generate video now
python main.py --mode generate

# Start scheduler
python main.py --mode start

# Show status
python main.py --mode status

# List videos
python main.py --mode videos --limit 10

# Clean old files
python main.py --mode cleanup --days 30

# Run tests
python test_pipeline.py
```

## Python API Quick Start

```python
# Generate content
from content_generator import TamilContentGenerator
gen = TamilContentGenerator()
content = gen.get_random_content()

# Generate audio
from tts_generator import TamilTTSGenerator
tts = TamilTTSGenerator()
audio = tts.generate_script_audio(content['script'], "audio")

# Create video
from video_creator import VideoCreator
creator = VideoCreator()
video = creator.create_video(content, audio, "video")

# Upload to YouTube
from youtube_uploader import YouTubeUploader
uploader = YouTubeUploader()
video_id = uploader.upload_video(video, content['title'], 
                                 content['description'], 
                                 content['tags'])
```

## Performance Tips

**Faster Generation:**
- Reduce resolution to 720p
- Lower FPS to 24
- Disable background music

**Better Quality:**
- Use 4K resolution
- Increase FPS to 60
- Add background music

**Lower Disk Usage:**
- Clean up old files regularly
- Move videos to external storage
- Compress after upload

## Monitoring

```bash
# Watch logs in real-time
tail -f video_generator.log

# Check disk usage
du -sh videos/ audio_output/

# Monitor system resources
top  # or Activity Monitor on macOS

# Check YouTube uploads
python main.py --mode videos
```

## Adding More Content

Edit `content_generator.py`:

```python
def _initialize_facts(self):
    return [
        # ... existing facts ...
        {
            "title": "Your Tamil Title",
            "content": "Your Tamil content here",
            "duration": 45,
            "category": "history"
        }
    ]
```

## Scheduling

Default: 8:00 AM and 8:00 PM (Asia/Kolkata timezone)

Change in `config.json`:
```json
"schedule_times": ["06:00", "18:00"]  // 6 AM and 6 PM
```

## YouTube Channel Setup

1. Create channel at youtube.com
2. Verify account
3. Get API credentials from Google Cloud Console
4. Save as `credentials.json`
5. Run `python main.py --mode generate`
6. Grant permissions in browser

## Deployment

**Local:**
```bash
python main.py --mode start
```

**Docker:**
```bash
docker-compose up -d
```

**Background (macOS):**
```bash
nohup python main.py --mode start > output.log 2>&1 &
```

**Background (Linux):**
```bash
screen -S video-gen
python main.py --mode start
# Press Ctrl+A then D to detach
```

## Database Queries

```python
from database import VideoDatabase

db = VideoDatabase()

# Get total videos
total = db.get_total_videos()

# Get published videos
published = db.get_published_videos()

# Get all videos
videos = db.get_all_videos(limit=10)

# Get video by ID
video = db.get_video(1)

# Get statistics
stats = db.get_statistics(1)
```

## Environment Variables

```bash
export LOG_LEVEL=DEBUG
export PYTHONUNBUFFERED=1
python main.py --mode start
```

## Common Issues

**Issue: "No module named moviepy"**
```bash
pip install --upgrade -r requirements.txt
```

**Issue: "YouTube authentication failed"**
```bash
rm token.pickle
python main.py --mode generate
```

**Issue: "Video file not found"**
- Check `video_generator.log`
- Verify disk space
- Check permissions

## Performance Metrics

| Task | Time | Resources |
|------|------|-----------|
| Content generation | 5 min | Low |
| Audio generation | 10-15 min | Medium |
| Video creation | 20-30 min | High |
| YouTube upload | 5-10 min | Medium |
| **Total** | **50-70 min** | **Medium** |

## Useful Links

- [YouTube API Docs](https://developers.google.com/youtube)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [MoviePy Docs](https://zulko.github.io/moviepy/)
- [Google Cloud Console](https://console.cloud.google.com/)

## Emergency Stop

```bash
# Stop scheduler
Ctrl+C

# Kill background process
pkill -f "python main.py"

# Stop Docker
docker-compose down
```

## Backup

```bash
# Backup database
cp videos.db videos.db.backup

# Backup videos
tar -czf videos_backup.tar.gz videos/

# Backup audio
tar -czf audio_backup.tar.gz audio_output/
```

## Reset

```bash
# Clear all generated files
rm -rf videos/ audio_output/
rm videos.db

# Keep credentials and config
# Restart scheduler
python main.py --mode start
```

---

**For detailed information, see README.md, SETUP.md, and API.md**
