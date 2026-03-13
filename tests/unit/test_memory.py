import os
import pytest
from core.memory import load_memory, save_memory
import config


def test_duplicate_detection():
    # Setup
    test_file = os.path.join(config.DATA_DIR, "test_memory.json")
    old_file = config.MEMORY_FILE
    old_trends = config.PROCESSED_TRENDS_FILE
    
    config.MEMORY_FILE = test_file
    config.PROCESSED_TRENDS_FILE = test_file
    
    # Ensure clean slate
    if os.path.exists(test_file):
        os.remove(test_file)

    # Run tests
    save_memory("test-link-1", "Test Title")
    save_memory("test-link-2", "Test Title 2")
    save_memory("test-link-1", "Duplicate should be ignored")

    mem = load_memory()
    assert "test-link-1" in mem
    assert "test-link-2" in mem
    assert len(mem) == 2

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    config.MEMORY_FILE = old_file
    config.PROCESSED_TRENDS_FILE = old_trends
