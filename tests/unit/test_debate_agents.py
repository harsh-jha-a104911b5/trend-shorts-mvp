import pytest
from agents.debate_agents import DebateNetwork


def test_debate_round():
    insight = "New AI beats humans."
    fact = {"description": "This dataset provides a novel benchmark for testing."}
    res = DebateNetwork.debate(insight, fact)

    assert "original_insight" in res
    assert "critique" in res
    assert "clarification" in res
    assert "revised" in res


def test_skeptic_challenge():
    insight = "AI proposes new math."
    fact = {"description": "Authors propose a dataset for future research."}
    res = DebateNetwork.debate(insight, fact)

    # skeptic should trigger on 'dataset'
    assert "dataset" in res["critique"].lower() or "hedged" in res["critique"].lower()
