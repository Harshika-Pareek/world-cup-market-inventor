# pipeline/generator.py
import json
from llm_client import call_llm

def generate_markets(signals: dict, team1: str, team2: str) -> list:
    """
    Stage 2: Generate novel betting markets from signals.
    
    Design decisions:
    - Temperature 0.8: creative generation needs variety
    - Signal-driven: markets reference specific match context
    - 8 markets: enough variety for critic to filter
    - Fallback: pipeline never breaks if LLM fails
    
    Alternative approaches considered:
    - One big prompt (extraction + generation): rejected
      because separation of concerns gives better quality
    - Few-shot examples: could improve quality in production
    - Multiple runs (3x): better quality but 3x latency
    """
    print(f"\n[Stage 2] Generating novel markets for {team1} vs {team2}...")

    prompt = f"""
You are a creative betting market designer for a World Cup trading team.
Your job is to invent NOVEL betting markets beyond standard win/lose/draw.

MATCH: {team1} vs {team2}

USE THESE SPECIFIC SIGNALS TO CREATE RELEVANT MARKETS:
- Key injuries: {signals.get('key_injuries')}
- {team1} form: {signals.get('team1_form')}
- {team2} form: {signals.get('team2_form')}
- {team1} tactics: {signals.get('team1_tactics')}
- {team2} tactics: {signals.get('team2_tactics')}
- Match conditions: {signals.get('match_conditions')}
- Motivation: {signals.get('motivation')}
- Historical context: {signals.get('historical_context')}
- Key betting signals: {signals.get('key_betting_signals')}

"Important: Generate diverse markets across different categories:
 - At least 2 player-specific markets
 - At least 2 time-based markets (first half, last 20 mins)
 - At least 2 tactical markets
 - At least 2 outcome-based markets
 Do not repeat similar market types.

Return ONLY a valid JSON array. No markdown. No explanation.

[
    {{
        "market_name": "short clear market name",
        "description": "clear description of what this bet is and exactly how it settles"
    }}
]
"""

    try:
        raw = call_llm(prompt, temperature=0.8, max_tokens=1200)

        if raw is None:
            print("LLM returned None — using fallback markets")
            return fallback_markets(team1, team2)

        # Clean markdown if LLM adds it
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        markets = json.loads(raw)
        print(f"Generated {len(markets)} markets")

        # Print what was generated
        print("\nGenerated markets:")
        for i, m in enumerate(markets):
            print(f"  {i+1}. {m.get('market_name')}")

        return markets

    except json.JSONDecodeError as e:
        print(f"JSON parse failed: {e} — using fallback")
        return fallback_markets(team1, team2)

    except Exception as e:
        print(f"Generator failed: {e} — using fallback")
        return fallback_markets(team1, team2)


def fallback_markets(team1: str, team2: str) -> list:
    """
    Fallback markets if LLM fails.
    Ensures pipeline never breaks.
    These are generic but valid markets.
    """
    return [
        {
            "market_name": "First Goal Before 20 Minutes",
            "description": f"Will either {team1} or {team2} score within the first 20 minutes?"
        },
        {
            "market_name": "Total Yellow Cards Over 3.5",
            "description": "Will there be 4 or more yellow cards shown in this match?"
        },
        {
            "market_name": "Both Teams Score",
            "description": f"Will both {team1} and {team2} score at least one goal?"
        },
        {
            "market_name": "Match Goes to Extra Time",
            "description": "Will the match be level after 90 minutes requiring extra time?"
        },
        {
            "market_name": "First Half Under 1.5 Goals",
            "description": "Will fewer than 2 goals be scored in the first half?"
        }
    ]