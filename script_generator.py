"""
Generates multi-angle curiosity-gap scripts with auto-translation.
"""

from __future__ import annotations
import json
import re
from deep_translator import GoogleTranslator
import config

def translate_if_needed(text: str) -> str:
    """Detect non-English and translate to English."""
    try:
        # Simple check: if any non-ascii characters are present, translate
        if any(ord(c) > 127 for c in text):
            return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        pass
    return text

def generate_multi_angle_scripts(trend_keyword: str) -> list[dict]:
    """Generate 4 different angles for a single trend."""
    english_keyword = translate_if_needed(trend_keyword)
    scripts = []
    
    # 1. Shock Hook
    scripts.append(_build_script(
        english_keyword, 
        "Shock", 
        f"STOP SCROLLING: {english_keyword} just changed everything.",
        "Something massive just leaked...",
        "Engineers are panicking right now."
    ))
    
    # 2. Curiosity Hook
    scripts.append(_build_script(
        english_keyword, 
        "Curiosity", 
        f"Why is everyone searching {english_keyword} today?",
        "Google is exploding with this query.",
        "The reason behind the surge is insane."
    ))
    
    # 3. Problem Hook
    scripts.append(_build_script(
        english_keyword, 
        "Problem", 
        f"The {english_keyword} problem is getting worse.",
        "Millions are affected and don't even know.",
        "Here is the dark truth you won't hear."
    ))
    
    # 4. Benefit Hook
    scripts.append(_build_script(
        english_keyword, 
        "Benefit", 
        f"This {english_keyword} hack saves hours of work.",
        "Everyone is using it to automate their day.",
        "I found the ultimate shortcut for you."
    ))
    
    return scripts

def _build_script(keyword: str, angle: str, hook: str, why: str, mystery: str) -> dict:
    """Helper to build the 4-scene curiosity gap structure."""
    return {
        "keyword": keyword,
        "angle": angle,
        "title": f"🚨 {hook[:50]} #Shorts #Tech",
        "description": f"{hook}\n\n{why}\n{config.YOUTUBE_DESCRIPTION_FOOTER}",
        "tags": ["tech", "ai", "shorts", "automation", keyword.replace(" ", "")],
        "scenes": [
            hook,
            f"{keyword} is blowing up.",
            mystery,
            config.TELEGRAM_CTA_TEXT
        ],
        "teaser": f"{hook} {why} Full explanation inside Telegram."
    }
