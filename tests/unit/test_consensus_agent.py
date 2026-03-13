import pytest
from agents.consensus_agent import consensus_agent


def test_fact_scoring():
    debate_log = {"critique": "Dataset is focused"}
    fact_dict = {
        "title": "A breakthrough in novel LLMs",
        "description": "This is the first time a model does X.",
    }
    score = consensus_agent(debate_log, fact_dict)

    # +2 for novel/breakthrough/first time -> x3 = +6
    # +1 for non-tutorial
    # -2 for dataset critique
    # Score should definitely exceed the threshold of 4.
    assert score > 4
