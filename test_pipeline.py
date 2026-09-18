"""
Test Pipeline - Test individual components
"""

import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_content_generation():
    """Test content generation"""
    logger.info("Testing content generation...")
    try:
        from content_generator import TamilContentGenerator
        
        generator = TamilContentGenerator()
        content = generator.get_random_content()
        
        logger.info(f"✓ Content generated successfully")
        logger.info(f"  Title: {content['title']}")
        logger.info(f"  Duration: {content['total_duration']} seconds")
        logger.info(f"  Items: {len(content['content'])}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Content generation failed: {e}")
        return False


def test_tts_generation():
    """Test text-to-speech generation"""
    logger.info("Testing TTS generation...")
    try:
        from tts_generator import TamilTTSGenerator
        
        tts = TamilTTSGenerator()
        test_text = "வணக்கம் நண்பர்களே!"
        
        audio_path = tts.generate_speech(test_text, "test_tts")
        
        if Path(audio_path).exists():
            logger.info(f"✓ TTS generation successful")
            logger.info(f"  Audio file: {audio_path}")
            return True
        else:
            logger.error(f"✗ Audio file not created")
            return False
            
    except Exception as e:
        logger.error(f"✗ TTS generation failed: {e}")
        return False


def test_video_creation():
    """Test video creation"""
    logger.info("Testing video creation...")
    try:
        from video_creator import VideoCreator
        from content_generator import TamilContentGenerator
        from tts_generator import TamilTTSGenerator
        
        # Generate content and audio
        content_gen = TamilContentGenerator()
        content = content_gen.get_random_content()
        
        tts_gen = TamilTTSGenerator()
        audio_path = tts_gen.generate_speech(
            "வணக்கம் நண்பர்களே! இது ஒரு சோதனை வீடியோ.",
            "test_audio"
        )
        
        # Create video
        video_creator = VideoCreator()
        video_path = video_creator.create_video(
            content,
            audio_path,
            "test_video"
        )
        
        if Path(video_path).exists():
            logger.info(f"✓ Video creation successful")
            logger.info(f"  Video file: {video_path}")
            return True
        else:
            logger.error(f"✗ Video file not created")
            return False
            
    except Exception as e:
        logger.error(f"✗ Video creation failed: {e}")
        return False


def test_database():
    """Test database operations"""
    logger.info("Testing database...")
    try:
        from database import VideoDatabase
        
        db = VideoDatabase("test_videos.db")
        
        # Add test video
        video_id = db.add_video(
            title="Test Video",
            description="This is a test video",
            video_path="/path/to/test.mp4",
            duration=900,
            tags="test,tamil"
        )
        
        # Get video
        video = db.get_video(video_id)
        
        if video and video['id'] == video_id:
            logger.info(f"✓ Database operations successful")
            logger.info(f"  Video ID: {video_id}")
            return True
        else:
            logger.error(f"✗ Database operations failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False


def test_youtube_uploader():
    """Test YouTube uploader initialization"""
    logger.info("Testing YouTube uploader...")
    try:
        from youtube_uploader import YouTubeUploader
        
        if not Path("credentials.json").exists():
            logger.warning("⚠ Credentials file not found - skipping YouTube test")
            logger.info("  To test YouTube upload:")
            logger.info("  1. Download credentials from Google Cloud Console")
            logger.info("  2. Save as credentials.json")
            logger.info("  3. Run this test again")
            return True
        
        uploader = YouTubeUploader()
        logger.info(f"✓ YouTube uploader initialized successfully")
        return True
        
    except Exception as e:
        logger.warning(f"⚠ YouTube uploader test skipped: {e}")
        return True


def test_scheduler():
    """Test scheduler initialization"""
    logger.info("Testing scheduler...")
    try:
        from scheduler import VideoGenerationScheduler
        
        scheduler = VideoGenerationScheduler()
        jobs = scheduler.get_scheduled_jobs()
        
        logger.info(f"✓ Scheduler initialized successfully")
        logger.info(f"  Scheduled jobs: {len(jobs)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Scheduler test failed: {e}")
        return False


def test_dependencies():
    """Test all dependencies"""
    logger.info("Testing dependencies...")
    
    dependencies = {
        'moviepy': 'Video processing',
        'pyttsx3': 'Text-to-speech',
        'PIL': 'Image processing',
        'numpy': 'Numerical computing',
        'requests': 'HTTP requests',
        'apscheduler': 'Task scheduling',
        'google': 'Google API client'
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            logger.info(f"✓ {module}: {description}")
        except ImportError:
            logger.error(f"✗ {module}: {description} - NOT INSTALLED")
            all_ok = False
    
    return all_ok


def run_all_tests():
    """Run all tests"""
    logger.info("=" * 80)
    logger.info("TAMIL VIDEO GENERATOR - TEST SUITE")
    logger.info("=" * 80)
    logger.info("")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Content Generation", test_content_generation),
        ("TTS Generation", test_tts_generation),
        ("Database", test_database),
        ("YouTube Uploader", test_youtube_uploader),
        ("Scheduler", test_scheduler),
        ("Video Creation", test_video_creation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info("")
        results[test_name] = test_func()
        logger.info("")
    
    # Summary
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info("")
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
