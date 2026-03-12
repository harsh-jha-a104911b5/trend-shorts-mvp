"""
Configuration for Trend Shorts MVP.
All settings in one place for easy modification.
"""

import os
import torch

# ─── VIDEO SETTINGS ───────────────────────────────────────────────
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
SCENE_DURATION = 2          # seconds per scene
SCENE_COUNT = 4             # number of scenes per video
FPS = 24                    # frames per second
TRANSITION_DURATION = 0.3   # seconds for fade transitions
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ─── TEXT STYLING ─────────────────────────────────────────────────
FONT_SIZE = 80              # large for mobile readability
TEXT_COLOR = "white"
OUTLINE_COLOR = "black"
OUTLINE_WIDTH = 4           # pixels for text outline

# ─── GRADIENT BACKGROUNDS (top_color → bottom_color per scene) ───
SCENE_GRADIENTS = [
    ((10, 5, 40),   (180, 0, 120)),    # deep space → hot pink
    ((5, 20, 50),   (0, 180, 220)),    # dark ocean → electric cyan
    ((15, 35, 10),  (0, 220, 90)),     # dark forest → neon green
    ((45, 10, 10),  (255, 90, 0)),     # dark ember → blazing orange
]

# ─── AUDIO SETTINGS ──────────────────────────────────────────────
AUDIO_BPM = 130             # beats per minute for background music
AUDIO_VOLUME = 0.75         # master volume (0.0 – 1.0)

# ─── GOOGLE TRENDS ────────────────────────────────────────────────
TRENDS_REGION = "india"     # pytrends geo code
TRENDS_COUNT = 10           # how many trends to fetch

# ─── MULTI-VIDEO PIPELINE ────────────────────────────────────────
MAX_VIDEOS_PER_RUN = 5      # maximum videos to generate per execution

# ─── TREND FILTERING ─────────────────────────────────────────────
# Keywords/phrases that indicate an ALLOWED category
ALLOWED_KEYWORDS = [
    "tech", "ai", "artificial intelligence", "machine learning",
    "smartphone", "phone", "iphone", "samsung", "pixel", "nothing phone",
    "laptop", "macbook", "notebook", "chromebook",
    "gadget", "wearable", "smartwatch", "earbuds", "headphones",
    "software", "app", "update", "release", "launch",
    "gpu", "processor", "chip", "cpu", "ram", "ssd",
    "robot", "automation", "chatgpt", "gemini", "copilot", "claude",
    "tesla", "electric", "ev", "drone", "vr", "ar",
    "cyber", "hack", "security", "cloud", "5g", "wifi",
    "startup", "funding", "ipo", "deal", "price", "sale", "discount",
]

# Keywords/phrases that indicate a BLOCKED category
BLOCKED_KEYWORDS = [
    "politics", "election", "minister", "parliament", "modi", "congress",
    "bjp", "aap", "vote", "mla", "mp", "government",
    "celebrity", "bollywood", "actor", "actress", "movie", "film",
    "cricket", "ipl", "match", "football", "soccer", "hockey", "tennis",
    "murder", "crime", "arrest", "jail", "court", "police", "scam",
    "war", "attack", "bomb", "military", "army", "navy",
    "religion", "temple", "mosque", "church", "riot",
]

# ─── AI SCRIPT GENERATION ────────────────────────────────────────
# Set to "mock" for free local generation (default).
# Set to "gemini", "openai", or "claude" and provide the API key below.
SCRIPT_MODE = "mock"

# API keys (only needed if SCRIPT_MODE != "mock")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

# ─── YOUTUBE UPLOAD ──────────────────────────────────────────────
YOUTUBE_UPLOAD_ENABLED = True  # set False to skip uploads
YOUTUBE_PRIVACY = "public"     # "public", "unlisted", or "private"

# ─── TELEGRAM POSTING ────────────────────────────────────────────
TELEGRAM_ENABLED = True        # set False to skip Telegram posts
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ─── SCHEDULING ──────────────────────────────────────────────────
SCHEDULE_ENABLED = False       # set True to enable auto-scheduling
SCHEDULE_INTERVAL_HOURS = 3   # run every N hours

# ─── GPU DETECTION ────────────────────────────────────────────────
CUDA_AVAILABLE = torch.cuda.is_available()
DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"
