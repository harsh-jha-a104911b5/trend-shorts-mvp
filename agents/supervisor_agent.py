"""
Supervisor Agent. Handles global failsafes for the AI Discovery Pipeline.
"""

from __future__ import annotations
import traceback
import time
from core.scheduler import run_scheduler
from core.logger import get_logger

log = get_logger("Supervisor")


def start_pipeline():
    """Starts the discovery engine with global failsafe catch."""
    try:
        log.info("Supervisor Agent initializing Multi-Agent AI Discovery Engine...")
        run_scheduler()
    except Exception as e:
        log.error(f"FATAL: Supervisor Agent caught unhandled exception: {e}")
        traceback.print_exc()
        time.sleep(60)
        # Try a cautious restart via recursion (with limits in a real system)
        start_pipeline()
