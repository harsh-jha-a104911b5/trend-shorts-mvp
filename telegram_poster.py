"""
Legacy telegram_poster wrapper. Core logic moved to `services/`.
"""

from services.telegram_service import post_to_telegram

__all__ = ["post_to_telegram"]
