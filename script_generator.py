"""
Legacy script_generator wrapper. Core logic moved to `agents/` and `core/`.
"""

from agents.extraction_agent import extraction_agent
from agents.debate_agents import DebateNetwork
from agents.consensus_agent import consensus_agent
from agents.content_agent import content_agent


def generate_scripts_from_fact(fact_dict: dict) -> list[dict]:
    insight = extraction_agent(fact_dict)
    debate_log = DebateNetwork.debate(insight, fact_dict)
    score = consensus_agent(debate_log, fact_dict)
    if score < 4:
        return []
    return [content_agent(fact_dict, debate_log)]
