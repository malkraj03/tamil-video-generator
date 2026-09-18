"""
Database Module - Stores video metadata and publishing history
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoDatabase:
    """SQLite database for video metadata"""
    
    def __init__(self, db_path: str = "videos.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Videos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    video_path TEXT NOT NULL,
                    audio_path TEXT,
                    video_id TEXT UNIQUE,
                    duration INTEGER,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    published_at TIMESTAMP,
                    status TEXT DEFAULT 'created',
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0
                )
            ''')
            
            # Publishing history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publishing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    youtube_video_id TEXT,
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    error_message TEXT,
                    FOREIGN KEY (video_id) REFERENCES videos(id)
                )
            ''')
            
            # Statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    date DATE,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    watch_time INTEGER DEFAULT 0,
                    FOREIGN KEY (video_id) REFERENCES videos(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def add_video(self, title: str, description: str, video_path: str,
                  audio_path: str = None, video_id: str = None,
                  duration: int = None, tags: str = None) -> int:
        """Add a new video record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO videos 
                (title, description, video_path, audio_path, video_id, duration, tags, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, video_path, audio_path, video_id, duration, tags, 'created'))
            
            conn.commit()
            video_id_db = cursor.lastrowid
            conn.close()
            
            logger.info(f"Video added to database: ID {video_id_db}")
            return video_id_db
            
        except Exception as e:
            logger.error(f"Error adding video to database: {e}")
            raise
    
    def update_video_status(self, video_id: int, status: str, 
                           youtube_video_id: str = None):
        """Update video status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE videos 
                SET status = ?, video_id = ?, published_at = ?
                WHERE id = ?
            ''', (status, youtube_video_id, datetime.now(), video_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Video {video_id} status updated to: {status}")
            
        except Exception as e:
            logger.error(f"Error updating video status: {e}")
            raise
    
    def add_publishing_history(self, video_id: int, youtube_video_id: str = None,
                              status: str = 'success', error_message: str = None):
        """Add publishing history record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO publishing_history 
                (video_id, youtube_video_id, status, error_message)
                VALUES (?, ?, ?, ?)
            ''', (video_id, youtube_video_id, status, error_message))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Publishing history recorded for video {video_id}")
            
        except Exception as e:
            logger.error(f"Error adding publishing history: {e}")
            raise
    
    def get_video(self, video_id: int) -> Optional[Dict]:
        """Get video details"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting video: {e}")
            return None
    
    def get_all_videos(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get all videos with pagination"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM videos 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting videos: {e}")
            return []
    
    def get_videos_by_status(self, status: str) -> List[Dict]:
        """Get videos by status"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM videos WHERE status = ? ORDER BY created_at DESC', (status,))
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting videos by status: {e}")
            return []
    
    def add_statistics(self, video_id: int, views: int = 0, likes: int = 0,
                      comments: int = 0, shares: int = 0, watch_time: int = 0):
        """Add statistics record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO statistics 
                (video_id, date, views, likes, comments, shares, watch_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (video_id, datetime.now().date(), views, likes, comments, shares, watch_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error adding statistics: {e}")
            raise
    
    def get_statistics(self, video_id: int) -> List[Dict]:
        """Get statistics for a video"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM statistics 
                WHERE video_id = ? 
                ORDER BY date DESC
            ''', (video_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return []
    
    def get_total_videos(self) -> int:
        """Get total number of videos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM videos')
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting total videos: {e}")
            return 0
    
    def get_published_videos(self) -> int:
        """Get number of published videos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'published'")
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting published videos: {e}")
            return 0
    
    def cleanup_old_files(self, days: int = 30):
        """Clean up old video and audio files"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get videos older than specified days
            cursor.execute('''
                SELECT video_path, audio_path FROM videos 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            rows = cursor.fetchall()
            
            deleted_count = 0
            for video_path, audio_path in rows:
                try:
                    if video_path and Path(video_path).exists():
                        Path(video_path).unlink()
                        deleted_count += 1
                    if audio_path and Path(audio_path).exists():
                        Path(audio_path).unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"Error deleting file: {e}")
            
            conn.close()
            logger.info(f"Cleaned up {deleted_count} old files")
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test database
    db = VideoDatabase()
    
    # Add test video
    video_id = db.add_video(
        title="Test Video",
        description="This is a test video",
        video_path="/path/to/video.mp4",
        duration=900,
        tags="test,tamil"
    )
    
    print(f"Added video with ID: {video_id}")
    
    # Get video
    video = db.get_video(video_id)
    print(f"Video: {video}")
    
    # Get all videos
    videos = db.get_all_videos()
    print(f"Total videos: {len(videos)}")
