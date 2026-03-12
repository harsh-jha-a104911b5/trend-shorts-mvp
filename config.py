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
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

# ─── TEXT STYLING ─────────────────────────────────────────────────
FONT_SIZE = 80              # large for mobile readability
TEXT_COLOR = "white"
OUTLINE_COLOR = "black"
OUTLINE_WIDTH = 4           # pixels for text outline

# ─── BACKGROUND COLORS (one per scene, cycled) ───────────────────
SCENE_BACKGROUNDS = [
    (25, 25, 112),    # midnight blue
    (139, 0, 0),      # dark red
    (0, 100, 0),      # dark green
    (75, 0, 130),     # indigo
]

# ─── GOOGLE TRENDS ────────────────────────────────────────────────
TRENDS_REGION = "india"     # pytrends geo code
TRENDS_COUNT = 10           # how many trends to fetch

# ─── AI SCRIPT GENERATION ────────────────────────────────────────
# Set to "mock" for free local generation (default).
# Set to "gemini", "openai", or "claude" and provide the API key below.
SCRIPT_MODE = "mock"

# API keys (only needed if SCRIPT_MODE != "mock")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

# ─── GPU DETECTION ────────────────────────────────────────────────
CUDA_AVAILABLE = torch.cuda.is_available()
DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"
