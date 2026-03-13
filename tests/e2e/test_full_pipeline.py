import pytest
import os
from unittest.mock import patch, MagicMock
from core.pipeline import run_pipeline
from core.memory import load_memory
import config


@patch("core.pipeline.generate_video")
@patch("core.pipeline.publishing_agent")
@patch("agents.research_agent.fetch_ai_discoveries")
def test_full_pipeline(mock_fetch, mock_publish, mock_generate):
    """
    E2E simulation to verify zero crashes down the entire agent network.
    Overrides memory constraints and blocks uploading.
    """

    # 1. Mock network return
    mock_fetch.return_value = [
        {
            "title": "Quantum AI Networks",
            "description": "Novel approach to interconnected neural networks.",
            "link": "e2e-test-link",
            "source": "arXiv",
        }
    ]

    # 2. Mock video and upload (heavy IO)
    mock_generate.return_value = "/tmp/fake.mp4"
    mock_publish.return_value = True

    # Setup clean space
    config.MAX_TRENDS_PER_RUN = 1
    test_file = os.path.join(config.DATA_DIR, "e2e_memory.json")
    old_file = config.MEMORY_FILE
    old_trends_file = config.PROCESSED_TRENDS_FILE
    
    config.MEMORY_FILE = test_file
    config.PROCESSED_TRENDS_FILE = test_file

    if os.path.exists(test_file):
        os.remove(test_file)

    # 3. Fire the entire engine module end to end
    run_pipeline()

    # 4. Verify system interactions
    mock_generate.assert_called_once()  # Debated, Accepted, Scripted, Rendered
    mock_publish.assert_called_once()

    mem = load_memory()
    assert "e2e-test-link" in mem

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    config.MEMORY_FILE = old_file
    config.PROCESSED_TRENDS_FILE = old_trends_file
