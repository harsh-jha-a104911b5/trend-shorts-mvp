"""
Autonomous Growth Engine: 5 Trends * 4 Angles = Infinity.
"""

import time
import json
import os
import sys
import traceback
import schedule
from datetime import datetime

import config
from trends import get_trends
from script_generator import generate_multi_angle_scripts
from video_generator import generate_video
from youtube_uploader import upload_video
from telegram_poster import post_to_telegram

def load_cache():
    if os.path.exists(config.PROCESSED_TRENDS_FILE):
        with open(config.PROCESSED_TRENDS_FILE, "r") as f:
            return set(json.load(f).get("processed", []))
    return set()

def save_cache(keyword):
    processed = list(load_cache())
    if keyword not in processed:
        processed.append(keyword)
        with open(config.PROCESSED_TRENDS_FILE, "w") as f:
            json.dump({"processed": processed}, f)

def filter_trends(raw_trends, cache):
    filtered = []
    for kw in raw_trends:
        kw_low = kw.lower()
        if kw in cache: continue
        if any(b in kw_low for b in config.BLOCKED_KEYWORDS): continue
        if any(a in kw_low for a in config.ALLOWED_KEYWORDS):
            filtered.append(kw)
    
    # Fallback to allow progress if filtering is too strict
    if not filtered:
        unprocessed = [k for k in raw_trends if k not in cache]
        filtered = unprocessed[:2]
    
    return filtered[:config.MAX_TRENDS_PER_RUN]

def run_pipeline():
    print(f"\n🚀 {datetime.now().strftime('%H:%M:%S')} - Starting Growth Cycle...")
    cache = load_cache()
    
    try:
        trends = get_trends(count=15)
        targets = filter_trends(trends, cache)
        print(f"🎯 Selected {len(targets)} trends to process.")

        for keyword in targets:
            print(f"\n🔥 Processing Trend: {keyword}")
            # Generate 4 scripts (angles) per trend
            scripts = generate_multi_angle_scripts(keyword)
            
            for script in scripts:
                print(f"🎬 Angle: {script['angle']} - Rendering...")
                try:
                    video_path = generate_video(script)
                    
                    video_url = None
                    if config.YOUTUBE_UPLOAD_ENABLED:
                        print("📤 Uploading...")
                        video_url = upload_video(
                            video_path, script["title"], 
                            script["description"], script["tags"]
                        )
                    
                    if config.TELEGRAM_ENABLED and video_url:
                        print("📨 Notifying Telegram...")
                        # Teaser includes curiosity hook
                        post_to_telegram(script["title"], video_url, script["teaser"])
                    
                except Exception as e:
                    print(f"❌ Angle failed: {e}")
                    traceback.print_exc()

            # Mark trend as done only if we tried it
            save_cache(keyword)

    except Exception as e:
        print(f"🛑 Critical Pipeline Error: {e}")
        traceback.print_exc()
        time.sleep(60) # Wait before retry

def main():
    if config.SCHEDULE_ENABLED:
        print(f"⏰ Scheduler active - Every {config.SCHEDULE_INTERVAL_HOURS} hours.")
        run_pipeline() # Initial run
        schedule.every(config.SCHEDULE_INTERVAL_HOURS).hours.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_pipeline()

if __name__ == "__main__":
    main()
