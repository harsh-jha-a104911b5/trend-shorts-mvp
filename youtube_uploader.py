"""
Legacy youtube_uploader wrapper. Core logic moved to `services/`.
"""

from services.youtube_service import upload_video

__all__ = ["upload_video"]
