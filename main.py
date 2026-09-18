"""
Main Application - Entry point for the Tamil Video Generator
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime
import json

from scheduler import VideoGenerationScheduler
from database import VideoDatabase

# Configure logging
def setup_logging(log_file: str = "video_generator.log", log_level: str = "INFO"):
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    return logger


class TamilVideoGeneratorApp:
    """Main application class"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self.scheduler = None
        self.db = None
    
    def initialize(self):
        """Initialize the application"""
        try:
            self.logger.info("Initializing Tamil Video Generator")
            
            # Load configuration
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Setup logging
            setup_logging(
                log_file=config.get('log_file', 'video_generator.log'),
                log_level=config.get('log_level', 'INFO')
            )
            
            # Initialize scheduler
            self.scheduler = VideoGenerationScheduler(self.config_file)
            self.db = VideoDatabase(config.get('database_path', 'videos.db'))
            
            self.logger.info("Application initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing application: {e}")
            raise
    
    def start_scheduler(self):
        """Start the scheduled video generation"""
        try:
            self.logger.info("Starting scheduler...")
            self.scheduler.start()
        except KeyboardInterrupt:
            self.logger.info("Scheduler interrupted by user")
            self.scheduler.stop()
        except Exception as e:
            self.logger.error(f"Error in scheduler: {e}")
            raise
    
    def generate_video_now(self):
        """Generate a video immediately (for testing)"""
        try:
            self.logger.info("Generating video immediately...")
            result = self.scheduler.generate_and_publish_video()
            
            if result['success']:
                self.logger.info(f"Video generated successfully!")
                self.logger.info(f"Video ID: {result.get('video_id')}")
                self.logger.info(f"Video path: {result.get('video_path')}")
            else:
                self.logger.error(f"Video generation failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating video: {e}")
            raise
    
    def show_status(self):
        """Show application status"""
        try:
            total_videos = self.db.get_total_videos()
            published_videos = self.db.get_published_videos()
            
            print("\n" + "=" * 80)
            print("TAMIL VIDEO GENERATOR - STATUS")
            print("=" * 80)
            print(f"Total videos generated: {total_videos}")
            print(f"Published videos: {published_videos}")
            print(f"Database: {self.db.db_path}")
            
            if self.scheduler:
                jobs = self.scheduler.get_scheduled_jobs()
                print(f"\nScheduled jobs: {len(jobs)}")
                for job in jobs:
                    print(f"  - {job['name']} (Next run: {job['next_run_time']})")
            
            print("=" * 80 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error showing status: {e}")
    
    def show_recent_videos(self, limit: int = 5):
        """Show recent videos"""
        try:
            videos = self.db.get_all_videos(limit=limit)
            
            print("\n" + "=" * 80)
            print(f"RECENT VIDEOS (Last {limit})")
            print("=" * 80)
            
            for video in videos:
                print(f"\nID: {video['id']}")
                print(f"Title: {video['title']}")
                print(f"Status: {video['status']}")
                print(f"Duration: {video['duration']} seconds")
                print(f"Created: {video['created_at']}")
                if video['video_id']:
                    print(f"YouTube ID: {video['video_id']}")
            
            print("\n" + "=" * 80 + "\n")
            
        except Exception as e:
            self.logger.error(f"Error showing videos: {e}")
    
    def cleanup_old_files(self, days: int = 30):
        """Clean up old files"""
        try:
            self.logger.info(f"Cleaning up files older than {days} days...")
            self.db.cleanup_old_files(days)
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up files: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Tamil Video Generator - Automated YouTube video creation'
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--mode',
        choices=['start', 'generate', 'status', 'videos', 'cleanup'],
        default='start',
        help='Operation mode'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of videos to show'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days for cleanup'
    )
    
    args = parser.parse_args()
    
    # Initialize application
    app = TamilVideoGeneratorApp(args.config)
    app.initialize()
    
    # Execute requested mode
    if args.mode == 'start':
        print("\n" + "=" * 80)
        print("TAMIL VIDEO GENERATOR - STARTING SCHEDULER")
        print("=" * 80)
        print("Press Ctrl+C to stop\n")
        app.show_status()
        app.start_scheduler()
    
    elif args.mode == 'generate':
        print("\n" + "=" * 80)
        print("TAMIL VIDEO GENERATOR - GENERATING VIDEO")
        print("=" * 80 + "\n")
        result = app.generate_video_now()
        app.show_status()
    
    elif args.mode == 'status':
        app.show_status()
    
    elif args.mode == 'videos':
        app.show_recent_videos(args.limit)
    
    elif args.mode == 'cleanup':
        print(f"\nCleaning up files older than {args.days} days...")
        app.cleanup_old_files(args.days)
        print("Cleanup completed!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
