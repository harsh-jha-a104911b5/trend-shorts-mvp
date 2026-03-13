"""
Content Agent. Constructs the final video script and Telegram structure.
"""

from __future__ import annotations
import re
import random
import config
from core.logger import get_logger

log = get_logger("ContentAgent")


def content_agent(fact_dict: dict, debate_log: dict) -> dict:
    """Generates YouTube short script and Telegram post based on consensus insight."""
    title = fact_dict["title"]
    summary = fact_dict["description"]
    link = fact_dict["link"]

    clean_title = re.sub(r"\[.*?\]", "", title).strip()
    words = clean_title.split()
    hook_frag = " ".join(words[:6]) + "..." if len(words) > 8 else clean_title

    hooks = [
        f"AI just did something terrifying: {hook_frag}",
        f"Scientists just proved that {hook_frag}",
        f"This AI discovery changes everything.",
        f"A massive AI breakthrough just leaked.",
    ]
    hook = random.choice(hooks)

    telegram_post = (
        f"🧠 *KNOWLEDGE ARCHIVE*\n\n"
        f"*{clean_title}*\n\n"
        f"_{summary[:250]}..._\n\n"
        f"🗣️ *Agent Debate Snippet:*\n"
        f"❌ _Skeptic:_ {debate_log['critique']}\n"
        f"✅ _Explainer:_ {debate_log['clarification']}\n\n"
        f"🔗 *Read Full Paper:* {link}"
    )

    script = {
        "keyword": clean_title,
        "angle": "Debated AI Fact",
        "title": f"🚨 {hook[:50]} #AI #Tech",
        "description": f"{title}\n\nFull explanation on Telegram: {config.TELEGRAM_LINK}",
        "tags": ["ai", "research", "technology", "shorts", "news"],
        "scenes": [
            "🚨 STOP SCROLLING 🚨",
            "A massive AI breakthrough just leaked.",
            clean_title[:35] + "...",
            config.TELEGRAM_CTA_TEXT,
        ],
        "teaser": telegram_post,
    }
    log.info("Finished composing multi-layered script and archive package.")
    return script
