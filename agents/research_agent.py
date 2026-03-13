"""
Research Agent: Scrapes arXiv, HuggingFace for novel AI papers. (formerly trends.py)
"""

from __future__ import annotations
import feedparser
from bs4 import BeautifulSoup
import re
import requests
import random
from core.logger import get_logger
import config

log = get_logger("ResearchAgent")


def fetch_ai_discoveries(count: int = 15) -> list[dict]:
    """Fetch raw AI papers, repos, and articles."""
    discoveries = []

    # 1. Fetch from arXiv (AI/ML)
    try:
        url = "http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=descending&max_results=10"
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title.replace("\n", " ").strip()
            if title.lower() == "error":
                continue
            discoveries.append(
                {
                    "title": title,
                    "description": entry.summary.replace("\n", " ").strip(),
                    "source": "arXiv",
                    "link": entry.link,
                }
            )
        log.info(f"Fetched {len(feed.entries)} candidates from arXiv")
    except Exception as e:
        log.error(f"arXiv fetch failed: {e}")

    # 2. Daily Papers via HuggingFace
    try:
        r = requests.get("https://huggingface.co/papers", timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.find_all("article", limit=5)
            for a in articles:
                h3 = a.find("h3")
                p = a.find("p")
                link_tag = a.find("a")
                if h3 and p and link_tag:
                    discoveries.append(
                        {
                            "title": h3.get_text().strip(),
                            "description": p.get_text().strip(),
                            "source": "HuggingFace",
                            "link": "https://huggingface.co" + link_tag["href"],
                        }
                    )
            log.info(f"Fetched candidates from HuggingFace")
    except Exception as e:
        log.error(f"HuggingFace fetch failed: {e}")

    random.shuffle(discoveries)
    return discoveries[:count]


def get_rich_trends(count: int = 15) -> list[dict]:
    """Used by legacy wrappers / main orchestrator."""
    log.info("Scanning for AI breakthroughs...")
    return fetch_ai_discoveries(count)


def research_run(memory: set) -> list[dict]:
    log.info("Fetching candidate discoveries...")
    raw_discoveries = fetch_ai_discoveries(15)
    filtered = [d for d in raw_discoveries if d["link"] not in memory]
    selected = filtered[: config.MAX_TRENDS_PER_RUN]
    log.info(f"Isolated {len(selected)} completely new topics for debate.")
    return selected
