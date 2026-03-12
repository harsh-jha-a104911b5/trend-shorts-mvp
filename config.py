"""
Configuration for Trend Shorts MVP - Autonomous Growth Engine.
"""

import os
import torch
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# ─── VIDEO SETTINGS ───────────────────────────────────────────────
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SCENE_DURATION = 3          # Increased slightly for better reading
SCENE_COUNT = 4             # 1: Hook, 2: Trend, 3: Why, 4: CTA
FPS = 24
TRANSITION_DURATION = 0.5   
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ─── TEXT STYLING ─────────────────────────────────────────────────
FONT_SIZE_HOOK = 100        # Larger for top hook
FONT_SIZE_BODY = 70         # For bottom explanation
TEXT_COLOR = "white"
OUTLINE_COLOR = "black"
OUTLINE_WIDTH = 5

# ─── API KEYS ────────────────────────────────────────────────────
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ─── MULTI-ANGLE CONFIG ──────────────────────────────────────────
ANGLES = ["Shock", "Curiosity", "Problem", "Benefit"]
MAX_TRENDS_PER_RUN = 5      # 5 trends * 4 angles = 20 videos

# ─── TREND FILTERING ─────────────────────────────────────────────
ALLOWED_KEYWORDS = [
    "ai", "technology", "software", "startup", "robot", 
    "phone", "openai", "google", "apple", "tesla", "gadget", "chip"
]

BLOCKED_KEYWORDS = [
    "politics", "crime", "war", "celebrity", "sports", "bollywood", "cricket"
]

# ─── CACHING & FILES ─────────────────────────────────────────────
PROCESSED_TRENDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed_trends.json")
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
HINDI_FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
HINDI_FONT_NAME = "NotoSansDevanagari-Regular.ttf"

# ─── PIPELINE SETTINGS ───────────────────────────────────────────
YOUTUBE_UPLOAD_ENABLED = True
YOUTUBE_PRIVACY = "public"
TELEGRAM_ENABLED = True
SCHEDULE_ENABLED = True
SCHEDULE_INTERVAL_HOURS = 3

# ─── GPU DETECTION ────────────────────────────────────────────────
CUDA_AVAILABLE = torch.cuda.is_available()
DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"

# ─── TELEGRAM GROWTH ─────────────────────────────────────────────
TELEGRAM_LINK = "https://t.me/aitechtrendss"
TELEGRAM_CTA_TEXT = "Full story on Telegram"
YOUTUBE_DESCRIPTION_FOOTER = f"\n\nJoin Telegram for real-time tech trends:\n{TELEGRAM_LINK}"
