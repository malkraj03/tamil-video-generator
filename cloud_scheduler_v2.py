"""
Cloud Scheduler V2 - Uses Expanded Content Database
Optimized for diverse, engaging content with budget constraints
"""

import os
import json
import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from content_database import ExpandedContentDatabase
from cloud_tts import CloudTTSGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from cloud_storage import CloudStorageManager
from database import VideoDatabase

logger = logging.getLogger(__name__)


class BudgetOptimizedVideoGenerator:
    """Generate videos with diverse content on budget"""
    
    def __init__(self, config: Dict):
        """
        Initialize Budget-Optimized Video Generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.project_id = config.get('gcp_project_id')
        self.bucket_name = config.get('gcp_bucket_name')
        self.credentials_path = config.get('gcp_credentials_path')
        
        # Initialize components
        self.content_database = ExpandedContentDatabase()
        self.tts_generator = CloudTTSGenerator(
            project_id=self.project_id,
            credentials_path=self.credentials_path
        )
        self.video_creator = VideoCreator(
            output_dir=tempfile.gettempdir(),
            resolution=self._parse_resolution(config.get('video_resolution', '1920x1080')),
            fps=config.get('video_fps', 30)
        )
        
        # Cloud storage
        self.storage_manager = CloudStorageManager(
            project_id=self.project_id,
            bucket_name=self.bucket_name,
            credentials_path=self.credentials_path
        )
        
        # YouTube uploader
        self.youtube_uploader = None
        if os.path.exists(config.get('youtube_credentials', 'credentials.json')):
            try:
                self.youtube_uploader = YouTubeUploader(
                    credentials_file=config['youtube_credentials']
                )
            except Exception as e:
                logger.warning(f"YouTube uploader not available: {e}")
        
        # Database
        self.db = VideoDatabase(config.get('database_path', 'videos.db'))
        
        logger.info("Budget-Optimized Video Generator initialized")
    
    def _parse_resolution(self, resolution_str: str) -> tuple:
        """Parse resolution string to tuple"""
        try:
            width, height = map(int, resolution_str.split('x'))
            return (width, height)
        except:
            return (1920, 1080)
    
    def generate_and_publish(self) -> Dict:
        """
        Generate and publish video with diverse content
        
        Returns:
            Result dictionary with status and details
        """
        temp_dir = None
        try:
            # Create temporary directory for processing
            temp_dir = tempfile.mkdtemp(prefix="tamil_video_")
            logger.info(f"Using temp directory: {temp_dir}")
            
            # Step 1: Generate diverse content
            logger.info("Step 1: Generating diverse content...")
            content = self.content_database.get_random_diverse_content(
                duration_target=self.config.get('video_duration_max', 20) * 60
            )
            logger.info(f"Content generated: {content['title']}")
            logger.info(f"Category: {content['category']}")
            logger.info(f"Difficulty: {content['difficulty']}")
            
            # Step 2: Generate audio
            logger.info("Step 2: Generating Tamil speech audio...")
            audio_filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            audio_path = self.tts_generator.generate_script_audio(
                content['script'],
                audio_filename,
                voice_name=self.config.get('tts_voice', 'ta-IN-Standard-A'),
                speaking_rate=self.config.get('tts_speaking_rate', 1.0)
            )
            
            if not audio_path:
                logger.error("Failed to generate audio")
                return {
                    'success': False,
                    'error': 'Audio generation failed'
                }
            
            logger.info(f"Audio generated: {audio_path}")
            
            # Step 3: Create video
            logger.info("Step 3: Creating video...")
            video_title = content['title'].replace(' ', '_')[:50]
            video_path = self.video_creator.create_video(
                content,
                audio_path,
                video_title
            )
            
            if not video_path or not os.path.exists(video_path):
                logger.error("Failed to create video")
                return {
                    'success': False,
                    'error': 'Video creation failed'
                }
            
            logger.info(f"Video created: {video_path}")
            
            # Step 4: Upload to Cloud Storage
            logger.info("Step 4: Uploading to Cloud Storage...")
            video_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            video_remote_path = self.storage_manager.upload_video(video_path, video_id)
            audio_remote_path = self.storage_manager.upload_audio(audio_path, video_id)
            
            if not video_remote_path:
                logger.error("Failed to upload video to Cloud Storage")
                return {
                    'success': False,
                    'error': 'Cloud Storage upload failed'
                }
            
            logger.info(f"Uploaded to Cloud Storage: {video_remote_path}")
            
            # Step 5: Publish to YouTube
            youtube_video_id = None
            if self.youtube_uploader:
                logger.info("Step 5: Publishing to YouTube...")
                youtube_video_id = self.youtube_uploader.upload_video(
                    video_path=video_path,
                    title=content['title'],
                    description=content['description'],
                    tags=content['tags'],
                    category_id='27',
                    privacy_status='public'
                )
                
                if youtube_video_id:
                    logger.info(f"Video published: {youtube_video_id}")
                else:
                    logger.warning("YouTube upload failed")
            else:
                logger.info("Step 5: Skipping YouTube upload (credentials not available)")
            
            # Step 6: Save to database
            logger.info("Step 6: Saving to database...")
            db_id = self.db.add_video(
                title=content['title'],
                description=content['description'],
                video_path=video_remote_path,
                audio_path=audio_remote_path,
                video_id=youtube_video_id,
                duration=content['total_duration'],
                tags=','.join(content['tags'])
            )
            
            logger.info(f"Video record saved: ID {db_id}")
            
            # Step 7: Cleanup local files
            logger.info("Step 7: Cleaning up local files...")
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                logger.info("Local files cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up local files: {e}")
            
            logger.info("=" * 80)
            logger.info("Video generation pipeline completed successfully!")
            logger.info(f"Category: {content['category']}")
            logger.info(f"Difficulty: {content['difficulty']}")
            logger.info("=" * 80)
            
            return {
                'success': True,
                'video_id': youtube_video_id,
                'cloud_path': video_remote_path,
                'title': content['title'],
                'category': content['category'],
                'difficulty': content['difficulty'],
                'db_id': db_id
            }
        
        except Exception as e:
            logger.error(f"Error in video generation pipeline: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
        
        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Error cleaning temp directory: {e}")
    
    def cleanup_old_files(self, days: int = 7) -> Dict:
        """
        Clean up old files from Cloud Storage
        Budget-optimized: 7-day retention
        
        Args:
            days: Delete files older than this many days
            
        Returns:
            Cleanup statistics
        """
        try:
            logger.info(f"Cleaning up files older than {days} days...")
            
            deleted_videos = self.storage_manager.cleanup_old_files(
                days=days,
                prefix='videos/'
            )
            
            deleted_audio = self.storage_manager.cleanup_old_files(
                days=days,
                prefix='audio/'
            )
            
            deleted_images = self.storage_manager.cleanup_old_files(
                days=days,
                prefix='images/'
            )
            
            total_deleted = deleted_videos + deleted_audio + deleted_images
            
            logger.info(f"Cleanup completed: {total_deleted} files deleted")
            
            return {
                'success': True,
                'deleted_videos': deleted_videos,
                'deleted_audio': deleted_audio,
                'deleted_images': deleted_images,
                'total_deleted': total_deleted
            }
        
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_content_stats(self) -> Dict:
        """Get content database statistics"""
        try:
            categories = self.content_database.get_all_categories()
            content_count = self.content_database.get_content_count()
            
            return {
                'success': True,
                'categories': categories,
                'content_count': content_count,
                'total_content': sum(content_count.values())
            }
        except Exception as e:
            logger.error(f"Error getting content stats: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_bucket_stats(self) -> Dict:
        """Get Cloud Storage bucket statistics"""
        try:
            stats = self.storage_manager.get_bucket_stats()
            logger.info(f"Bucket stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error getting bucket stats: {e}")
            return {}


def cloud_run_handler(request):
    """
    Cloud Run HTTP handler
    Triggered by Cloud Scheduler via HTTP request
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response
    """
    try:
        # Load configuration
        config = {
            'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
            'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME'),
            'gcp_credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'youtube_credentials': os.getenv('YOUTUBE_CREDENTIALS', 'credentials.json'),
            'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
            'video_fps': int(os.getenv('VIDEO_FPS', '30')),
            'video_duration_max': int(os.getenv('VIDEO_DURATION_MAX', '20')),
            'tts_voice': os.getenv('TTS_VOICE', 'ta-IN-Standard-A'),
            'tts_speaking_rate': float(os.getenv('TTS_SPEAKING_RATE', '1.0')),
            'database_path': os.getenv('DATABASE_PATH', '/tmp/videos.db')
        }
        
        # Validate required config
        if not config['gcp_project_id'] or not config['gcp_bucket_name']:
            return {
                'success': False,
                'error': 'Missing GCP configuration'
            }, 400
        
        # Generate video
        generator = BudgetOptimizedVideoGenerator(config)
        result = generator.generate_and_publish()
        
        return result, 200 if result['success'] else 500
    
    except Exception as e:
        logger.error(f"Cloud Run handler error: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }, 500


def cleanup_handler(request):
    """
    Cloud Run HTTP handler for cleanup
    Triggered by Cloud Scheduler
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response
    """
    try:
        config = {
            'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
            'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME'),
            'gcp_credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            'youtube_credentials': os.getenv('YOUTUBE_CREDENTIALS', 'credentials.json'),
            'video_resolution': os.getenv('VIDEO_RESOLUTION', '1920x1080'),
            'video_fps': int(os.getenv('VIDEO_FPS', '30')),
            'video_duration_max': int(os.getenv('VIDEO_DURATION_MAX', '20')),
            'database_path': os.getenv('DATABASE_PATH', '/tmp/videos.db')
        }
        
        generator = BudgetOptimizedVideoGenerator(config)
        result = generator.cleanup_old_files(days=7)  # 7-day retention for budget
        
        return result, 200 if result['success'] else 500
    
    except Exception as e:
        logger.error(f"Cleanup handler error: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }, 500


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test configuration
    config = {
        'gcp_project_id': os.getenv('GCP_PROJECT_ID'),
        'gcp_bucket_name': os.getenv('GCP_BUCKET_NAME'),
        'gcp_credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'youtube_credentials': 'credentials.json',
        'video_resolution': '1920x1080',
        'video_fps': 30,
        'video_duration_max': 20,
        'tts_voice': 'ta-IN-Standard-A',
        'tts_speaking_rate': 1.0,
        'database_path': 'videos.db'
    }
    
    generator = BudgetOptimizedVideoGenerator(config)
    
    # Get content stats
    stats = generator.get_content_stats()
    print(f"Content Stats: {json.dumps(stats, indent=2)}")
    
    # Generate video
    result = generator.generate_and_publish()
    print(f"Generation Result: {json.dumps(result, indent=2)}")
