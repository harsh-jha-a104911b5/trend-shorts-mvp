"""
Premium Video Generator with Auto-Font, Unsplash, and Curiosity Layout.
"""

from __future__ import annotations
import os
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, vfx
from datetime import datetime
import wave
import tempfile
import config

# ─── ASSET HELPERS ────────────────────────────────────────────────


def ensure_hindi_font():
    """Download NotoSansDevanagari if missing."""
    os.makedirs(config.FONTS_DIR, exist_ok=True)
    font_path = os.path.join(config.FONTS_DIR, config.HINDI_FONT_NAME)
    if not os.path.exists(font_path):
        print(f"📥 Downloading Devanagari font...")
        try:
            r = requests.get(config.HINDI_FONT_URL, timeout=30)
            with open(font_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"❌ Font download failed: {e}")
    return font_path if os.path.exists(font_path) else None


def fetch_context_image(keyword: str) -> Image.Image | None:
    """Fetch background image from Unsplash."""
    if not config.UNSPLASH_ACCESS_KEY:
        return None

    print(f"🖼 Fetching image for '{keyword}'...")
    try:
        url = f"https://api.unsplash.com/search/photos?query={keyword}&per_page=1&client_id={config.UNSPLASH_ACCESS_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("results"):
            img_url = data["results"][0]["urls"]["regular"]
            img_r = requests.get(img_url, timeout=10)
            return Image.open(requests.get(img_url, stream=True).raw).convert("RGB")
    except Exception as e:
        print(f"⚠️ Unsplash failed: {e}")
    return None


# ─── CORE GENERATOR ───────────────────────────────────────────────


def generate_video(script: dict) -> str:
    """Render a curiosity-gap Short with multi-layered layout."""
    ensure_hindi_font()
    keyword = script["keyword"]
    bg_image = fetch_context_image(keyword)

    clips = []

    for idx, text in enumerate(script["scenes"]):
        # Create frame
        img = _render_frame(text, idx, bg_image, script["scenes"])

        # Clip with Zoom effect for retention
        clip = ImageClip(np.array(img), duration=config.SCENE_DURATION)

        # Simple Zoom In
        clip = clip.with_effects([vfx.Resize(lambda t: 1 + 0.05 * t)])

        # Fades
        clip = clip.with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.3)])
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    # Audio
    audio_path = _generate_beat(video.duration)
    video = video.with_audio(AudioFileClip(audio_path))

    # Export
    outpath = os.path.join(
        config.OUTPUT_DIR,
        f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{script['angle']}.mp4",
    )
    codec = "h264_nvenc" if config.CUDA_AVAILABLE else "libx264"

    video.write_videofile(
        outpath, fps=config.FPS, codec=codec, audio_codec="aac", logger=None
    )

    # Cleanup
    video.close()
    if os.path.exists(audio_path):
        os.unlink(audio_path)

    return outpath


def _render_frame(
    text: str, idx: int, bg_img: Image.Image | None, scenes: list[str]
) -> Image.Image:
    W, H = config.VIDEO_WIDTH, config.VIDEO_HEIGHT

    # 1. Background (Image with blur + dark overlay or Gradient)
    if bg_img:
        img = bg_img.resize((W, H), Image.Resampling.LANCZOS)
        img = img.filter(ImageFilter.GaussianBlur(20))
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 160))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    else:
        # Fallback to gradient
        img = _create_fancy_gradient(W, H, idx)

    draw = ImageDraw.Draw(img, "RGBA")

    # 2. Layout Distribution
    # Top: Hook (Scene 0)
    # Center: Visual context (Image if available)
    # Bottom: Why/Explanation (Scenes 1-3)

    hook_font = _get_font(config.FONT_SIZE_HOOK)
    body_font = _get_font(config.FONT_SIZE_BODY)

    # Render Hook (Always at top)
    hook_text = scenes[0]
    _draw_centered_text(draw, hook_text, hook_font, W, 250)

    # Render Current Scene Text (at bottom area)
    if idx > 0:
        _draw_centered_text(draw, text, body_font, W, H - 450)

    # Layout decoration - middle line
    draw.line([(W * 0.1, H // 2), (W * 0.9, H // 2)], fill=(255, 255, 255, 50), width=2)

    return img


def _draw_centered_text(
    draw: ImageDraw, text: str, font: ImageFont, W: int, y_pos: int
):
    """Draw text with shadow inside a safe margin."""
    lines = _wrap_text(text, font, W - 150)
    bbox = draw.multiline_textbbox((0, 0), lines, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) / 2

    # Shadow
    draw.multiline_text(
        (x + 4, y_pos + 4), lines, font=font, fill="black", align="center"
    )
    # Main
    draw.multiline_text((x, y_pos), lines, font=font, fill="white", align="center")


def _wrap_text(text: str, font: ImageFont, max_w: int) -> str:
    words = text.split()
    lines = []
    curr = ""
    for w in words:
        test = f"{curr} {w}".strip()
        if font.getbbox(test)[2] <= max_w:
            curr = test
        else:
            if curr:
                lines.append(curr)
            curr = w
    if curr:
        lines.append(curr)
    return "\n".join(lines)


def _get_font(size: int):
    path = os.path.join(config.FONTS_DIR, config.HINDI_FONT_NAME)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _create_fancy_gradient(w, h, idx):
    top = (idx * 40 % 255, 20, 100)
    bot = (20, idx * 60 % 255, 150)
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / h
        arr[y, :] = [int(top[i] * (1 - t) + bot[i] * t) for i in range(3)]
    return Image.fromarray(arr)


def _generate_beat(duration):
    sr = 44100
    n = int(sr * duration)
    t = np.linspace(0, duration, n)
    # Simple rhythmic synth beat
    beat = 0.3 * np.sin(2 * np.pi * 60 * t) * np.exp(-10 * (t % 0.5))
    wav_path = os.path.join(tempfile.gettempdir(), "beat.wav")
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((beat * 32767).astype(np.int16).tobytes())
    return wav_path
