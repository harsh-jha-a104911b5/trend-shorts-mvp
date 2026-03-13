"""
Memory module. Handles local database for tracking facts and metrics.
"""

from __future__ import annotations
import os
import json
import config
from core.logger import get_logger

log = get_logger("Memory")


def load_memory() -> set:
    """Retrieve published insights from long-term memory."""
    processed = set()
    # Support legacy file
    if os.path.exists(config.PROCESSED_TRENDS_FILE):
        with open(config.PROCESSED_TRENDS_FILE, "r", encoding="utf-8") as f:
            try:
                processed.update(json.load(f).get("processed", []))
            except json.JSONDecodeError:
                pass

    if os.path.exists(config.MEMORY_FILE):
        with open(config.MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                processed.update([r["link"] for r in data.get("records", [])])
                processed.update(data.get("processed", []))
            except json.JSONDecodeError:
                pass
    return processed


def save_memory(link_id: str, title: str = "", source: str = "", timestamp: str = ""):
    """Store published insight to prevent duplicates."""
    data = {"processed": [], "records": []}

    if os.path.exists(config.MEMORY_FILE):
        with open(config.MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass

    if link_id not in data.get("processed", []):
        data.setdefault("processed", []).append(link_id)
        data.setdefault("records", []).append(
            {"link": link_id, "title": title, "source": source, "timestamp": timestamp}
        )
        with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log.info(f"Memory saved for: {title[:30]}")


def log_metrics(videos_produced: int, errors: int, runtime_sec: float):
    """Log performance metrics."""
    metrics = {"metrics": []}
    if os.path.exists(config.METRICS_FILE):
        with open(config.METRICS_FILE, "r", encoding="utf-8") as f:
            try:
                metrics = json.load(f)
            except json.JSONDecodeError:
                pass

    import time
    from datetime import datetime

    metrics["metrics"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "videos_produced": videos_produced,
            "errors": errors,
            "runtime_sec": round(runtime_sec, 2),
        }
    )

    with open(config.METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)
