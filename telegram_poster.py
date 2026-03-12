"""
Telegram Bot poster for sharing new video updates.

Uses the Telegram Bot API (HTTP) — no heavy SDK needed.
Configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py.
"""

from __future__ import annotations

import requests
import config


def post_to_telegram(title: str, video_url: str) -> bool:
    """
    Send a formatted message to the configured Telegram channel/chat.

    Args:
        title:     Video title string.
        video_url: YouTube video URL.

    Returns:
        True if the message was sent, False otherwise.
    """
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("   ⚠  Telegram not configured (set TELEGRAM_BOT_TOKEN & TELEGRAM_CHAT_ID in config.py)")
        return False

    message = (
        f"🔥 *New Tech Trend*\n\n"
        f"📹 {_escape_md(title)}\n\n"
        f"▶️ Watch here: {video_url}\n\n"
        f"_Join for more updates\\!_"
    )

    try:
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": False,
        }
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json()

        if data.get("ok"):
            print("   ✅ Telegram post sent")
            return True
        else:
            print(f"   ❌ Telegram API error: {data.get('description', 'Unknown')}")
            return False

    except Exception as e:
        print(f"   ❌ Telegram post failed: {e}")
        return False


def _escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special = r"_*[]()~`>#+-=|{}.!"
    escaped = ""
    for ch in text:
        if ch in special:
            escaped += f"\\{ch}"
        else:
            escaped += ch
    return escaped
