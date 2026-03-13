"""
Legacy video_generator wrapper. Core logic moved to `services/`.
"""

from services.video_service import generate_video, fetch_context_image

__all__ = ["generate_video", "fetch_context_image"]
