"""
Autonomous AI Knowledge Discovery & Translation Engine
"""

import time
import json
import os
import sys
import traceback
import schedule
from datetime import datetime

import config
from trends import get_rich_trends
from script_generator import generate_scripts_from_fact
from video_generator import generate_video
from youtube_uploader import upload_video
from telegram_poster import post_to_telegram

def load_cache():
    if os.path.exists(config.PROCESSED_TRENDS_FILE):
        with open(config.PROCESSED_TRENDS_FILE, "r") as f:
            return set(json.load(f).get("processed", []))
    return set()

def save_cache(link_id):
    processed = list(load_cache())
    if link_id not in processed:
        processed.append(link_id)
        with open(config.PROCESSED_TRENDS_FILE, "w") as f:
            json.dump({"processed": processed}, f)

def filter_discoveries(raw_discoveries, cache):
    filtered = []
    
    for disc in raw_discoveries:
        # Avoid processing same arXiv paper twice by hashing the link
        link_id = disc["link"]
        if link_id in cache: 
            continue
            
        # Basic filter constraint (if needed)
        filtered.append(disc)
        
    return filtered[:config.MAX_TRENDS_PER_RUN]

def run_pipeline():
    print(f"\n🚀 {datetime.now().strftime('%H:%M:%S')} - Starting AI Discovery Engine...")
    cache = load_cache()
    
    try:
        # fetch rich dicts from Agent
        discoveries = get_rich_trends(count=15)
        targets = filter_discoveries(discoveries, cache)
        
        print(f"🎯 Selected {len(targets)} new AI papers/repos to process.")

        for fact in targets:
            print(f"\n🧠 Processing Discovery: {fact['title'][:50]}...")
            
            # Uniqueness & Extraction pass
            scripts = generate_scripts_from_fact(fact)
            
            for script in scripts:
                print(f"🎬 Knowledge Render - Generating Video...")
                try:
                    video_path = generate_video(script)
                    
                    video_url = None
                    if config.YOUTUBE_UPLOAD_ENABLED:
                        print("📤 Uploading Knowledge Short...")
                        video_url = upload_video(
                            video_path, script["title"], 
                            script["description"], script["tags"]
                        )
                    
                    if config.TELEGRAM_ENABLED and video_url:
                        print("📨 Archiving to Telegram Knowledge Base...")
                        
                        # Pack the detailed deep archive summary into Telegram with link attached 
                        # This matches the user's specific Telegram Post format requirements 
                        post_to_telegram(script["title"], video_url, script["teaser"])
                    
                except Exception as e:
                    print(f"❌ Render failed: {e}")
                    traceback.print_exc()

            # Mark processed by saving link to cache
            save_cache(fact["link"])

    except Exception as e:
        print(f"🛑 Critical Pipeline Error: {e}")
        traceback.print_exc()
        time.sleep(60) # Global Failsafe Wait

def main():
    if config.SCHEDULE_ENABLED:
        print(f"⏰ Knowledge Engine active - Every {config.SCHEDULE_INTERVAL_HOURS} hours.")
        run_pipeline() # Initial run
        schedule.every(config.SCHEDULE_INTERVAL_HOURS).hours.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_pipeline()

if __name__ == "__main__":
    main()
