"""
YouTube Shorts uploader via YouTube Data API v3.

Uses existing OAuth credentials (youtube_credentials.json).
Token is cached locally (youtube_token.json) so login is only required once.
"""

from __future__ import annotations

import os
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import config

# OAuth scope for uploading videos
_SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Paths relative to project root
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_CREDENTIALS_FILE = os.path.join(_PROJECT_DIR, "youtube_credentials.json")
_TOKEN_FILE = os.path.join(_PROJECT_DIR, "youtube_token.json")


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    privacy: str = "public",
) -> str | None:
    """
    Upload a video to YouTube and return the video URL.

    Args:
        video_path:   Absolute path to the .mp4 file.
        title:        Video title (max 100 chars).
        description:  Video description.
        tags:         List of tag strings.
        privacy:      "public", "unlisted", or "private".

    Returns:
        YouTube video URL on success, or None on failure.
    """
    try:
        youtube = _get_authenticated_service()

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": "28",  # Science & Technology
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
                "madeForKids": False,
            },
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024,  # 1 MB chunks
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        # Execute upload with progress
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"   📤 Upload progress: {pct}%")

        video_id = response["id"]
        video_url = f"https://youtube.com/shorts/{video_id}"
        print(f"   ✅ Upload complete: {video_url}")
        return video_url

    except Exception as e:
        print(f"   ❌ YouTube upload failed: {e}")
        return None


def _get_authenticated_service():
    """
    Build an authenticated YouTube API service.

    Loads cached token if available, otherwise runs OAuth flow
    and caches the new token for future runs.
    """
    creds = None

    # Load cached token
    if os.path.exists(_TOKEN_FILE):
        with open(_TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # Refresh or re-authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("   🔄 Refreshing YouTube token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(_CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"YouTube credentials not found at: {_CREDENTIALS_FILE}\n"
                    "Download from Google Cloud Console → APIs → Credentials."
                )
            print("   🔐 Opening browser for YouTube authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                _CREDENTIALS_FILE, _SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Cache token for next run
        with open(_TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
        print("   💾 Token cached for future runs")

    return build("youtube", "v3", credentials=creds)
