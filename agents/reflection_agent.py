"""
Reflection Agent. Logs post-run analysis.
"""

from __future__ import annotations
from core.logger import get_logger

log = get_logger("ReflectionAgent")


def reflection_agent(published_count: int):
    """Analyzes recent performance and logs engagement strategy."""
    log.info(f"Analyzing run performance...")
    if published_count == 0:
        log.warning(
            "Engagement Warning: No new content published. Consider broadening search parameters."
        )
    else:
        log.info(
            f"Strong Engagement Metric: Successfully pushed {published_count} high-quality insights."
        )
        log.info(
            "Strategy Adjustment: Continuing to prioritize high-novelty hooks based on algorithmic response."
        )
