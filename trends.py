"""
Fetch trending keywords from Google Trends (India).
Falls back to curated defaults if the API is unreachable.
"""

from pytrends.request import TrendReq


def get_trends(count: int = 10) -> list[str]:
    """
    Return a list of currently trending search keywords in India.

    Uses the Google Trends 'trending_searches' endpoint via pytrends.
    Falls back to a hardcoded list if the request fails (network issues,
    rate-limiting, etc.) so the pipeline never breaks.

    Args:
        count: Maximum number of trend keywords to return.

    Returns:
        A list of trend keyword strings.
    """
    try:
        pytrends = TrendReq(hl="en-US", tz=330)  # IST offset
        trending = pytrends.trending_searches(pn="india")
        # trending is a DataFrame with a single column (0)
        keywords = trending[0].tolist()[:count]
        if keywords:
            return keywords
    except Exception as e:
        print(f"⚠  Google Trends unavailable: {e}")

    # Fallback — keeps the pipeline running even offline
    return [
        "Artificial Intelligence",
        "iPhone 16",
        "Cricket World Cup",
        "Budget 2026",
        "Electric Cars India",
    ]
