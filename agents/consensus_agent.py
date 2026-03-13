"""
Consensus Agent. Scores the debated insight.
"""

from __future__ import annotations
from core.logger import get_logger

log = get_logger("ConsensusAgent")


def consensus_agent(debate_log: dict, fact_dict: dict) -> int:
    """
    Score the debate 0-10 on accuracy, novelty, and educational value.
    Reject low quality.
    """
    score = 5
    summary = fact_dict.get("description", "").lower()
    title = fact_dict.get("title", "").lower()

    # Novelty value
    if "novel" in summary or "breakthrough" in title or "first time" in summary:
        score += 2

    # Educational Value
    if "tutorial" not in title and "survey" not in title:
        score += 1
        if "architecture" in summary or "model" in summary:
            score += 1

    # Accuracy downgrade from Skeptic
    if "dataset" in debate_log.get("critique", "") or "hedged" in debate_log.get(
        "critique", ""
    ):
        score -= 2

    log.info(f"[Consensus] Final Score: {score}/10")
    return max(0, min(10, score))
