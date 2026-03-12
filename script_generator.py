"""
Generate a short video script (list of scene texts) for a trending keyword.

Supports two modes:
  • "mock"  — free, deterministic, zero-API local generation (default).
  • API     — plug in Gemini / OpenAI / Claude by setting config.SCRIPT_MODE
              and the matching API key.
"""

from __future__ import annotations

import config


def generate_script(keyword: str) -> dict:
    """
    Produce a script dict for the given trending keyword.

    Returns:
        {
            "keyword": "...",
            "scenes": ["SCENE 1 TEXT", "SCENE 2 TEXT", ...]
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
    """Generate a punchy 4-scene script locally without any API."""
    kw_upper = keyword.upper()
    scenes = [
        "🔥 STOP SCROLLING!",
        f"🚀 {kw_upper} IS TRENDING",
        "💥 YOU NEED TO KNOW THIS",
        "👇 FOLLOW FOR MORE!",
    ]
    return {"keyword": keyword, "scenes": scenes}


# ──────────────────────────────────────────────────────────────────
#  Mode 2 — API generators (plug-and-play)
# ──────────────────────────────────────────────────────────────────

_PROMPT_TEMPLATE = (
    "You are a YouTube Shorts scriptwriter. "
    "Generate exactly 4 short, punchy scene texts (max 8 words each) "
    "for a vertical video about the trending topic: '{keyword}'. "
    "Return ONLY a JSON object like: "
    '{{ "scenes": ["SCENE1", "SCENE2", "SCENE3", "SCENE4"] }}'
)


def _gemini_script(keyword: str) -> dict:
    """Use Google Gemini API to generate a script."""
    try:
        import google.generativeai as genai
        import json

        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(_PROMPT_TEMPLATE.format(keyword=keyword))
        data = json.loads(response.text)
        return {"keyword": keyword, "scenes": data["scenes"][:config.SCENE_COUNT]}
    except Exception as e:
        print(f"⚠  Gemini failed ({e}), falling back to mock.")
        return _mock_script(keyword)


def _openai_script(keyword: str) -> dict:
    """Use OpenAI API to generate a script."""
    try:
        from openai import OpenAI
        import json

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(keyword=keyword)}],
            temperature=0.8,
        )
        data = json.loads(resp.choices[0].message.content)
        return {"keyword": keyword, "scenes": data["scenes"][:config.SCENE_COUNT]}
    except Exception as e:
        print(f"⚠  OpenAI failed ({e}), falling back to mock.")
        return _mock_script(keyword)


def _claude_script(keyword: str) -> dict:
    """Use Anthropic Claude API to generate a script."""
    try:
        import anthropic
        import json

        client = anthropic.Anthropic(api_key=config.CLAUDE_API_KEY)
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=256,
            messages=[{"role": "user", "content": _PROMPT_TEMPLATE.format(keyword=keyword)}],
        )
        data = json.loads(msg.content[0].text)
        return {"keyword": keyword, "scenes": data["scenes"][:config.SCENE_COUNT]}
    except Exception as e:
        print(f"⚠  Claude failed ({e}), falling back to mock.")
        return _mock_script(keyword)
