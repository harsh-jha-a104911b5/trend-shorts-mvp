import pytest
from agents.extraction_agent import extraction_agent
from agents.debate_agents import DebateNetwork
from agents.consensus_agent import consensus_agent
from agents.content_agent import content_agent


def test_fact_pipeline():
    """Validates the core transition from discovery extraction down to script output."""
    fact_dict = {
        "title": "Agentic Reasoning in Math",
        "description": "This demonstrates a novel zero shot agent.",
        "source": "arXiv",
        "link": "https://test",
    }

    insight = extraction_agent(fact_dict)
    assert insight is not None

    debate = DebateNetwork.debate(insight, fact_dict)
    assert debate["critique"] is not None

    score = consensus_agent(debate, fact_dict)
    assert score >= 4  # Should definitely pass novelty

    script = content_agent(fact_dict, debate)
    assert script["keyword"] == "Agentic Reasoning in Math"
    assert len(script["scenes"]) == 4
