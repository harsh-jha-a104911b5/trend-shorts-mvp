"""
AI Discovery Agent: Replaces Google Trends.
Aggregates the latest AI research, repos, and news from arXiv, HuggingFace, etc.
"""

from __future__ import annotations
import urllib.request
import feedparser
from bs4 import BeautifulSoup
import re
import requests
import json
import random

def fetch_ai_discoveries(count: int = 15) -> list[dict]:
    """
    Fetch raw AI papers, repos, and articles.
    Returns a list of dicts: {"title": str, "description": str, "source": str, "link": str}
    """
    discoveries = []
    
    # 1. Fetch from arXiv (AI/ML)
    try:
        url = 'http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG&sortBy=submittedDate&sortOrder=desc&max_results=10'
        feed = feedparser.parse(url)
        for entry in feed.entries:
            discoveries.append({
                "title": entry.title.replace('\n', ' ').strip(),
                "description": entry.summary.replace('\n', ' ').strip(),
                "source": "arXiv",
                "link": entry.link
            })
    except Exception as e:
        print(f"⚠ arXiv fetch failed: {e}")

    # 2. Daily Papers via HuggingFace (Unofficial RSS/Scrape)
    try:
        r = requests.get('https://huggingface.co/papers', timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Look for article tags (HF usually uses <article> for papers)
            articles = soup.find_all('article', limit=5)
            for a in articles:
                h3 = a.find('h3')
                p = a.find('p')
                link_tag = a.find('a')
                if h3 and p and link_tag:
                    discoveries.append({
                        "title": h3.get_text().strip(),
                        "description": p.get_text().strip(),
                        "source": "HuggingFace",
                        "link": "https://huggingface.co" + link_tag['href']
                    })
    except Exception as e:
        print(f"⚠ HuggingFace fetch failed: {e}")
        
    # Shuffle to ensure varied sources
    random.shuffle(discoveries)
    
    return discoveries[:count]

def extract_fact(discovery: dict) -> str:
    """
    Extract a single interesting insight from the discovery.
    Since we don't always want to burn an LLM call for raw extraction unless SCRIPT_MODE is API,
    we'll do a local heuristic summary, or use the title itself as the base fact.
    """
    # For MVP, combining Title + first sentence of summary usually yields the core thesis.
    desc = discovery["description"]
    # Get first sentence cleanly
    first_sentence = re.split(r'(?<=[.!?]) +', desc)[0]
    
    # Clean up arXiv abstract noise
    first_sentence = first_sentence.strip()
    
    fact = f"{discovery['title']}: {first_sentence}"
    return fact

# Provide backwards compatibility wrapper so main.py doesn't completely break if it 
# expects a plain list of strings.
def get_trends(count: int = 15) -> list[str]:
    """
    Legacy wrapper. Returns a list of fact strings instead of keywords.
    """
    print("\n📡 Discovery Agent: Scanning arXiv & HuggingFace for AI breakthroughs...")
    raw_discoveries = fetch_ai_discoveries(count)
    return [extract_fact(d) for d in raw_discoveries]

def get_rich_trends(count: int = 15) -> list[dict]:
    """
    Returns the rich dictionary format for Telegram archiving.
    """
    print("\n📡 Discovery Agent: Scanning arXiv & HuggingFace for AI breakthroughs...")
    return fetch_ai_discoveries(count)
