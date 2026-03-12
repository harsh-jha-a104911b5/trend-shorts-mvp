"""
Trend Shorts — Autonomous Content Pipeline.

Fully automated:
  1. Fetch trending keywords from Google Trends (India).
  2. Filter keywords to tech-relevant topics only.
  3. Generate scripts with title/description/tags.
  4. Render premium 1080×1920 YouTube Shorts videos.
  5. Upload each video to YouTube.
  6. Post video links to Telegram.
  7. Optionally loop on a schedule (every N hours).
"""

from __future__ import annotations

import sys
import time
from datetime import datetime

import schedule

import config
from trends import get_trends
from script_generator import generate_script
from video_generator import generate_video
from youtube_uploader import upload_video
from telegram_poster import post_to_telegram


# ═══════════════════════════════════════════════════════════════════
#  TREND FILTERING
# ═══════════════════════════════════════════════════════════════════

def filter_trends(keywords: list[str]) -> list[str]:
    """
    Keep only tech-relevant trends and remove blocked categories.

    A keyword passes if:
      • It does NOT match any BLOCKED keyword, AND
      • It matches at least one ALLOWED keyword, OR the allowed list is empty.

    Falls back to returning all keywords if filtering removes everything
    (so the pipeline never starves).
    """
    filtered = []
    for kw in keywords:
        kw_lower = kw.lower()

        # Block check
        if any(b in kw_lower for b in config.BLOCKED_KEYWORDS):
            print(f"   🚫 Blocked: {kw}")
            continue

        # Allow check
        if any(a in kw_lower for a in config.ALLOWED_KEYWORDS):
            filtered.append(kw)
            print(f"   ✅ Allowed: {kw}")
        else:
            print(f"   ⏭️  Skipped (no match): {kw}")

    if not filtered:
        # Fallback: use first few unblocked trends so the pipeline still runs
        unblocked = [
            kw for kw in keywords
            if not any(b in kw.lower() for b in config.BLOCKED_KEYWORDS)
        ]
        fallback = unblocked[:2] or keywords[:1]
        print(f"   ⚠  No allowed trends found — using fallback: {fallback}")
        return fallback

    return filtered


# ═══════════════════════════════════════════════════════════════════
#  SINGLE PIPELINE RUN
# ═══════════════════════════════════════════════════════════════════

def run_pipeline() -> None:
    """Execute one full cycle: fetch → filter → generate → upload → post."""
    start = time.time()
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 60)
    print(f"  🎬  TREND SHORTS — Autonomous Content Pipeline")
    print(f"  🕐  {run_ts}")
    print("=" * 60)
    print(f"  Device : {config.DEVICE.upper()}")
    print(f"  CUDA   : {'✅ Available' if config.CUDA_AVAILABLE else '❌ Not available'}")
    print(f"  Mode   : {config.SCRIPT_MODE}")
    print(f"  Upload : {'✅ YouTube' if config.YOUTUBE_UPLOAD_ENABLED else '❌ Disabled'}")
    print(f"  Notify : {'✅ Telegram' if config.TELEGRAM_ENABLED else '❌ Disabled'}")
    print("=" * 60)

    # ── Step 1: Fetch trends ──────────────────────────────────────
    print("\n📡 Fetching trends...")
    raw_trends = get_trends(count=config.TRENDS_COUNT)
    if not raw_trends:
        print("❌ No trends found. Skipping this run.")
        return

    # ── Step 2: Filter trends ─────────────────────────────────────
    print(f"\n🔍 Filtering {len(raw_trends)} trends...")
    trends = filter_trends(raw_trends)
    trends = trends[: config.MAX_VIDEOS_PER_RUN]
    print(f"\n🎯 {len(trends)} trend(s) selected for video generation")

    # ── Step 3–5: Process each trend ──────────────────────────────
    results = []

    for idx, keyword in enumerate(trends, 1):
        print(f"\n{'─' * 60}")
        print(f"  📌 [{idx}/{len(trends)}] {keyword}")
        print(f"{'─' * 60}")

        # Generate script
        print("  ✍️  Generating script...")
        script = generate_script(keyword)
        print(f"  📝 Title: {script['title']}")
        for i, scene in enumerate(script["scenes"], 1):
            print(f"     Scene {i}: {scene}")

        # Generate video
        print("  🎞️  Generating video...")
        video_path = generate_video(script)
        print(f"  💾 Saved: {video_path}")

        # Upload to YouTube
        video_url = None
        if config.YOUTUBE_UPLOAD_ENABLED:
            print("  📤 Uploading to YouTube...")
            video_url = upload_video(
                video_path=video_path,
                title=script["title"],
                description=script["description"],
                tags=script["tags"],
                privacy=config.YOUTUBE_PRIVACY,
            )

        # Post to Telegram
        if config.TELEGRAM_ENABLED and video_url:
            print("  📨 Posting to Telegram...")
            post_to_telegram(title=script["title"], video_url=video_url)

        results.append({
            "keyword": keyword,
            "video": video_path,
            "url": video_url,
        })

    # ── Summary ───────────────────────────────────────────────────
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"  ✅  PIPELINE COMPLETE — {len(results)} video(s) in {elapsed:.1f}s")
    print(f"{'=' * 60}")
    for r in results:
        status = r["url"] or "local only"
        print(f"  • {r['keyword']}: {status}")
    print("=" * 60)


# ═══════════════════════════════════════════════════════════════════
#  SCHEDULING
# ═══════════════════════════════════════════════════════════════════

def run_with_schedule() -> None:
    """Run the pipeline on a recurring schedule."""
    hours = config.SCHEDULE_INTERVAL_HOURS
    print(f"\n⏰ Scheduler active — running every {hours} hour(s)")
    print("   Press Ctrl+C to stop.\n")

    # Run immediately on start
    run_pipeline()

    # Schedule recurring runs
    schedule.every(hours).hours.do(run_pipeline)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # check every 30s
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user.")


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    """Entry point — run once or start scheduler based on config."""
    if config.SCHEDULE_ENABLED:
        run_with_schedule()
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
