"""
Extraction Agent.
"""

from __future__ import annotations
import re
from core.logger import get_logger

log = get_logger("ExtractionAgent")


def extraction_agent(fact_dict: dict) -> str:
    """Extracts a single concise insight from the paper."""
    title = fact_dict["title"]
    summary = fact_dict["description"]
    # Get first sentence
    sentences = re.split(r"(?<=[.!?]) +", summary)
    core = sentences[0] if sentences else title
    insight = f"{title}: {core}"
    log.info(f"Extracted insight: {insight[:60]}...")
    return insight
