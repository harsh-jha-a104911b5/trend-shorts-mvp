"""
Fact Extraction, Verification, and Script Generation Agent.
"""

from __future__ import annotations
import json
import re
import random
from deep_translator import GoogleTranslator
import config

def score_uniqueness(text: str, title: str) -> int:
    """
    Heuristic Uniqueness Scorer.
    Scores 0-10 based on keywords associated with surprise, novelty, or disruption.
    """
    score = 5 # Base score
    
    # Positive novelty indicators
    hot_words = ['breakthrough', 'unexpected', 'outperforms', 'state-of-the-art', 
                 'first time', 'overcome', 'novel', 'paradigm', 'surpasses', 'human-level']
    
    text_lower = text.lower() + " " + title.lower()
    
    for word in hot_words:
        if word in text_lower:
            score += 2
            
    # Penalize purely theoretical / academic noise
    boring = ['survey', 'review', 'empirical study', 'we analyze', 'dataset']
    for word in boring:
        if word in text_lower:
            score -= 3
            
    return max(0, min(10, score))


def extract_hook_from_paper(title: str, summary: str) -> str:
    """
    Distills a complex AI paper title/abstract into a single TikTok hook string.
    If Gemini/OpenAI is active, this should ideally use the LLM. 
    For MVP, we use NLP heuristics.
    """
    # Simple extraction for local execution without LLM overhead
    # We strip bracket metadata e.g. [2305.1234] 
    clean_title = re.sub(r'\[.*?\]', '', title).strip()
    
    # Create an intriguing mystery phrase
    words = clean_title.split()
    if len(words) > 8:
        hook_fragment = " ".join(words[:6]) + "..."
    else:
        hook_fragment = clean_title
        
    hooks = [
        f"AI just did something terrifying: {hook_fragment}",
        f"Scientists just proved that {hook_fragment}",
        f"This new AI discovery will change everything.",
        f"A massive AI breakthrough just happened: {hook_fragment}"
    ]
    return random.choice(hooks)


def generate_scripts_from_fact(fact_dict: dict) -> list[dict]:
    """
    Takes a rich discovery dict and generates a video script and Telegram Knowledge Archive.
    """
    title = fact_dict["title"]
    summary = fact_dict["description"]
    link = fact_dict["link"]
    
    # 1. Verification & Uniqueness Agent
    score = score_uniqueness(summary, title)
    if score < 4:
        # Returning empty list drops this fact from the pipeline
        print(f"   📉 Dropping low uniqueness fact (Score: {score})")
        return []
        
    print(f"   📈 High Uniqueness Fact (Score: {score})")
    
    hook = extract_hook_from_paper(title, summary)
    
    # Telegram Archive Format
    telegram_detailed = (
        f"🧠 *KNOWLEDGE ARCHIVE*\n\n"
        f"*{title}*\n\n"
        f"_{summary[:300]}..._\n\n"
        f"🔗 *Read Full Paper:* {link}"
    )
    
    # Video Generation Dict (Using curiosity gap)
    script = {
        "keyword": title,
        "angle": "Discovery",
        "title": f"🚨 {hook[:50]} #AI #Tech",
        "description": f"{title}\n\nFull explanation on Telegram: {config.TELEGRAM_LINK}",
        "tags": ["ai", "research", "technology", "shorts", "news"],
        "scenes": [
            "🚨 STOP SCROLLING 🚨",
            "A massive AI breakthrough just leaked.",
            title[:40] + "...",
            config.TELEGRAM_CTA_TEXT
        ],
        
        # We pass the full deep telegram message in 'teaser' so main.py can pipe exactly this
        "teaser": telegram_detailed 
    }
    
    return [script]
