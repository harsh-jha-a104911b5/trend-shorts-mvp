"""
Multi-Agent Fact Extraction, Debate, and Script Generation.
"""

from __future__ import annotations
import re
import random
import config

def extraction_agent(fact_dict: dict) -> str:
    """
    Extracts a single concise insight from the paper.
    """
    title = fact_dict["title"]
    summary = fact_dict["description"]
    # Get first sentence
    sentences = re.split(r'(?<=[.!?]) +', summary)
    core = sentences[0] if sentences else title
    insight = f"{title}: {core}"
    return insight

def debate_agents(insight: str, fact_dict: dict) -> dict:
    """
    Simulates a 3-agent debate over the specific insight.
    Round 1: Discoverer proposes.
    Round 2: Skeptic critiques, Explainer clarifies.
    Round 3: Revised consensus.
    """
    print(f"\n   🤖 [Discoverer] Proposing insight: '{insight[:80]}...'")
    
    summary = fact_dict["description"].lower()
    
    # skeptic logic
    if any(hedge in summary for hedge in ['suggests', 'might', 'potentially', 'early stage', 'propose']):
        skeptic_critique = "The claim is heavily hedged. This might not be production-ready yet."
    elif 'dataset' in summary or 'benchmark' in summary:
        skeptic_critique = "This focuses on an evaluation dataset, not a fundamentally new capability."
    else:
        skeptic_critique = "This sounds impressive, but does it generalize beyond the specific test environment?"
        
    print(f"   🤖 [Skeptic]    Critique: {skeptic_critique}")
    
    # explainer logic
    if "first" in summary or "novel" in summary or "state-of-the-art" in summary:
        explainer_clarification = "The authors explicitly demonstrate state-of-the-art results, differentiating it clearly from prior work."
    else:
        explainer_clarification = "The underlying architecture provides measurable improvements worth highlighting."
        
    print(f"   🤖 [Explainer]  Clarification: {explainer_clarification}")
    
    # Round 3
    revised_statement = f"While its immediate scale may be bounded, the research introduces a highly novel paradigm."
    print(f"   🤖 [Discoverer] Revised: {revised_statement}")
    
    return {
        "original_insight": insight,
        "critique": skeptic_critique,
        "clarification": explainer_clarification,
        "revised": revised_statement
    }

def consensus_agent(debate_log: dict, fact_dict: dict) -> int:
    """
    Score the debate 0-10 on accuracy, novelty, and educational value.
    Reject low quality.
    """
    score = 5
    summary = fact_dict["description"].lower()
    title = fact_dict["title"].lower()
    
    # Novelty value
    if "novel" in summary or "breakthrough" in title or "first time" in summary:
        score += 2
        
    # Educational Value 
    if "tutorial" not in title and "survey" not in title:
        score += 1
        if "architecture" in summary or "model" in summary:
            score += 1
            
    # Accuracy downgrade from Skeptic
    if "dataset" in debate_log["critique"] or "hedged" in debate_log["critique"]:
        score -= 2
        
    print(f"   ⚖️ [Consensus]  Final Score: {score}/10")
    return max(0, min(10, score))

def content_agent(fact_dict: dict, debate_log: dict) -> dict:
    """
    Generates YouTube short script and Telegram post based on consensus insight.
    """
    title = fact_dict["title"]
    summary = fact_dict["description"]
    link = fact_dict["link"]
    
    clean_title = re.sub(r'\[.*?\]', '', title).strip()
    words = clean_title.split()
    hook_frag = " ".join(words[:6]) + "..." if len(words) > 8 else clean_title
    
    hooks = [
        f"AI just did something terrifying: {hook_frag}",
        f"Scientists just proved that {hook_frag}",
        f"This AI discovery changes everything.",
        f"A massive AI breakthrough just leaked."
    ]
    hook = random.choice(hooks)
    
    # Telegram Archive Post containing debate context
    telegram_post = (
        f"🧠 *KNOWLEDGE ARCHIVE*\n\n"
        f"*{clean_title}*\n\n"
        f"_{summary[:250]}..._\n\n"
        f"🗣️ *Agent Debate Snippet:*\n"
        f"❌ _Skeptic:_ {debate_log['critique']}\n"
        f"✅ _Explainer:_ {debate_log['clarification']}\n\n"
        f"🔗 *Read Full Paper:* {link}"
    )
    
    return {
        "keyword": clean_title,
        "angle": "Debated AI Fact",
        "title": f"🚨 {hook[:50]} #AI #Tech",
        "description": f"{title}\n\nFull explanation on Telegram: {config.TELEGRAM_LINK}",
        "tags": ["ai", "research", "technology", "shorts", "news"],
        "scenes": [
            "🚨 STOP SCROLLING 🚨",
            "A massive AI breakthrough just leaked.",
            clean_title[:35] + "...",
            config.TELEGRAM_CTA_TEXT
        ],
        "teaser": telegram_post
    }

def generate_scripts_from_fact(fact_dict: dict) -> list[dict]:
    """
    Pipeline orchestrator for the Fact Extraction -> Debate -> Consensus Agents.
    """
    insight = extraction_agent(fact_dict)
    debate_log = debate_agents(insight, fact_dict)
    score = consensus_agent(debate_log, fact_dict)
    
    if score < 4:
        print("   📉 Consensus Reject: Quality threshold not met.")
        return []
        
    print("   📈 Consensus Approve: Insight validated for publishing.")
    script = content_agent(fact_dict, debate_log)
    return [script]
