"""
YouTube Uploader - Handles video upload and publishing to YouTube
Supports both local (browser OAuth) and headless (refresh token) authentication
"""

import os
import json
import logging
from typing import Optional, Dict
from pathlib import Path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# YouTube API scopes
YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
]


class YouTubeUploader:
    """Upload and manage videos on YouTube"""

    def __init__(self, credentials_file: str = "credentials.json",
                 token_file: str = "token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with YouTube API.

        Supports two modes:
        1. Headless (CI/CD): Uses YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET,
           and YOUTUBE_REFRESH_TOKEN environment variables
        2. Local: Uses credentials.json file and browser-based OAuth flow
        """
        try:
            credentials = None

            # Mode 1: Headless authentication via environment variables
            client_id = os.getenv('YOUTUBE_CLIENT_ID')
            client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
            refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')

            if client_id and client_secret and refresh_token:
                logger.info("Using headless authentication (environment variables)")
                credentials = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                    token_uri='https://oauth2.googleapis.com/token',
                    scopes=YOUTUBE_SCOPES,
                )
                # Refresh to get a valid access token
                credentials.refresh(Request())
                logger.info("Headless authentication successful")

            # Mode 2: Local authentication via token file or browser flow
            else:
                logger.info("Using local authentication")

                # Try to load existing token
                if os.path.exists(self.token_file):
                    with open(self.token_file, 'rb') as token:
                        credentials = pickle.load(token)

                # Refresh token if expired
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())

                # Create new credentials via browser flow
                if not credentials or not credentials.valid:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.info("For local use: download OAuth credentials from Google Cloud Console")
                        logger.info("For cloud use: set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
                        return

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file,
                        YOUTUBE_SCOPES
                    )
                    credentials = flow.run_local_server(port=0)

                    # Save token for future use
                    with open(self.token_file, 'wb') as token:
                        pickle.dump(credentials, token)

            # Build YouTube service
            if credentials:
                self.youtube = build('youtube', 'v3', credentials=credentials)
                logger.info("Successfully authenticated with YouTube API")
            else:
                logger.warning("YouTube authentication not available")

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    def upload_video(self, video_path: str, title: str, description: str,
                     tags: list, category_id: str = "27",
                     privacy_status: str = "public",
                     schedule_time: Optional[str] = None) -> Optional[str]:
        """
        Upload video to YouTube

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (27 = Education)
            privacy_status: 'public', 'private', or 'unlisted'
            schedule_time: ISO 8601 format for scheduled publishing

        Returns:
            Video ID if successful, None otherwise
        """
        try:
            if not self.youtube:
                logger.error("YouTube service not initialized")
                return None

            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None

            logger.info(f"Uploading video: {title}")

            # Truncate title if too long (YouTube limit: 100 chars)
            if len(title) > 100:
                title = title[:97] + "..."

            # Truncate description if too long (YouTube limit: 5000 chars)
            if len(description) > 5000:
                description = description[:4997] + "..."

            # Prepare request body
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags[:500],  # YouTube tag limit
                    'categoryId': category_id,
                    'defaultLanguage': 'ta',
                    'defaultAudioLanguage': 'ta'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'madeForKids': False,
                    'selfDeclaredMadeForKids': False,
                }
            }

            # Add scheduled publishing if specified
            if schedule_time:
                body['status']['publishAt'] = schedule_time
                body['status']['privacyStatus'] = 'private'

            # Prepare media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=10 * 1024 * 1024  # 10MB chunks
            )

            # Create request
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )

            # Execute upload with progress tracking
            response = self._execute_upload(request)

            if response:
                video_id = response['id']
                logger.info(f"Video uploaded successfully! Video ID: {video_id}")
                logger.info(f"Video URL: https://www.youtube.com/watch?v={video_id}")
                return video_id

            return None

        except HttpError as e:
            logger.error(f"HTTP error during upload: {e}")
            if e.resp.status == 403:
                logger.error("Quota exceeded or insufficient permissions. "
                             "Check YouTube Data API quota in Google Cloud Console.")
            return None
        except Exception as e:
            logger.error(f"Error uploading video: {e}")
            return None

    def _execute_upload(self, request, max_retries: int = 5) -> Optional[Dict]:
        """Execute upload with retry logic"""
        import time

        response = None
        retry_count = 0

        while response is None:
            try:
                status, response = request.next_chunk()

                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")

            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = min(2 ** retry_count, 60)
                        logger.warning(f"Retrying upload in {wait_time}s "
                                       f"(attempt {retry_count}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Max retries exceeded")
                        return None
                else:
                    logger.error(f"HTTP error: {e}")
                    return None

        return response

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set custom thumbnail for video"""
        try:
            if not self.youtube:
                logger.error("YouTube service not initialized")
                return False

            if not os.path.exists(thumbnail_path):
                logger.error(f"Thumbnail file not found: {thumbnail_path}")
                return False

            media = MediaFileUpload(thumbnail_path, mimetype='image/jpeg', resumable=True)
            request = self.youtube.thumbnails().set(videoId=video_id, media_body=media)
            request.execute()

            logger.info(f"Thumbnail set successfully for video: {video_id}")
            return True

        except Exception as e:
            logger.error(f"Error setting thumbnail: {e}")
            return False

    def get_video_status(self, video_id: str) -> Optional[Dict]:
        """Get video status and details"""
        try:
            if not self.youtube:
                return None

            request = self.youtube.videos().list(
                part='status,snippet,statistics',
                id=video_id
            )
            response = request.execute()

            if response['items']:
                return response['items'][0]
            return None

        except Exception as e:
            logger.error(f"Error getting video status: {e}")
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Check if credentials are available
    has_env = all([
        os.getenv('YOUTUBE_CLIENT_ID'),
        os.getenv('YOUTUBE_CLIENT_SECRET'),
        os.getenv('YOUTUBE_REFRESH_TOKEN'),
    ])

    if has_env:
        print("Environment variables found. Testing headless authentication...")
    elif os.path.exists("credentials.json"):
        print("credentials.json found. Testing local authentication...")
    else:
        print("No YouTube credentials found.")
        print("\nFor local setup, run: python auth_setup.py")
        print("For cloud setup, set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
