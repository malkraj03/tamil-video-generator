"""
Cloud Storage Manager - Google Cloud Storage integration
Handles upload, download, and cleanup of videos, audio, and images
"""

import os
import logging
from typing import Optional, List, Dict
from pathlib import Path
from datetime import datetime, timedelta
from google.cloud import storage
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


class CloudStorageManager:
    """Manage files in Google Cloud Storage"""
    
    def __init__(self, project_id: str, bucket_name: str, 
                 credentials_path: Optional[str] = None):
        """
        Initialize Cloud Storage Manager
        
        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name
            credentials_path: Path to service account JSON (optional)
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        
        # Initialize storage client
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = storage.Client(project=project_id, credentials=credentials)
        else:
            self.client = storage.Client(project=project_id)
        
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"Cloud Storage initialized: gs://{bucket_name}")
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Upload file to Cloud Storage
        
        Args:
            local_path: Local file path
            remote_path: Remote path in bucket (e.g., 'videos/video.mp4')
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(local_path):
                logger.error(f"File not found: {local_path}")
                return False
            
            blob = self.bucket.blob(remote_path)
            blob.upload_from_filename(local_path)
            
            logger.info(f"Uploaded: {local_path} → gs://{self.bucket_name}/{remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download file from Cloud Storage
        
        Args:
            remote_path: Remote path in bucket
            local_path: Local file path
            
        Returns:
            True if successful
        """
        try:
            # Create local directory if needed
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            
            logger.info(f"Downloaded: gs://{self.bucket_name}/{remote_path} → {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False
    
    def upload_video(self, local_path: str, video_id: str) -> Optional[str]:
        """
        Upload video to Cloud Storage
        
        Args:
            local_path: Local video file path
            video_id: Unique video identifier
            
        Returns:
            Remote path if successful
        """
        try:
            remote_path = f"videos/{video_id}/{Path(local_path).name}"
            
            if self.upload_file(local_path, remote_path):
                return remote_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None
    
    def upload_audio(self, local_path: str, video_id: str) -> Optional[str]:
        """Upload audio file to Cloud Storage"""
        try:
            remote_path = f"audio/{video_id}/{Path(local_path).name}"
            
            if self.upload_file(local_path, remote_path):
                return remote_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading audio: {e}")
            return None
    
    def upload_image(self, local_path: str, video_id: str) -> Optional[str]:
        """Upload image/thumbnail to Cloud Storage"""
        try:
            remote_path = f"images/{video_id}/{Path(local_path).name}"
            
            if self.upload_file(local_path, remote_path):
                return remote_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return None
    
    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in bucket with optional prefix
        
        Args:
            prefix: Prefix to filter files (e.g., 'videos/')
            
        Returns:
            List of file paths
        """
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete file from Cloud Storage
        
        Args:
            remote_path: Remote path in bucket
            
        Returns:
            True if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            
            logger.info(f"Deleted: gs://{self.bucket_name}/{remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def delete_folder(self, folder_prefix: str) -> int:
        """
        Delete all files in a folder
        
        Args:
            folder_prefix: Folder prefix (e.g., 'videos/video_id/')
            
        Returns:
            Number of deleted files
        """
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=folder_prefix)
            deleted_count = 0
            
            for blob in blobs:
                blob.delete()
                deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} files from {folder_prefix}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting folder: {e}")
            return 0
    
    def cleanup_old_files(self, days: int = 14, prefix: str = "") -> int:
        """
        Delete files older than specified days
        
        Args:
            days: Delete files older than this many days
            prefix: Prefix to filter files
            
        Returns:
            Number of deleted files
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            deleted_count = 0
            
            for blob in blobs:
                # Check if blob is older than cutoff
                if blob.updated and blob.updated.replace(tzinfo=None) < cutoff_date:
                    blob.delete()
                    deleted_count += 1
                    logger.info(f"Deleted old file: {blob.name}")
            
            logger.info(f"Cleanup: Deleted {deleted_count} old files (older than {days} days)")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0
    
    def get_file_url(self, remote_path: str, expiration_hours: int = 24) -> Optional[str]:
        """
        Get signed URL for file (for sharing)
        
        Args:
            remote_path: Remote path in bucket
            expiration_hours: URL expiration time in hours
            
        Returns:
            Signed URL if successful
        """
        try:
            blob = self.bucket.blob(remote_path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=expiration_hours),
                method="GET"
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Error generating signed URL: {e}")
            return None
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            blob = self.bucket.blob(remote_path)
            blob.reload()
            return blob.size
            
        except Exception as e:
            logger.error(f"Error getting file size: {e}")
            return None
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists in bucket"""
        try:
            blob = self.bucket.blob(remote_path)
            return blob.exists()
            
        except Exception as e:
            logger.error(f"Error checking file existence: {e}")
            return False
    
    def get_bucket_stats(self) -> Dict:
        """Get bucket statistics"""
        try:
            blobs = self.client.list_blobs(self.bucket_name)
            
            total_size = 0
            total_files = 0
            file_types = {}
            
            for blob in blobs:
                total_files += 1
                total_size += blob.size or 0
                
                # Count by file type
                ext = Path(blob.name).suffix or 'no_extension'
                file_types[ext] = file_types.get(ext, 0) + 1
            
            return {
                'total_files': total_files,
                'total_size_gb': round(total_size / (1024**3), 2),
                'file_types': file_types
            }
            
        except Exception as e:
            logger.error(f"Error getting bucket stats: {e}")
            return {}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    storage_manager = CloudStorageManager(
        project_id="your-project-id",
        bucket_name="tamil-video-generator"
    )
    
    # Upload a file
    # storage_manager.upload_file("local_file.mp4", "videos/video.mp4")
    
    # List files
    # files = storage_manager.list_files("videos/")
    # print(f"Files: {files}")
    
    # Get bucket stats
    stats = storage_manager.get_bucket_stats()
    print(f"Bucket stats: {stats}")
