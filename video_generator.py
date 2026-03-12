"""
Generate a vertical (1080×1920) YouTube Shorts video from scene texts.

Pipeline:
  1. Render each scene as a PIL image (text on coloured background).
  2. Compose the scenes into a video with moviepy.
  3. Export to mp4 via ffmpeg (GPU-accelerated when CUDA is available).
"""

from __future__ import annotations

import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips

import config


# ─── PUBLIC API ───────────────────────────────────────────────────

def generate_video(script: dict) -> str:
    """
    Create a Shorts video from the given script and return the output path.

    Args:
        script: dict with "keyword" (str) and "scenes" (list[str]).

    Returns:
        Absolute path to the saved .mp4 file.
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    scenes = script["scenes"][:config.SCENE_COUNT]
    clips = []

    for idx, text in enumerate(scenes):
        bg_color = config.SCENE_BACKGROUNDS[idx % len(config.SCENE_BACKGROUNDS)]
        img = _render_scene(text, bg_color)
        clip = ImageClip(_pil_to_array(img), duration=config.SCENE_DURATION)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"short_{timestamp}.mp4"
    outpath = os.path.join(config.OUTPUT_DIR, filename)

    # Choose ffmpeg codec params — GPU or CPU
    codec, ffmpeg_params = _codec_params()

    video.write_videofile(
        outpath,
        fps=config.FPS,
        codec=codec,
        ffmpeg_params=ffmpeg_params,
        logger="bar",          # shows a progress bar
    )

    # Clean up
    video.close()
    for c in clips:
        c.close()

    return outpath


# ─── SCENE RENDERING ─────────────────────────────────────────────

def _render_scene(text: str, bg_color: tuple[int, int, int]) -> Image.Image:
    """Draw centred, outlined text on a solid-colour background."""
    img = Image.new("RGB", (config.VIDEO_WIDTH, config.VIDEO_HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    font = _get_font(config.FONT_SIZE)

    # Word-wrap text to fit the frame width (with padding)
    wrapped = _wrap_text(text, font, config.VIDEO_WIDTH - 120)

    # Measure wrapped block
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (config.VIDEO_WIDTH - text_w) / 2
    y = (config.VIDEO_HEIGHT - text_h) / 2

    # Draw outline by offsetting in 8 directions
    ow = config.OUTLINE_WIDTH
    for dx in (-ow, 0, ow):
        for dy in (-ow, 0, ow):
            if dx == 0 and dy == 0:
                continue
            draw.multiline_text(
                (x + dx, y + dy), wrapped, font=font,
                fill=config.OUTLINE_COLOR, align="center",
            )

    # Draw main text
    draw.multiline_text(
        (x, y), wrapped, font=font,
        fill=config.TEXT_COLOR, align="center",
    )

    return img


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Simple greedy word-wrap that respects max_width."""
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines)


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a bold font — tries common system paths, then falls back to default."""
    candidates = [
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    # Last resort — Pillow built-in bitmap font (small but works)
    return ImageFont.load_default()


# ─── HELPERS ──────────────────────────────────────────────────────

def _pil_to_array(img: Image.Image):
    """Convert a PIL Image to a numpy array for moviepy."""
    import numpy as np
    return np.array(img)


def _codec_params() -> tuple[str, list[str]]:
    """
    Return (codec, ffmpeg_params) for video export.

    If CUDA is available, attempt NVENC hardware encoding.
    Otherwise fall back to libx264 (CPU) which is universally available.
    """
    if config.CUDA_AVAILABLE:
        print("⚡ CUDA detected — using GPU-accelerated encoding (h264_nvenc)")
        return "h264_nvenc", [
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
        ]

    print("🖥  No CUDA GPU — using CPU encoding (libx264)")
    return "libx264", [
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
    ]
