"""
Scheduler - Orchestrates the entire video generation and publishing pipeline
Runs twice daily at specified times
"""

import os
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

from content_generator import TamilContentGenerator
from tts_generator import TamilTTSGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from database import VideoDatabase

logger = logging.getLogger(__name__)


class VideoGenerationScheduler:
    """Orchestrates video generation and publishing"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self._load_config(config_file)
        self.scheduler = BackgroundScheduler()
        
        # Initialize components
        self.content_generator = TamilContentGenerator()
        self.tts_generator = TamilTTSGenerator(output_dir=self.config['audio_dir'])
        self.video_creator = VideoCreator(
            output_dir=self.config['video_dir'],
            resolution=self._parse_resolution(self.config['video_resolution']),
            fps=self.config['video_fps']
        )
        
        # YouTube uploader (optional if credentials available)
        self.youtube_uploader = None
        if os.path.exists(self.config.get('youtube_credentials', 'credentials.json')):
            try:
                self.youtube_uploader = YouTubeUploader(
                    credentials_file=self.config['youtube_credentials']
                )
            except Exception as e:
                logger.warning(f"YouTube uploader not available: {e}")
        
        # Database
        self.db = VideoDatabase(self.config['database_path'])
        
        # Create output directories
        self._create_directories()
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")
        
        # Default configuration
        return {
            'audio_dir': 'audio_output',
            'video_dir': 'videos',
            'database_path': 'videos.db',
            'youtube_credentials': 'credentials.json',
            'video_resolution': '1920x1080',
            'video_fps': 30,
            'video_duration_min': 15,
            'video_duration_max': 20,
            'schedule_times': ['08:00', '20:00'],
            'timezone': 'Asia/Kolkata'
        }
    
    def _parse_resolution(self, resolution_str: str) -> tuple:
        """Parse resolution string to tuple"""
        try:
            width, height = map(int, resolution_str.split('x'))
            return (width, height)
        except:
            return (1920, 1080)
    
    def _create_directories(self):
        """Create necessary directories"""
        for directory in [self.config['audio_dir'], self.config['video_dir']]:
            Path(directory).mkdir(exist_ok=True)
    
    def start(self):
        """Start the scheduler"""
        try:
            logger.info("Starting video generation scheduler")
            
            # Schedule jobs
            for schedule_time in self.config['schedule_times']:
                hour, minute = map(int, schedule_time.split(':'))
                
                self.scheduler.add_job(
                    self.generate_and_publish_video,
                    CronTrigger(hour=hour, minute=minute),
                    id=f'video_generation_{hour}_{minute}',
                    name=f'Generate and publish video at {schedule_time}',
                    misfire_grace_time=600
                )
                
                logger.info(f"Scheduled video generation at {schedule_time}")
            
            # Start scheduler
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            
            # Keep scheduler running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            logger.info("Stopping scheduler")
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def generate_and_publish_video(self):
        """Main pipeline: Generate content -> Create audio -> Create video -> Publish"""
        try:
            logger.info("=" * 80)
            logger.info("Starting video generation pipeline")
            logger.info("=" * 80)
            
            # Step 1: Generate content
            logger.info("Step 1: Generating content...")
            content = self.content_generator.get_random_content(
                duration_target=self.config['video_duration_max'] * 60
            )
            logger.info(f"Content generated: {content['title']}")
            logger.info(f"Total duration: {content['total_duration']} seconds")
            
            # Step 2: Generate audio
            logger.info("Step 2: Generating Tamil speech audio...")
            audio_filename = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            audio_path = self.tts_generator.generate_script_audio(
                content['script'],
                audio_filename
            )
            logger.info(f"Audio generated: {audio_path}")
            
            # Step 3: Create video
            logger.info("Step 3: Creating video...")
            video_title = content['title'].replace(' ', '_')
            video_path = self.video_creator.create_video(
                content,
                audio_path,
                video_title
            )
            logger.info(f"Video created: {video_path}")
            
            # Step 4: Publish to YouTube (if credentials available)
            video_id = None
            if self.youtube_uploader:
                logger.info("Step 4: Publishing to YouTube...")
                video_id = self.youtube_uploader.upload_video(
                    video_path=video_path,
                    title=content['title'],
                    description=content['description'],
                    tags=content['tags'],
                    category_id='27',  # Education
                    privacy_status='public'
                )
                
                if video_id:
                    logger.info(f"Video published successfully. Video ID: {video_id}")
                else:
                    logger.warning("Video upload failed")
            else:
                logger.info("Step 4: Skipping YouTube upload (credentials not available)")
            
            # Step 5: Save to database
            logger.info("Step 5: Saving to database...")
            self.db.add_video(
                title=content['title'],
                description=content['description'],
                video_path=video_path,
                audio_path=audio_path,
                video_id=video_id,
                duration=content['total_duration'],
                tags=','.join(content['tags'])
            )
            logger.info("Video record saved to database")
            
            logger.info("=" * 80)
            logger.info("Video generation pipeline completed successfully!")
            logger.info("=" * 80)
            
            return {
                'success': True,
                'video_id': video_id,
                'video_path': video_path,
                'title': content['title']
            }
        
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"Error in video generation pipeline: {e}")
            logger.error("=" * 80)
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_video_manual(self) -> Optional[dict]:
        """Manually trigger video generation (for testing)"""
        return self.generate_and_publish_video()
    
    def get_scheduled_jobs(self) -> list:
        """Get list of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': str(job.next_run_time)
            })
        return jobs


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scheduler = VideoGenerationScheduler()
    
    # For testing, generate one video manually
    logger.info("Generating test video...")
    result = scheduler.generate_video_manual()
    logger.info(f"Result: {result}")
    
    # Uncomment to start scheduled generation
    # scheduler.start()
