"""
Core Pipeline Orchestration.
"""

from __future__ import annotations
import time
import traceback
from datetime import datetime

import config
from core.logger import get_logger
from core.memory import load_memory, save_memory, log_metrics
from agents.research_agent import research_run
from agents.extraction_agent import extraction_agent
from agents.debate_agents import DebateNetwork
from agents.consensus_agent import consensus_agent
from agents.content_agent import content_agent
from agents.reflection_agent import reflection_agent
from services.video_service import generate_video
from services.youtube_service import upload_video
from services.telegram_service import post_to_telegram

log = get_logger("Pipeline")


def publishing_agent(video_path: str, script: dict) -> bool:
    """Handles end-to-end distribution of content."""
    success = False
    video_url = None

    if config.YOUTUBE_UPLOAD_ENABLED:
        log.info("Uploading to YouTube...")
        video_url = upload_video(
            video_path, script["title"], script["description"], script["tags"]
        )
        if video_url:
            success = True

    if config.TELEGRAM_ENABLED and video_url:
        log.info("Posting to Telegram Archive...")
        post_to_telegram(script["title"], video_url, script["teaser"])
        success = True

    return success


def run_pipeline():
    log.info("=" * 60)
    log.info(f"Starting Multi-Agent AI Discovery Pipeline...")
    log.info("=" * 60)

    start_time = time.time()
    memory = load_memory()
    published_count = 0
    errors_count = 0

    try:
        targets = research_run(memory)
        for fact in targets:
            log.info("-" * 60)
            log.info(f"Evaluating Topic: {fact['title'][:60]}...")

            try:
                insight = extraction_agent(fact)
                debate_log = DebateNetwork.debate(insight, fact)
                score = consensus_agent(debate_log, fact)

                if score < 4:
                    log.warning("Consensus Reject: Quality threshold not met.")
                    save_memory(
                        fact["link"],
                        fact.get("title", ""),
                        "rejected",
                        datetime.now().isoformat(),
                    )
                    continue

                log.info("Consensus Approve: Insight validated for publishing.")
                script = content_agent(fact, debate_log)

                log.info("Structuring Video Hook...")
                video_path = generate_video(script)

                if publishing_agent(video_path, script):
                    published_count += 1

                # Save to active memory
                save_memory(
                    fact["link"],
                    fact.get("title", ""),
                    "published",
                    datetime.now().isoformat(),
                )

            except Exception as e:
                errors_count += 1
                log.error(f"Render/Publish failed for {fact['link']}: {e}")
                traceback.print_exc()

            # Basic fallback save memory so it doesn't loop forever
            save_memory(
                fact["link"], fact.get("title", ""), "error", datetime.now().isoformat()
            )

        reflection_agent(published_count)

    except Exception as e:
        errors_count += 1
        log.error(f"Critical Pipeline Error: {e}")
        traceback.print_exc()
        time.sleep(60)

    # Log metrics
    run_time = time.time() - start_time
    log_metrics(published_count, errors_count, run_time)
