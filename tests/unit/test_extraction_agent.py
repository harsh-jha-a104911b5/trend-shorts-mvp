import pytest
from agents.extraction_agent import extraction_agent


def test_fact_extraction():
    mock_dict = {
        "title": "Quantum AI",
        "description": "This is a new field. It combines quantum physics with AI. Very cool.",
    }
    insight = extraction_agent(mock_dict)
    assert insight == "Quantum AI: This is a new field."
