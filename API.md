# API Documentation

## Overview

This document describes the Python API for the Tamil Video Generator system. You can use these classes and methods to integrate the video generation pipeline into your own applications.

## Table of Contents

1. [Content Generator](#content-generator)
2. [TTS Generator](#tts-generator)
3. [Video Creator](#video-creator)
4. [YouTube Uploader](#youtube-uploader)
5. [Database](#database)
6. [Scheduler](#scheduler)

---

## Content Generator

### Class: `TamilContentGenerator`

Generates Tamil history and fun facts content.

#### Methods

##### `get_random_content(duration_target=900)`

Generate random content that fits the target duration.

**Parameters:**
- `duration_target` (int): Target duration in seconds (default: 900 = 15 mins)

**Returns:**
```python
{
    'title': str,              # Video title
    'description': str,        # YouTube description
    'script': str,            # Complete narration script
    'content': List[Dict],    # List of content items
    'total_duration': int,    # Total duration in seconds
    'estimated_video_duration': int,  # With intro/outro
    'tags': List[str],        # YouTube tags
    'category': str           # Content category
}
```

**Example:**
```python
from content_generator import TamilContentGenerator

generator = TamilContentGenerator()
content = generator.get_random_content(duration_target=1200)
print(content['title'])
print(content['script'])
```

---

## TTS Generator

### Class: `TamilTTSGenerator`

Generates Tamil speech from text using text-to-speech.

#### Constructor

```python
TamilTTSGenerator(output_dir='audio_output')
```

**Parameters:**
- `output_dir` (str): Directory to save audio files

#### Methods

##### `generate_speech(text, filename)`

Generate speech from Tamil text.

**Parameters:**
- `text` (str): Tamil text to convert
- `filename` (str): Output filename (without extension)

**Returns:**
- `str`: Path to generated audio file

**Example:**
```python
from tts_generator import TamilTTSGenerator

tts = TamilTTSGenerator()
audio_path = tts.generate_speech("வணக்கம்!", "greeting")
print(f"Audio saved to: {audio_path}")
```

##### `generate_script_audio(script, filename)`

Generate audio from complete script.

**Parameters:**
- `script` (str): Complete Tamil script
- `filename` (str): Output filename

**Returns:**
- `str`: Path to combined audio file

**Example:**
```python
script = "வணக்கம்! இது ஒரு சோதனை. நன்றி!"
audio_path = tts.generate_script_audio(script, "complete_script")
```

##### `add_background_music(speech_audio, music_audio, output_filename, music_volume=0.3)`

Add background music to speech.

**Parameters:**
- `speech_audio` (str): Path to speech audio
- `music_audio` (str): Path to background music
- `output_filename` (str): Output filename
- `music_volume` (float): Volume of music (0.0-1.0)

**Returns:**
- `str`: Path to combined audio

---

## Video Creator

### Class: `VideoCreator`

Creates videos with mixed styles.

#### Constructor

```python
VideoCreator(output_dir='videos', resolution=(1920, 1080), fps=30)
```

**Parameters:**
- `output_dir` (str): Directory to save videos
- `resolution` (tuple): Video resolution (width, height)
- `fps` (int): Frames per second

#### Methods

##### `create_video(content, audio_path, title)`

Create complete video from content and audio.

**Parameters:**
- `content` (dict): Content dictionary from ContentGenerator
- `audio_path` (str): Path to audio file
- `title` (str): Video title

**Returns:**
- `str`: Path to created video file

**Example:**
```python
from video_creator import VideoCreator
from content_generator import TamilContentGenerator
from tts_generator import TamilTTSGenerator

# Generate content
content_gen = TamilContentGenerator()
content = content_gen.get_random_content()

# Generate audio
tts_gen = TamilTTSGenerator()
audio_path = tts_gen.generate_script_audio(content['script'], "audio")

# Create video
video_creator = VideoCreator(resolution=(1920, 1080), fps=30)
video_path = video_creator.create_video(content, audio_path, "my_video")
print(f"Video created: {video_path}")
```

---

## YouTube Uploader

### Class: `YouTubeUploader`

Upload and manage videos on YouTube.

#### Constructor

```python
YouTubeUploader(credentials_file='credentials.json', token_file='token.pickle')
```

**Parameters:**
- `credentials_file` (str): Path to OAuth credentials JSON
- `token_file` (str): Path to save authentication token

#### Methods

##### `upload_video(video_path, title, description, tags, category_id='27', privacy_status='public', schedule_time=None)`

Upload video to YouTube.

**Parameters:**
- `video_path` (str): Path to video file
- `title` (str): Video title
- `description` (str): Video description
- `tags` (list): List of tags
- `category_id` (str): YouTube category ID (27=Education)
- `privacy_status` (str): 'public', 'private', or 'unlisted'
- `schedule_time` (str): ISO 8601 format for scheduled publishing

**Returns:**
- `str`: YouTube video ID if successful, None otherwise

**Example:**
```python
from youtube_uploader import YouTubeUploader

uploader = YouTubeUploader()
video_id = uploader.upload_video(
    video_path='videos/my_video.mp4',
    title='Tamil History',
    description='Learn about Tamil history',
    tags=['tamil', 'history', 'education'],
    category_id='27'
)
print(f"Video uploaded: {video_id}")
```

##### `set_thumbnail(video_id, thumbnail_path)`

Set custom thumbnail for video.

**Parameters:**
- `video_id` (str): YouTube video ID
- `thumbnail_path` (str): Path to thumbnail image

**Returns:**
- `bool`: True if successful

##### `get_video_status(video_id)`

Get video status and details.

**Parameters:**
- `video_id` (str): YouTube video ID

**Returns:**
- `dict`: Video details or None

##### `create_playlist(title, description='')`

Create a new playlist.

**Parameters:**
- `title` (str): Playlist title
- `description` (str): Playlist description

**Returns:**
- `str`: Playlist ID

##### `add_video_to_playlist(playlist_id, video_id)`

Add video to playlist.

**Parameters:**
- `playlist_id` (str): Playlist ID
- `video_id` (str): Video ID

**Returns:**
- `bool`: True if successful

---

## Database

### Class: `VideoDatabase`

SQLite database for video metadata.

#### Constructor

```python
VideoDatabase(db_path='videos.db')
```

**Parameters:**
- `db_path` (str): Path to SQLite database file

#### Methods

##### `add_video(title, description, video_path, audio_path=None, video_id=None, duration=None, tags=None)`

Add a new video record.

**Parameters:**
- `title` (str): Video title
- `description` (str): Video description
- `video_path` (str): Path to video file
- `audio_path` (str): Path to audio file
- `video_id` (str): YouTube video ID
- `duration` (int): Duration in seconds
- `tags` (str): Comma-separated tags

**Returns:**
- `int`: Database ID of added video

**Example:**
```python
from database import VideoDatabase

db = VideoDatabase()
video_id = db.add_video(
    title='Tamil History',
    description='Learn about Tamil history',
    video_path='videos/tamil_history.mp4',
    duration=900,
    tags='tamil,history,education'
)
```

##### `update_video_status(video_id, status, youtube_video_id=None)`

Update video status.

**Parameters:**
- `video_id` (int): Database video ID
- `status` (str): New status ('created', 'published', 'failed')
- `youtube_video_id` (str): YouTube video ID

##### `get_video(video_id)`

Get video details.

**Parameters:**
- `video_id` (int): Database video ID

**Returns:**
- `dict`: Video details or None

##### `get_all_videos(limit=100, offset=0)`

Get all videos with pagination.

**Parameters:**
- `limit` (int): Number of videos to return
- `offset` (int): Offset for pagination

**Returns:**
- `list`: List of video dictionaries

##### `get_videos_by_status(status)`

Get videos by status.

**Parameters:**
- `status` (str): Video status

**Returns:**
- `list`: List of matching videos

##### `add_statistics(video_id, views=0, likes=0, comments=0, shares=0, watch_time=0)`

Add statistics record.

##### `get_statistics(video_id)`

Get statistics for a video.

**Returns:**
- `list`: List of statistics records

##### `cleanup_old_files(days=30)`

Clean up old video and audio files.

**Parameters:**
- `days` (int): Delete files older than this many days

---

## Scheduler

### Class: `VideoGenerationScheduler`

Orchestrates video generation and publishing.

#### Constructor

```python
VideoGenerationScheduler(config_file='config.json')
```

**Parameters:**
- `config_file` (str): Path to configuration file

#### Methods

##### `start()`

Start the scheduler with configured schedule times.

**Example:**
```python
from scheduler import VideoGenerationScheduler

scheduler = VideoGenerationScheduler()
scheduler.start()  # Runs indefinitely
```

##### `stop()`

Stop the scheduler.

##### `generate_and_publish_video()`

Manually trigger video generation and publishing.

**Returns:**
```python
{
    'success': bool,
    'video_id': str,      # YouTube video ID
    'video_path': str,    # Path to video file
    'title': str,         # Video title
    'error': str          # Error message if failed
}
```

**Example:**
```python
result = scheduler.generate_and_publish_video()
if result['success']:
    print(f"Video published: {result['video_id']}")
else:
    print(f"Error: {result['error']}")
```

##### `generate_video_manual()`

Manually trigger video generation (alias for above).

##### `get_scheduled_jobs()`

Get list of scheduled jobs.

**Returns:**
```python
[
    {
        'id': str,
        'name': str,
        'next_run_time': str
    }
]
```

---

## Complete Example

Here's a complete example using all components:

```python
from content_generator import TamilContentGenerator
from tts_generator import TamilTTSGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from database import VideoDatabase

# Step 1: Generate content
print("Generating content...")
content_gen = TamilContentGenerator()
content = content_gen.get_random_content(duration_target=1200)
print(f"Title: {content['title']}")

# Step 2: Generate audio
print("Generating audio...")
tts_gen = TamilTTSGenerator()
audio_path = tts_gen.generate_script_audio(content['script'], "my_audio")
print(f"Audio: {audio_path}")

# Step 3: Create video
print("Creating video...")
video_creator = VideoCreator()
video_path = video_creator.create_video(content, audio_path, "my_video")
print(f"Video: {video_path}")

# Step 4: Upload to YouTube
print("Uploading to YouTube...")
uploader = YouTubeUploader()
video_id = uploader.upload_video(
    video_path=video_path,
    title=content['title'],
    description=content['description'],
    tags=content['tags']
)
print(f"YouTube ID: {video_id}")

# Step 5: Save to database
print("Saving to database...")
db = VideoDatabase()
db_id = db.add_video(
    title=content['title'],
    description=content['description'],
    video_path=video_path,
    audio_path=audio_path,
    video_id=video_id,
    duration=content['total_duration'],
    tags=','.join(content['tags'])
)
print(f"Database ID: {db_id}")

print("Done!")
```

---

## Error Handling

All methods may raise exceptions. Always use try-except blocks:

```python
try:
    video_id = uploader.upload_video(...)
except Exception as e:
    print(f"Error: {e}")
    # Handle error
```

---

## Configuration

Configure behavior via `config.json`:

```json
{
  "video_resolution": "1920x1080",
  "video_fps": 30,
  "video_duration_min": 15,
  "video_duration_max": 20,
  "schedule_times": ["08:00", "20:00"],
  "timezone": "Asia/Kolkata"
}
```

---

## Logging

Enable logging to see detailed information:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Performance Tips

1. **Reuse objects**: Create scheduler/uploader once, reuse multiple times
2. **Batch operations**: Process multiple videos together
3. **Cache content**: Store generated content for reuse
4. **Async operations**: Use threading for parallel processing

---

## Support

For issues and questions, check the README.md and SETUP.md files.
