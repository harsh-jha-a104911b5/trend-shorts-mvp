"""
Trend Shorts — Autonomous Content Pipeline.

Fully automated:
  1. Fetch trending keywords from Google Trends (India).
  2. Filter keywords (block non-tech, prevent duplicates).
  3. Generate scripts with title/description/tags.
  4. Render premium 1080×1920 YouTube Shorts videos.
  5. Upload each video to YouTube.
  6. Post video links to Telegram.
  7. Loop indefinitely on a schedule (catch all exceptions).
"""

from __future__ import annotations

import sys
import time
import json
import os
from datetime import datetime

import schedule

import config
from trends import get_trends
from script_generator import generate_script
from video_generator import generate_video
from youtube_uploader import upload_video
from telegram_poster import post_to_telegram


# ═══════════════════════════════════════════════════════════════════
#  DUPLICATE CACHE
# ═══════════════════════════════════════════════════════════════════

def load_processed_trends() -> set[str]:
    """Load the cache of previously processed trends."""
    if os.path.exists(config.PROCESSED_TRENDS_FILE):
        try:
            with open(config.PROCESSED_TRENDS_FILE, "r") as f:
                data = json.load(f)
                return set(data.get("processed", []))
        except Exception as e:
            print(f"   ⚠  Failed to load processed trends: {e}")
    return set()


def save_processed_trend(keyword: str) -> None:
    """Save a successfully processed trend to the cache."""
    processed = list(load_processed_trends())
    if keyword not in processed:
        processed.append(keyword)
        # Keep only the last 500 to prevent infinite growth
        processed = processed[-500:]
        try:
            with open(config.PROCESSED_TRENDS_FILE, "w") as f:
                json.dump({"processed": processed}, f, indent=4)
        except Exception as e:
            print(f"   ⚠  Failed to save processed trend: {e}")


# ═══════════════════════════════════════════════════════════════════
#  TREND FILTERING
# ═══════════════════════════════════════════════════════════════════

def filter_trends(keywords: list[str], processed: set[str]) -> list[str]:
    """
    Keep only new, tech-relevant trends.
    """
    filtered = []
    
    for kw in keywords:
        kw_lower = kw.lower()

        # Duplicate check
        if kw in processed:
            print(f"   ⏭️  Skipped (already processed): {kw}")
            continue

        # Block check
        if any(b in kw_lower for b in config.BLOCKED_KEYWORDS):
            print(f"   🚫 Blocked (category): {kw}")
            continue

        # Allow check
        if any(a in kw_lower for a in config.ALLOWED_KEYWORDS):
            filtered.append(kw)
            print(f"   ✅ Allowed: {kw}")
        else:
            print(f"   ⏭️  Skipped (no match): {kw}")

    if not filtered:
        # Fallback: use first few unblocked and unprocessed trends
        unblocked = [
            kw for kw in keywords
            if kw not in processed and not any(b in kw.lower() for b in config.BLOCKED_KEYWORDS)
        ]
        fallback = unblocked[:2]
        if fallback:
            print(f"   ⚠  No allowed trends found — using fallback: {fallback}")
            return fallback

    return filtered


# ═══════════════════════════════════════════════════════════════════
#  SINGLE PIPELINE RUN
# ═══════════════════════════════════════════════════════════════════

def run_pipeline() -> None:
    """Execute one full cycle autonomously."""
    start = time.time()
    run_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n" + "=" * 60)
    print(f"  🎬  TREND SHORTS — Autonomous Content Engine")
    print(f"  🕐  {run_ts}")
    print("=" * 60)
    print(f"  Device : {config.DEVICE.upper()}")
    print(f"  CUDA   : {'✅ Available' if config.CUDA_AVAILABLE else '❌ Not available'}")
    print(f"  Mode   : {config.SCRIPT_MODE}")
    print("=" * 60)

    try:
        # ── Step 1: Fetch trends ──────────────────────────────────────
        print("\n📡 Fetching trends...")
        raw_trends = get_trends(count=config.TRENDS_COUNT)
        if not raw_trends:
            print("❌ No trends found. Skipping this run.")
            return

        # ── Step 2: Load cache & filter ───────────────────────────────
        processed_cache = load_processed_trends()
        print(f"\n🔍 Filtering {len(raw_trends)} trends...")
        trends = filter_trends(raw_trends, processed_cache)
        trends = trends[: config.MAX_VIDEOS_PER_RUN]
        print(f"\n🎯 {len(trends)} trend(s) pass filtering")

        # ── Step 3–5: Process each trend safely ───────────────────────
        results = []

        for idx, keyword in enumerate(trends, 1):
            print(f"\n{'─' * 60}")
            print(f"  📌 [{idx}/{len(trends)}] {keyword}")
            print(f"{'─' * 60}")

            try:
                # Generate script
                print("  ✍️  Generating script...")
                script = generate_script(keyword)
                
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
                    if video_url:
                        print(f"  ✅ Upload successful: {video_url}")

                # Post to Telegram
                if config.TELEGRAM_ENABLED and video_url:
                    print("  📨 Posting to Telegram...")
                    post_to_telegram(title=script["title"], video_url=video_url)

                # Save to cache so we don't process it again next run
                save_processed_trend(keyword)

                results.append({
                    "keyword": keyword,
                    "status": "Success",
                    "url": video_url or "Local only"
                })

            except Exception as e:
                # Catch-all to prevent one bad video from crashing the pipeline
                print(f"  ❌ Error processing '{keyword}': {e}")
                results.append({"keyword": keyword, "status": f"Failed: {e}", "url": "N/A"})

        # ── Summary ───────────────────────────────────────────────────
        elapsed = time.time() - start
        print(f"\n{'=' * 60}")
        print(f"  ✅  PIPELINE COMPLETED in {elapsed:.1f}s")
        print(f"{'=' * 60}")
        if results:
            for r in results:
                print(f"  • {r['keyword']} | {r['status']} | {r['url']}")
        else:
            print("  • No new videos generated this run.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ CRITICAL PIPELINE ERROR: {e}")
        print("Pipeline is continuing to next schedule.")


# ═══════════════════════════════════════════════════════════════════
#  SCHEDULING (INFINITE LOOP)
# ═══════════════════════════════════════════════════════════════════

def run_with_schedule() -> None:
    """Run the pipeline on a recurring schedule independently."""
    hours = config.SCHEDULE_INTERVAL_HOURS
    print(f"\n⏰ Autonomous Scheduler Active — running every {hours} hour(s)")
    print("   System will run indefinitely. Press Ctrl+C to stop.\n")

    # Run immediately on start
    run_pipeline()

    # Schedule recurring runs
    schedule.every(hours).hours.do(run_pipeline)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # check every minute
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user.")


# ═══════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    """Entry point — starts the autonomous engine."""
    if config.SCHEDULE_ENABLED:
        run_with_schedule()
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
