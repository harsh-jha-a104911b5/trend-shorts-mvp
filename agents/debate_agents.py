"""
Multi-Agent debate simulation.
"""

from __future__ import annotations
from core.logger import get_logger

log = get_logger("DebateAgents")


class DebateNetwork:
    @staticmethod
    def debate(insight: str, fact_dict: dict) -> dict:
        """
        Simulates a 3-agent debate.
        Round 1: Discoverer proposes.
        Round 2: Skeptic critiques, Explainer clarifies.
        Round 3: Revised consensus.
        """
        log.info(f"[Discoverer] Proposing insight: '{insight[:80]}...'")

        summary = fact_dict.get("description", "").lower()

        # skeptic logic
        if any(
            hedge in summary
            for hedge in ["suggests", "might", "potentially", "early stage", "propose"]
        ):
            skeptic_critique = (
                "The claim is heavily hedged. This might not be production-ready yet."
            )
        elif "dataset" in summary or "benchmark" in summary:
            skeptic_critique = "This focuses on an evaluation dataset, not a fundamentally new capability."
        else:
            skeptic_critique = "This sounds impressive, but does it generalize beyond the specific test environment?"

        log.info(f"[Skeptic] Critique: {skeptic_critique}")

        # explainer logic
        if "first" in summary or "novel" in summary or "state-of-the-art" in summary:
            explainer_clarification = "The authors explicitly demonstrate state-of-the-art results, differentiating it clearly from prior work."
        else:
            explainer_clarification = "The underlying architecture provides measurable improvements worth highlighting."

        log.info(f"[Explainer] Clarification: {explainer_clarification}")

        # Round 3
        revised_statement = f"While its immediate scale may be bounded, the research introduces a highly novel paradigm."
        log.info(f"[Discoverer] Revised: {revised_statement}")

        return {
            "original_insight": insight,
            "critique": skeptic_critique,
            "clarification": explainer_clarification,
            "revised": revised_statement,
        }
