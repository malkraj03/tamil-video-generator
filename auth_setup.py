"""
YouTube OAuth Setup Script

Run this ONCE on your local machine to get the refresh token needed for cloud deployment.

Usage:
    python auth_setup.py

Prerequisites:
    1. Go to https://console.cloud.google.com/
    2. Create a project (or select existing)
    3. Enable YouTube Data API v3
    4. Go to Credentials -> Create Credentials -> OAuth 2.0 Client ID
    5. Application type: Desktop application
    6. Download the JSON file
    7. Save it as 'credentials.json' in this project folder
    8. Run this script

Output:
    This script will print YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and
    YOUTUBE_REFRESH_TOKEN values that you need to add as GitHub Secrets.
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_youtube_auth():
    """Run OAuth flow and print credentials for GitHub Secrets"""

    credentials_file = "credentials.json"

    if not os.path.exists(credentials_file):
        print("\n" + "=" * 70)
        print("ERROR: credentials.json not found!")
        print("=" * 70)
        print()
        print("Please follow these steps first:")
        print()
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project (or select existing one)")
        print("3. Go to 'APIs & Services' -> 'Library'")
        print("4. Search for 'YouTube Data API v3' and ENABLE it")
        print("5. Go to 'APIs & Services' -> 'Credentials'")
        print("6. Click 'Create Credentials' -> 'OAuth 2.0 Client ID'")
        print("7. If prompted, configure the OAuth consent screen:")
        print("   - User Type: External")
        print("   - App name: Tamil Video Generator")
        print("   - Add your email as test user")
        print("8. Application type: 'Desktop application'")
        print("9. Click 'Create'")
        print("10. Click 'Download JSON' (download icon)")
        print("11. Save the file as 'credentials.json' in this folder:")
        print(f"    {os.path.abspath('.')}")
        print("12. Run this script again: python auth_setup.py")
        print()
        print("=" * 70)
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube',
        ]

        print("\n" + "=" * 70)
        print("YouTube OAuth Setup")
        print("=" * 70)
        print()
        print("A browser window will open for YouTube authentication.")
        print("Please sign in with the Google account that owns your YouTube channel.")
        print("Grant ALL requested permissions.")
        print()

        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        credentials = flow.run_local_server(port=8090)

        # Read client info from credentials.json
        with open(credentials_file, 'r') as f:
            client_data = json.load(f)

        # Handle both 'installed' and 'web' credential types
        if 'installed' in client_data:
            client_info = client_data['installed']
        elif 'web' in client_data:
            client_info = client_data['web']
        else:
            client_info = client_data

        client_id = client_info['client_id']
        client_secret = client_info['client_secret']
        refresh_token = credentials.refresh_token

        if not refresh_token:
            print("\nERROR: No refresh token received.")
            print("Try deleting 'token.pickle' and running again.")
            sys.exit(1)

        # Print the values needed for GitHub Secrets
        print()
        print("=" * 70)
        print("SUCCESS! Authentication completed.")
        print("=" * 70)
        print()
        print("Add these as GitHub Secrets (Settings -> Secrets -> Actions):")
        print()
        print(f"YOUTUBE_CLIENT_ID={client_id}")
        print()
        print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
        print()
        print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
        print()
        print("=" * 70)
        print()
        print("IMPORTANT STEPS:")
        print("1. Go to your GitHub repository")
        print("2. Go to Settings -> Secrets and variables -> Actions")
        print("3. Click 'New repository secret'")
        print("4. Add each of the 3 secrets above (name=value)")
        print("5. The GitHub Actions workflow will use these automatically")
        print()
        print("=" * 70)

        # Also verify the token works
        print("\nVerifying authentication...")
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        test_creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri='https://oauth2.googleapis.com/token',
        )
        test_creds.refresh(Request())

        youtube = build('youtube', 'v3', credentials=test_creds)
        channels = youtube.channels().list(part='snippet', mine=True).execute()

        if channels.get('items'):
            channel = channels['items'][0]
            print(f"Authenticated channel: {channel['snippet']['title']}")
            print(f"Channel ID: {channel['id']}")
        else:
            print("Warning: No YouTube channel found for this account.")
            print("Create a channel at https://www.youtube.com/ first.")

        print("\nSetup complete!")

    except ImportError:
        print("Missing dependencies. Install with: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("- Delete 'token.pickle' and try again")
        print("- Make sure you enabled YouTube Data API v3")
        print("- Make sure your OAuth consent screen is configured")
        print("- Add your email as a test user in OAuth consent screen")
        sys.exit(1)


if __name__ == "__main__":
    setup_youtube_auth()
