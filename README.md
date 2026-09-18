# Tamil Video Generator - Automated YouTube Video Creation

A fully automated system to generate and publish Tamil history and fun facts videos to YouTube daily (twice per day). Videos are 15-20 minutes long with mixed styles including slideshows, documentary footage, and animations.

## Features

✅ **Automated Content Generation**
- Tamil history and fun facts database
- Intelligent content selection for target duration
- Automatic script generation

✅ **Audio Generation**
- Tamil text-to-speech (TTS) narration
- Multiple sentence processing for better quality
- Background music support

✅ **Video Creation**
- Mixed video styles (slideshow, documentary, animation)
- Free stock images from Unsplash
- Professional transitions and effects
- 1080p resolution at 30fps

✅ **YouTube Integration**
- Automated video upload
- Metadata and tags management
- Scheduled publishing
- Playlist management

✅ **Scheduling & Automation**
- Twice-daily video generation (configurable times)
- Background scheduler
- Error handling and retries

✅ **Database & Tracking**
- SQLite database for video metadata
- Publishing history
- Statistics tracking
- File cleanup

## System Requirements

- Python 3.10+
- FFmpeg
- ImageMagick
- 4GB RAM minimum
- 50GB disk space (for videos)
- Internet connection

## Installation

### Option 1: Local Installation

1. **Clone/Download the project**
```bash
cd tamil_video_generator
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install system dependencies**

**macOS:**
```bash
brew install ffmpeg imagemagick
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg imagemagick libsm6 libxext6 libxrender-dev
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Download ImageMagick from https://imagemagick.org/script/download.php

### Option 2: Docker Installation

```bash
docker-compose up -d
```

## YouTube Setup

### 1. Create YouTube Channel
- Go to https://www.youtube.com
- Create a new channel (if you don't have one)
- Verify your account

### 2. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials as JSON
6. Save as `credentials.json` in project root

### 3. First Run Authentication
```bash
python main.py --mode generate
```
This will open a browser for YouTube authentication. Grant permissions and you're set!

## Configuration

Edit `config.json` to customize:

```json
{
  "audio_dir": "audio_output",
  "video_dir": "videos",
  "video_resolution": "1920x1080",
  "video_fps": 30,
  "video_duration_min": 15,
  "video_duration_max": 20,
  "schedule_times": ["08:00", "20:00"],
  "timezone": "Asia/Kolkata"
}
```

## Usage

### Start Scheduled Generation (Twice Daily)
```bash
python main.py --mode start
```

### Generate Video Immediately (Testing)
```bash
python main.py --mode generate
```

### View Status
```bash
python main.py --mode status
```

### View Recent Videos
```bash
python main.py --mode videos --limit 10
```

### Clean Up Old Files
```bash
python main.py --mode cleanup --days 30
```

## Project Structure

```
tamil_video_generator/
├── main.py                 # Main application entry point
├── scheduler.py            # Video generation scheduler
├── content_generator.py    # Tamil content generation
├── tts_generator.py        # Text-to-speech for Tamil
├── video_creator.py        # Video creation pipeline
├── youtube_uploader.py     # YouTube API integration
├── database.py             # SQLite database management
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── audio_output/           # Generated audio files
├── videos/                 # Generated videos
└── videos.db              # SQLite database
```

## How It Works

### Daily Pipeline (Runs Twice)

1. **Content Generation** (5 min)
   - Selects random Tamil facts/history
   - Creates script with proper duration
   - Generates metadata and tags

2. **Audio Generation** (10-15 min)
   - Converts Tamil script to speech
   - Processes sentence by sentence
   - Combines with background music

3. **Video Creation** (20-30 min)
   - Creates mixed-style video clips
   - Fetches stock images from Unsplash
   - Adds text overlays and transitions
   - Syncs audio with video

4. **YouTube Publishing** (5-10 min)
   - Uploads to YouTube
   - Sets metadata and tags
   - Publishes to channel

5. **Database Update**
   - Records video metadata
   - Tracks publishing history
   - Stores statistics

**Total Time: ~50-70 minutes per video**

## Content Database

The system includes a database of 20+ Tamil history and culture facts:
- Ancient kingdoms (Chola, Pandya, Chera, Pallava)
- Tamil literature (Sangam, Silappatikaram, Manimakalai)
- Tamil arts and culture
- Tamil science and mathematics
- Tamil festivals and traditions

You can easily add more facts by editing `content_generator.py`.

## Free Resources Used

✅ **Text-to-Speech**: pyttsx3 (offline, free)
✅ **Stock Images**: Unsplash API (free, no attribution required)
✅ **Video Processing**: FFmpeg (free, open-source)
✅ **Image Processing**: Pillow, ImageMagick (free, open-source)
✅ **Database**: SQLite (free, built-in)
✅ **Scheduling**: APScheduler (free, open-source)

## Troubleshooting

### FFmpeg not found
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg
```

### YouTube authentication fails
- Delete `token.pickle` file
- Run `python main.py --mode generate` again
- Grant permissions in browser

### Videos not generating
- Check `video_generator.log` for errors
- Ensure sufficient disk space
- Verify internet connection

### Audio quality issues
- Adjust `rate` in `tts_generator.py` (default: 150)
- Try different TTS engines
- Add background music for better quality

## Performance Optimization

For faster video generation:
- Reduce video resolution to 720p
- Lower FPS to 24
- Use smaller stock images
- Disable background music

## Scaling & Deployment

### AWS Deployment
1. Create EC2 instance (t3.medium or larger)
2. Install dependencies
3. Set up cron job for scheduling
4. Use S3 for video storage

### Google Cloud Deployment
1. Create Compute Engine instance
2. Use Cloud Scheduler for cron jobs
3. Store videos in Cloud Storage

### DigitalOcean Deployment
1. Create Droplet (2GB RAM minimum)
2. Install Docker
3. Deploy with docker-compose

## Future Enhancements

- [ ] Support for multiple languages
- [ ] AI-powered content generation
- [ ] Advanced video effects and animations
- [ ] Real-time statistics dashboard
- [ ] Thumbnail generation with AI
- [ ] Multi-channel publishing
- [ ] Comment moderation
- [ ] Analytics integration

## License

This project is provided as-is for educational and personal use.

## Support

For issues and questions:
1. Check `video_generator.log` for error details
2. Review the troubleshooting section
3. Check YouTube API documentation
4. Verify FFmpeg installation

## Contributing

Feel free to:
- Add more Tamil facts to the database
- Improve video styles and effects
- Optimize performance
- Add new features

## Disclaimer

- Ensure you have rights to publish content
- Follow YouTube's community guidelines
- Respect copyright for images and music
- Use authentic Tamil language
- Verify historical facts before publishing

---

**Created with ❤️ for Tamil content creators**

Happy video generation! 🎬📹
