import pytest
from agents.content_agent import content_agent
import config


def test_hook_generation():
    debate = {"critique": "None", "clarification": "Clear"}
    fact = {
        "title": "Self Replicating Neural Networks Found",
        "description": "Long dec",
        "link": "http://x",
    }
    script = content_agent(fact, debate)

    assert "Self Replicating" in script["keyword"]
    assert len(script["scenes"]) == 4


def test_telegram_explanation():
    debate = {"critique": "None", "clarification": "Clear"}
    fact = {"title": "XYZ", "description": "ABC", "link": "123"}
    script = content_agent(fact, debate)

    # Must include deep knowledge format
    assert "KNOWLEDGE ARCHIVE" in script["teaser"]
    assert "Agent Debate Snippet" in script["teaser"]
