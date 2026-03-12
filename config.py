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
