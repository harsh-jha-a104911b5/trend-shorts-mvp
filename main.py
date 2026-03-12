"""
Trend Shorts MVP — main entry point.

Fully automated pipeline:
  1. Fetch a trending keyword from Google Trends (India).
  2. Generate a short video script.
  3. Render a 1080×1920 YouTube Shorts video.
  4. Save the video to /output.
"""

import sys
import config
from trends import get_trends
from script_generator import generate_script
from video_generator import generate_video


def main() -> None:
    print("=" * 50)
    print("  🎬  TREND SHORTS MVP")
    print("=" * 50)
    print(f"  Device : {config.DEVICE.upper()}")
    print(f"  CUDA   : {'✅ Available' if config.CUDA_AVAILABLE else '❌ Not available'}")
    print(f"  Mode   : {config.SCRIPT_MODE}")
    print("=" * 50)

    # ── Step 1: Fetch trends ──────────────────────────────────────
    print("\n📡 Fetching trends...")
    trends = get_trends(count=config.TRENDS_COUNT)
    if not trends:
        print("❌ No trends found. Exiting.")
        sys.exit(1)

    keyword = trends[0]
    print(f"🔥 Trend detected: {keyword}")

    # ── Step 2: Generate script ───────────────────────────────────
    print("\n✍️  Generating script...")
    script = generate_script(keyword)
    print(f"📝 Script ({len(script['scenes'])} scenes):")
    for i, scene in enumerate(script["scenes"], 1):
        print(f"   Scene {i}: {scene}")

    # ── Step 3: Generate video ────────────────────────────────────
    print("\n🎞️  Generating video...")
    output_path = generate_video(script)

    # ── Done ──────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print(f"  ✅ Video saved: {output_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
