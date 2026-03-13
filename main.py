"""
Autonomous AI Discovery Engine with Multi-Agent Debate Simulation.
"""

from __future__ import annotations
import time
import json
import os
import sys
import traceback
import schedule
import random
from datetime import datetime

import config
from trends import get_rich_trends
from script_generator import generate_scripts_from_fact
from video_generator import generate_video
from youtube_uploader import upload_video
from telegram_poster import post_to_telegram

# ─── MEMORY SYSTEM ───────────────────────────────────────────────
def load_memory() -> set:
    """Retrieve published insights from long-term memory."""
    if os.path.exists(config.PROCESSED_TRENDS_FILE):
        with open(config.PROCESSED_TRENDS_FILE, "r") as f:
            return set(json.load(f).get("processed", []))
    return set()

def save_memory(link_id: str):
    """Store published insight to prevent duplicates."""
    processed = list(load_memory())
    if link_id not in processed:
        processed.append(link_id)
        with open(config.PROCESSED_TRENDS_FILE, "w", encoding="utf-8") as f:
            json.dump({"processed": processed}, f)

# ─── RESEARCH AGENT ──────────────────────────────────────────────
def research_agent(memory: set) -> list[dict]:
    """Fetch raw candidate discoveries and filter against memory."""
    print("🔬 [Research Agent] Fetching candidate discoveries...")
    raw_discoveries = get_rich_trends(count=15)
    filtered = []
    for disc in raw_discoveries:
        if disc["link"] not in memory:
            filtered.append(disc)
    
    selected = filtered[:config.MAX_TRENDS_PER_RUN]
    print(f"🎯 [Research Agent] Isolated {len(selected)} completely new topics for debate.")
    return selected

# ─── PUBLISHING AGENT ────────────────────────────────────────────
def publishing_agent(video_path: str, script: dict) -> bool:
    """Handles end-to-end distribution of content."""
    success = False
    video_url = None
    
    if config.YOUTUBE_UPLOAD_ENABLED:
        print("📤 [Publishing Agent] Uploading to YouTube...")
        video_url = upload_video(
            video_path, script["title"], 
            script["description"], script["tags"]
        )
        if video_url: success = True
        
    if config.TELEGRAM_ENABLED and video_url:
        print("📨 [Publishing Agent] Posting to Telegram Archive...")
        post_to_telegram(script["title"], video_url, script["teaser"])
        success = True
        
    return success

# ─── REFLECTION AGENT ────────────────────────────────────────────
def reflection_agent(published_count: int):
    """Analyzes recent performance and logs engagement strategy."""
    print(f"\n🧠 [Reflection Agent] Analyzing run performance...")
    if published_count == 0:
        print("   ⚠️ Engagement Warning: No new content published. Consider broadening search parameters.")
    else:
        print(f"   📈 Strong Engagement Metric: Successfully pushed {published_count} high-quality insights.")
        print("   💡 Strategy Adjustment: Continuing to prioritize high-novelty hooks based on algorithmic response.")

# ─── CORE PIPELINE ───────────────────────────────────────────────
def run_pipeline():
    print(f"\n============================================================")
    print(f"🚀 {datetime.now().strftime('%H:%M:%S')} - Starting Multi-Agent AI Discovery Pipeline...")
    print(f"============================================================")
    
    memory = load_memory()
    published_count = 0
    
    try:
        # 1. Research Agent
        targets = research_agent(memory)

        for fact in targets:
            print(f"\n────────────────────────────────────────────────────────────")
            print(f"🔎 Evaluating Topic: {fact['title'][:60]}...")
            
            # 2. Extraction, Debate, Consensus, Content Agents
            #    (Handled internally by script_generator)
            scripts = generate_scripts_from_fact(fact)
            
            for script in scripts:
                print(f"\n🎬 [Content Agent] Structuring Video Hook...")
                try:
                    # 3. Video Generation
                    video_path = generate_video(script)
                    
                    # 4. Publishing Agent
                    if publishing_agent(video_path, script):
                        published_count += 1
                        
                except Exception as e:
                    print(f"❌ [System] Render/Publish failed: {e}")
                    traceback.print_exc()

            # 5. Commit to Memory (even if failed, to avoid endless retries on broken papers)
            save_memory(fact["link"])

        # 6. Reflection Agent
        reflection_agent(published_count)

    except Exception as e:
        print(f"🛑 [System] Critical Pipeline Error: {e}")
        traceback.print_exc()
        time.sleep(60) # Global Failsafe Wait

def main():
    if config.SCHEDULE_ENABLED:
        print(f"⏰ Pipeline active - Repeating every {config.SCHEDULE_INTERVAL_HOURS} hours.")
        run_pipeline() # Initial run
        schedule.every(config.SCHEDULE_INTERVAL_HOURS).hours.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_pipeline()

if __name__ == "__main__":
    main()
