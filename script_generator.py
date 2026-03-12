"""
Generate a short video script (list of scene texts) for a trending keyword.

Also produces title, description, and tags for YouTube upload.

Supports two modes:
  • "mock"  — free, deterministic, zero-API local generation (default).
  • API     — plug in Gemini / OpenAI / Claude by setting config.SCRIPT_MODE
              and the matching API key.
"""

from __future__ import annotations

import config


def generate_script(keyword: str) -> dict:
    """
    Produce a complete script dict for the given trending keyword.

    Returns:
        {
            "keyword": "...",
            "scenes": ["SCENE 1 TEXT", ...],
            "title": "VIDEO TITLE",
            "description": "Video description text.",
            "tags": ["tag1", "tag2", ...]
        }
    """
    mode = config.SCRIPT_MODE.lower()

    if mode == "mock":
        return _mock_script(keyword)
    elif mode == "gemini":
        return _gemini_script(keyword)
    elif mode == "openai":
        return _openai_script(keyword)
    elif mode == "claude":
        return _claude_script(keyword)
    else:
        print(f"⚠  Unknown SCRIPT_MODE '{mode}', falling back to mock.")
        return _mock_script(keyword)


# ──────────────────────────────────────────────────────────────────
#  Mode 1 — Mock generator (free, always works)
# ──────────────────────────────────────────────────────────────────

def _mock_script(keyword: str) -> dict:
    """Generate a punchy 4-scene script with title/desc/tags locally."""
    kw_upper = keyword.upper()
    kw_title = keyword.title()

    scenes = [
        "🔥 STOP SCROLLING!",
        f"🚀 {kw_upper} IS TRENDING",
        "💥 YOU NEED TO KNOW THIS",
        "👇 FOLLOW FOR MORE!",
    ]

    title = f"{kw_title} — Trending Now! 🔥 #Shorts"
    description = (
        f"🚀 {kw_title} is trending right now!\n\n"
        f"Stay updated with the latest tech trends.\n"
        f"Like, subscribe, and hit the bell for daily shorts!\n\n"
        f"#Shorts #{kw_title.replace(' ', '')} #Trending #Tech"
    )
    tags = [
        keyword.lower(),
        "shorts", "trending", "tech", "viral",
        "technology", "ai", "gadgets", "news",
    ]

    return {
        "keyword": keyword,
        "scenes": scenes,
        "title": title,
        "description": description,
        "tags": tags,
    }


# ──────────────────────────────────────────────────────────────────
#  Mode 2 — API generators (plug-and-play)
# ──────────────────────────────────────────────────────────────────

_PROMPT_TEMPLATE = (
    "You are a YouTube Shorts scriptwriter for a tech channel. "
    "Generate content for a vertical video about: '{keyword}'. "
    "Return ONLY a JSON object with these exact keys:\n"
    '{{\n'
    '  "scenes": ["SCENE1", "SCENE2", "SCENE3", "SCENE4"],\n'
    '  "title": "CATCHY TITLE UNDER 100 CHARS",\n'
    '  "description": "Short engaging description with hashtags",\n'
    '  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]\n'
    '}}\n'
    "Scenes must be max 8 words each. Title must be attention-grabbing."
)


def _parse_api_response(keyword: str, raw_text: str) -> dict:
    """Parse JSON from API response and build the full script dict."""
    import json
    data = json.loads(raw_text)
    result = {
        "keyword": keyword,
        "scenes": data.get("scenes", [])[:config.SCENE_COUNT],
        "title": data.get("title", f"{keyword} — Trending Now! 🔥 #Shorts"),
        "description": data.get("description", f"{keyword} is trending!"),
        "tags": data.get("tags", [keyword.lower(), "shorts", "tech"]),
    }
    return result


def _gemini_script(keyword: str) -> dict:
    """Use Google Gemini API to generate a script."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(_PROMPT_TEMPLATE.format(keyword=keyword))
        return _parse_api_response(keyword, response.text)
    except Exception as e:
        print(f"⚠  Gemini failed ({e}), falling back to mock.")
        return _mock_script(keyword)


def _openai_script(keyword: str) -> dict:
    """Use OpenAI API to generate a script."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(keyword=keyword)}],
            temperature=0.8,
        )
        return _parse_api_response(keyword, resp.choices[0].message.content)
    except Exception as e:
        print(f"⚠  OpenAI failed ({e}), falling back to mock.")
        return _mock_script(keyword)


def _claude_script(keyword: str) -> dict:
    """Use Anthropic Claude API to generate a script."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=config.CLAUDE_API_KEY)
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=256,
            messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(keyword=keyword)}],
        )
        return _parse_api_response(keyword, msg.content[0].text)
    except Exception as e:
        print(f"⚠  Claude failed ({e}), falling back to mock.")
        return _mock_script(keyword)
