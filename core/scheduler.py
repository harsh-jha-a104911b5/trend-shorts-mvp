"""
Task Scheduler.
"""

from __future__ import annotations
import time
import schedule
import config
from core.pipeline import run_pipeline
from core.logger import get_logger

log = get_logger("Scheduler")


def run_scheduler():
    if config.SCHEDULE_ENABLED:
        log.info(
            f"Pipeline active - Repeating every {config.SCHEDULE_INTERVAL_HOURS} hours."
        )
        run_pipeline()  # Initial run
        schedule.every(config.SCHEDULE_INTERVAL_HOURS).hours.do(run_pipeline)
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        log.info("Running once (scheduler disabled in config).")
        run_pipeline()
