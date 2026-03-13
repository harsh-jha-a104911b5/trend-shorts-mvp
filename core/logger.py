import logging
import os
import config

# Ensure directories exist
os.makedirs(config.LOGS_DIR, exist_ok=True)
os.makedirs(config.DATA_DIR, exist_ok=True)

logger = logging.getLogger("PipelineLogger")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Also log to console
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def get_logger(name: str):
    return logger.getChild(name)
