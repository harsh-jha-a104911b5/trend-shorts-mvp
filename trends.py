"""
Fetch trending keywords from Google Trends (India).

Uses multiple fallback methods to ensure trends are ALWAYS available:
  1. Direct RSS feed from Google Trends (most reliable)
  2. pytrends library
  3. Curated fallback list (offline safety net)
"""

import requests
from xml.etree import ElementTree as ET


def get_trends(count: int = 10) -> list[str]:
    """
    Return a list of currently trending search keywords in India.

    Tries multiple methods with automatic fallback to guarantee results.

    Args:
        count: Maximum number of trend keywords to return.

    Returns:
        A list of trend keyword strings.
    """
    # Method 1: Direct RSS feed (most reliable)
    keywords = _fetch_rss_trends(count)
    if keywords:
        return keywords

    # Method 2: pytrends library
    keywords = _fetch_pytrends(count)
    if keywords:
        return keywords

    # Method 3: Hardcoded fallback (offline safety net)
    print("⚠  All trend sources failed — using fallback keywords")
    return _fallback_keywords()[:count]


def _fetch_rss_trends(count: int) -> list[str]:
    """Fetch trends from Google Trends RSS feed (direct HTTP)."""
    try:
        url = "https://trends.google.com/trending/rss?geo=IN"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        items = root.findall(".//item/title")
        keywords = [item.text.strip() for item in items if item.text]

        if keywords:
            print(f"✅ Fetched {len(keywords[:count])} trends via RSS feed")
            return keywords[:count]
    except Exception as e:
        print(f"⚠  RSS feed failed: {e}")

    return []


def _fetch_pytrends(count: int) -> list[str]:
    """Fetch trends using the pytrends library as backup."""
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=330)
        trending = pytrends.trending_searches(pn="india")
        keywords = trending[0].tolist()[:count]

        if keywords:
            print(f"✅ Fetched {len(keywords)} trends via pytrends")
            return keywords
    except Exception as e:
        print(f"⚠  pytrends failed: {e}")

    return []


def _fallback_keywords() -> list[str]:
    """Curated fallback list — keeps the pipeline running even offline."""
    return [
        "Artificial Intelligence",
        "iPhone 16",
        "Cricket World Cup",
        "Budget 2026",
        "Electric Cars India",
        "ChatGPT",
        "Stock Market Today",
        "Instagram Update",
        "Bollywood News",
        "Tech Layoffs",
    ]
