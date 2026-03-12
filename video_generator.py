"""
Generate a premium vertical (1080×1920) YouTube Shorts video from scene texts.

Pipeline:
  1. Render each scene with gradient backgrounds, decorative elements,
     glowing text, and vignette effects.
  2. Generate a synthetic background beat (kick, snare, hi-hat, bass, pad).
  3. Compose scenes with fade transitions via moviepy.
  4. Export to mp4 via ffmpeg (GPU-accelerated when CUDA is available).
"""

from __future__ import annotations

import os
import wave
import tempfile
from datetime import datetime

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, vfx

import config


# ─── PUBLIC API ───────────────────────────────────────────────────

def generate_video(script: dict) -> str:
    """
    Create a premium Shorts video and return the output path.

    Args:
        script: dict with "keyword" (str) and "scenes" (list[str]).

    Returns:
        Absolute path to the saved .mp4 file.
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    scenes = script["scenes"][: config.SCENE_COUNT]
    clips = []

    for idx, text in enumerate(scenes):
        gradient = config.SCENE_GRADIENTS[idx % len(config.SCENE_GRADIENTS)]
        img = _render_scene(text, gradient, idx)
        clip = ImageClip(np.array(img), duration=config.SCENE_DURATION)

        # Fade transitions on every clip
        fade = config.TRANSITION_DURATION
        clip = clip.with_effects([vfx.FadeIn(fade), vfx.FadeOut(fade)])

        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    # Generate & attach background music
    print("🎵 Generating background beat...")
    audio_path = _generate_background_music(video.duration)
    audio = AudioFileClip(audio_path)
    video = video.with_audio(audio)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"short_{timestamp}.mp4"
    outpath = os.path.join(config.OUTPUT_DIR, filename)

    codec, ffmpeg_params = _codec_params()

    video.write_videofile(
        outpath,
        fps=config.FPS,
        codec=codec,
        ffmpeg_params=ffmpeg_params,
        audio_codec="aac",
        logger="bar",
    )

    # Clean up
    video.close()
    audio.close()
    for c in clips:
        c.close()
    try:
        os.unlink(audio_path)
    except OSError:
        pass

    return outpath


# ═══════════════════════════════════════════════════════════════════
#  SCENE RENDERING — premium visuals
# ═══════════════════════════════════════════════════════════════════

def _render_scene(
    text: str,
    gradient: tuple[tuple[int, int, int], tuple[int, int, int]],
    scene_idx: int,
) -> Image.Image:
    """Render a visually rich scene with gradient, decorations, glow text."""
    W, H = config.VIDEO_WIDTH, config.VIDEO_HEIGHT
    color_top, color_bot = gradient

    # 1. Gradient background
    img = _create_gradient(W, H, color_top, color_bot)

    # 2. Decorative geometry
    _add_decorations(img, color_bot, scene_idx)

    # 3. Vignette overlay
    img = _add_vignette(img)

    # 4. Glowing centered text
    _add_glowing_text(img, text, color_bot)

    return img


# ── gradient ──────────────────────────────────────────────────────

def _create_gradient(w: int, h: int, c1: tuple, c2: tuple) -> Image.Image:
    """Smooth vertical gradient with a slight power-curve for depth."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = (y / h) ** 0.8  # subtle curve
        arr[y, :] = [
            int(c1[0] * (1 - t) + c2[0] * t),
            int(c1[1] * (1 - t) + c2[1] * t),
            int(c1[2] * (1 - t) + c2[2] * t),
        ]
    return Image.fromarray(arr)


# ── decorations ───────────────────────────────────────────────────

def _add_decorations(img: Image.Image, accent: tuple, idx: int) -> None:
    """Overlay geometric accents — corner lines, floating circles, dots."""
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size
    a40 = accent + (40,)
    a25 = accent + (25,)
    a50 = accent + (50,)
    a20 = accent + (20,)

    # Corner lines — top-left
    for i in range(3):
        off = i * 30
        draw.line([(0, 80 + off), (200 - off, 0)], fill=a40, width=3)

    # Corner lines — bottom-right
    for i in range(3):
        off = i * 30
        draw.line([(W, H - 80 - off), (W - 200 + off, H)], fill=a40, width=3)

    # Floating circles (shifted per scene for variety)
    circles = [
        (0.15, 0.20, 60), (0.85, 0.30, 40),
        (0.10, 0.75, 50), (0.90, 0.80, 35),
        (0.50, 0.12, 30), (0.70, 0.88, 45),
    ]
    for cx_f, cy_f, r in circles:
        cx = (int(cx_f * W) + idx * 80) % W
        cy = int(cy_f * H)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a25, outline=a40, width=2)

    # Horizontal accent bars near top & bottom
    draw.line([(W * 0.2, 160), (W * 0.8, 160)], fill=a50, width=2)
    draw.line([(W * 0.2, H - 160), (W * 0.8, H - 160)], fill=a50, width=2)

    # Scattered micro-dots
    for i in range(20):
        x = (100 + i * 120 + idx * 50) % W
        y = (200 + i * 180 + idx * 70) % H
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=a20)

    # Diamond accent at center-top
    cx, cy = W // 2, 100
    s = 18
    draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                 fill=a40, outline=a50)


# ── vignette ──────────────────────────────────────────────────────

def _add_vignette(img: Image.Image) -> Image.Image:
    """Subtle dark vignette fading from edges inward."""
    W, H = img.size
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(vig)

    steps = 40
    for i in range(steps):
        shrink = int(i * max(W, H) / 100)
        alpha = int(100 * (1 - i / steps))
        x0 = -100 + shrink
        y0 = -100 + shrink
        x1 = W + 100 - shrink
        y1 = H + 100 - shrink
        if x0 < x1 and y0 < y1:
            draw.rectangle([x0, y0, x1, y1], fill=(0, 0, 0, alpha))

    vig = vig.filter(ImageFilter.GaussianBlur(radius=50))
    result = Image.alpha_composite(img.convert("RGBA"), vig)
    return result.convert("RGB")


# ── glowing text ──────────────────────────────────────────────────

def _add_glowing_text(
    img: Image.Image, text: str, glow_rgb: tuple[int, int, int]
) -> None:
    """Draw centred text with a coloured glow halo behind it."""
    W, H = img.size
    font = _get_font(config.FONT_SIZE)
    wrapped = _wrap_text(text, font, W - 160)

    # Measure text block
    tmp = ImageDraw.Draw(img)
    bbox = tmp.multiline_textbbox((0, 0), wrapped, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) / 2
    y = (H - th) / 2

    # 1. Glow halo — coloured text blurred on transparent layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.multiline_text(
        (x, y), wrapped, font=font,
        fill=glow_rgb + (180,), align="center",
    )
    glow = glow.filter(ImageFilter.GaussianBlur(radius=20))
    composited = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    img.paste(composited)

    # 2. Black outline for contrast
    draw = ImageDraw.Draw(img)
    ow = config.OUTLINE_WIDTH
    for dx in (-ow, 0, ow):
        for dy in (-ow, 0, ow):
            if dx == 0 and dy == 0:
                continue
            draw.multiline_text(
                (x + dx, y + dy), wrapped, font=font,
                fill=config.OUTLINE_COLOR, align="center",
            )

    # 3. White foreground text
    draw.multiline_text(
        (x, y), wrapped, font=font,
        fill=config.TEXT_COLOR, align="center",
    )


# ═══════════════════════════════════════════════════════════════════
#  BACKGROUND MUSIC — synthetic beat generator
# ═══════════════════════════════════════════════════════════════════

def _generate_background_music(duration: float) -> str:
    """
    Create an energetic royalty-free beat using pure numpy synthesis.

    Components:
      • Kick drum  (beats 1 & 3)
      • Snare      (beats 2 & 4)
      • Hi-hat     (8th notes)
      • Sub bass   (continuous low hum)
      • Synth pad  (Am chord shimmer)

    Returns:
        Path to a temporary WAV file.
    """
    sr = 44100
    bpm = config.AUDIO_BPM
    n = int(sr * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    beat_s = 60.0 / bpm  # seconds per beat

    # ── Kick drum ─────────────────────────────────────────────────
    kick = np.zeros(n)
    for b in range(int(duration / beat_s)):
        if b % 4 in (0, 2):
            s = int(b * beat_s * sr)
            ln = min(int(0.15 * sr), n - s)
            if ln > 0:
                kt = np.arange(ln) / sr
                kick[s : s + ln] += np.sin(2 * np.pi * 55 * kt) * np.exp(-kt * 25)

    # ── Snare ─────────────────────────────────────────────────────
    snare = np.zeros(n)
    for b in range(int(duration / beat_s)):
        if b % 4 in (1, 3):
            s = int(b * beat_s * sr)
            ln = min(int(0.10 * sr), n - s)
            if ln > 0:
                st = np.arange(ln) / sr
                snare[s : s + ln] += np.random.randn(ln) * np.exp(-st * 40) * 0.4

    # ── Hi-hat (8th notes) ────────────────────────────────────────
    hihat = np.zeros(n)
    eighth = beat_s / 2
    for h in range(int(duration / eighth)):
        s = int(h * eighth * sr)
        ln = min(int(0.03 * sr), n - s)
        if ln > 0:
            hihat[s : s + ln] += (
                np.random.randn(ln) * np.exp(-np.arange(ln) / (0.01 * sr)) * 0.15
            )

    # ── Sub bass ──────────────────────────────────────────────────
    sub = 0.15 * np.sin(2 * np.pi * 40 * t + np.sin(2 * np.pi * 0.25 * t) * 3)

    # ── Synth pad (Am chord: A3 C4 E4) ───────────────────────────
    pad = np.zeros(n)
    for freq in (220.0, 261.63, 329.63):
        pad += 0.05 * np.sin(
            2 * np.pi * freq * t + np.sin(2 * np.pi * 1.5 * t) * 0.5
        )

    # ── Mix ───────────────────────────────────────────────────────
    audio = kick * 0.50 + snare * 0.35 + hihat * 0.25 + sub + pad

    # ── Fade in / out ─────────────────────────────────────────────
    fade = int(0.5 * sr)
    if n > 2 * fade:
        audio[:fade] *= np.linspace(0, 1, fade)
        audio[-fade:] *= np.linspace(1, 0, fade)

    # ── Normalise ─────────────────────────────────────────────────
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * config.AUDIO_VOLUME

    # ── Save WAV ──────────────────────────────────────────────────
    wav_path = os.path.join(tempfile.gettempdir(), "trend_shorts_beat.wav")
    audio_int = (audio * 32767).astype(np.int16)
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int.tobytes())

    return wav_path


# ═══════════════════════════════════════════════════════════════════
#  TEXT HELPERS
# ═══════════════════════════════════════════════════════════════════

def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
    """Greedy word-wrap to fit within max_w pixels."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        test = f"{cur} {word}".strip()
        if font.getbbox(test)[2] - font.getbbox(test)[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Load a bold font — tries common OS paths, then Pillow default."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for path in (
        os.path.join(base_dir, "fonts", "NotoSansDevanagari-Bold.ttf"),
        "C:/Windows/Fonts/NirmalaB.ttf",
        "C:/Windows/Fonts/mangalbd.ttf",
        "C:/Windows/Fonts/mangal.ttf",
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


# ═══════════════════════════════════════════════════════════════════
#  CODEC SELECTION
# ═══════════════════════════════════════════════════════════════════

def _codec_params() -> tuple[str, list[str]]:
    """(codec, ffmpeg_params) — NVENC GPU or libx264 CPU."""
    if config.CUDA_AVAILABLE:
        print("⚡ CUDA detected — using GPU-accelerated encoding (h264_nvenc)")
        return "h264_nvenc", ["-preset", "fast", "-pix_fmt", "yuv420p"]
    print("🖥  No CUDA GPU — using CPU encoding (libx264)")
    return "libx264", ["-preset", "ultrafast", "-pix_fmt", "yuv420p"]
