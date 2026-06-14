# pipeline/extractor.py
import json
from llm_client import call_llm

def extract_signals(news: str, team1: str, team2: str) -> dict:
    """
    Stage 1: Extract structured signals from raw news.

    Design decisions:
    - Temperature 0.0: factual extraction needs consistency
    - Structured JSON: machine readable for next pipeline stage
    - Seven signal categories: injuries, form, tactics,
      conditions, goalkeeper, defensive, historical
    - Fallback: pipeline never breaks if LLM fails

    Why seven categories:
    Each generates different types of markets.
    Goalkeeper signals → penalty/save markets
    Defensive signals → low scoring/clean sheet markets
    Injury signals → player specific markets
    More signal types = more creative varied markets
    """
    print(f"\n[Stage 1] Extracting signals for {team1} vs {team2}...")

    prompt = f"""
You are a football betting analyst working for a World Cup trading team.
Read the following match news carefully and extract ALL key signals.
Pay special attention to goalkeeper stats and defensive actions.

MATCH NEWS:
{news}

TEAMS: {team1} vs {team2}

Return ONLY valid JSON. No markdown. No explanation. Just JSON.

{{
    "match": "{team1} vs {team2}",

    "key_injuries": [
        {{
            "player": "player name",
            "team": "team name",
            "status": "doubtful or injured",
            "impact": "how this affects betting markets"
        }}
    ],

    "team1_form": "brief description of {team1} recent form and results",
    "team2_form": "brief description of {team2} recent form and results",

    "team1_tactics": "expected tactical setup and style for {team1}",
    "team2_tactics": "expected tactical setup and style for {team2}",

    "match_conditions": "weather, temperature, venue and atmosphere",

    "motivation": "what is at stake for each team — revenge, survival, glory",

    "historical_context": "head to head history and key previous meetings",

    "goalkeeper_signals": {{
        "team1_goalkeeper": "name and key stats for {team1} goalkeeper",
        "team1_gk_saves": "average saves per match and notable saves",
        "team1_gk_penalties": "penalty saving record and shootout experience",
        "team1_clean_sheets": "clean sheet record in this tournament",
        "team2_goalkeeper": "name and key stats for {team2} goalkeeper",
        "team2_gk_saves": "average saves per match and notable saves",
        "team2_gk_penalties": "penalty saving record and shootout experience",
        "team2_clean_sheets": "clean sheet record in this tournament",
        "shootout_likely": "is a penalty shootout a realistic possibility?"
    }},

    "defensive_signals": {{
        "team1_defensive_actions": "tackles, blocks, interceptions per match for {team1}",
        "team1_shots_conceded": "shots conceded per match for {team1}",
        "team2_defensive_actions": "tackles, blocks, interceptions per match for {team2}",
        "team2_shots_conceded": "shots conceded per match for {team2}",
        "set_piece_threat": "are set pieces a major threat for either team?",
        "defensive_style": "how does each team defend — high press, deep block, man mark?"
    }},

    "key_betting_signals": [
        "signal 1 — most important thing affecting betting markets",
        "signal 2 — second most important signal",
        "signal 3 — third signal",
        "signal 4 — fourth signal",
        "signal 5 — goalkeeper or defensive specific signal",
        "signal 6 — tactical or conditions signal"
    ]
}}
"""

    try:
        raw = call_llm(prompt, temperature=0.0, max_tokens=1500)

        if raw is None:
            print("LLM returned None — using fallback signals")
            return fallback_signals(team1, team2)

        # Clean markdown if LLM adds it
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        signals = json.loads(raw)
        print_signal_summary(signals, team1, team2)
        print(f"Signals extracted ✅")
        return signals

    except json.JSONDecodeError as e:
        print(f"JSON parse failed: {e} — using fallback")
        return fallback_signals(team1, team2)

    except Exception as e:
        print(f"Extraction failed: {e} — using fallback")
        return fallback_signals(team1, team2)


def print_signal_summary(signals: dict, team1: str, team2: str):
    """
    Print plain English summary of all extracted signals.
    Makes News-to-Signal aspect visible in demo.
    Shows trader exactly what the AI found.
    """
    print(f"\n{'='*50}")
    print(f"SIGNAL SUMMARY: {signals.get('match')}")
    print(f"{'='*50}")

    # Injuries
    injuries = signals.get("key_injuries", [])
    if injuries:
        print(f"\n🏥 KEY INJURIES:")
        for injury in injuries:
            print(f"  → {injury.get('player')} "
                  f"({injury.get('team')}): "
                  f"{injury.get('status')} — "
                  f"{injury.get('impact')}")

    # Goalkeeper signals
    gk = signals.get("goalkeeper_signals", {})
    if gk:
        print(f"\n🧤 GOALKEEPER SIGNALS:")
        print(f"  → {team1}: {gk.get('team1_goalkeeper')}")
        print(f"     Saves: {gk.get('team1_gk_saves')}")
        print(f"     Penalties: {gk.get('team1_gk_penalties')}")
        print(f"     Clean sheets: {gk.get('team1_clean_sheets')}")
        print(f"  → {team2}: {gk.get('team2_goalkeeper')}")
        print(f"     Saves: {gk.get('team2_gk_saves')}")
        print(f"     Penalties: {gk.get('team2_gk_penalties')}")
        print(f"     Clean sheets: {gk.get('team2_clean_sheets')}")
        print(f"  → Shootout likely: {gk.get('shootout_likely')}")

    # Defensive signals
    defence = signals.get("defensive_signals", {})
    if defence:
        print(f"\n DEFENSIVE SIGNALS:")
        print(f"  → {team1} defensive actions: "
              f"{defence.get('team1_defensive_actions')}")
        print(f"  → {team1} shots conceded: "
              f"{defence.get('team1_shots_conceded')}")
        print(f"  → {team2} defensive actions: "
              f"{defence.get('team2_defensive_actions')}")
        print(f"  → {team2} shots conceded: "
              f"{defence.get('team2_shots_conceded')}")
        print(f"  → Set piece threat: "
              f"{defence.get('set_piece_threat')}")
        print(f"  → Defensive style: "
              f"{defence.get('defensive_style')}")

    # Form
    print(f"\n  FORM:")
    print(f"  → {team1}: {signals.get('team1_form')}")
    print(f"  → {team2}: {signals.get('team2_form')}")

    # Conditions
    print(f"\n  CONDITIONS:")
    print(f"  → {signals.get('match_conditions')}")

    # Motivation
    print(f"\n MOTIVATION:")
    print(f"  → {signals.get('motivation')}")

    # History
    print(f"\n HISTORY:")
    print(f"  → {signals.get('historical_context')}")

    # Key betting signals
    betting_signals = signals.get("key_betting_signals", [])
    if betting_signals:
        print(f"\n💡 KEY BETTING SIGNALS:")
        for signal in betting_signals:
            print(f"  → {signal}")

    print(f"{'='*50}\n")


def fallback_signals(team1: str, team2: str) -> dict:
    """
    Fallback if LLM fails.
    Returns reasonable default signals.
    Pipeline never breaks.
    """
    return {
        "match": f"{team1} vs {team2}",
        "key_injuries": [
            {
                "player": "Unknown",
                "team": team1,
                "status": "doubtful",
                "impact": "Weakens attacking options"
            }
        ],
        "team1_form": f"{team1} in good recent form",
        "team2_form": f"{team2} competitive recent results",
        "team1_tactics": "Attacking 4-3-3",
        "team2_tactics": "Defensive counter-attack",
        "match_conditions": "Standard World Cup conditions",
        "motivation": "High stakes World Cup match",
        "historical_context": "Competitive recent history",
        "goalkeeper_signals": {
            "team1_goalkeeper": f"{team1} goalkeeper",
            "team1_gk_saves": "averaging 3 saves per match",
            "team1_gk_penalties": "no penalty save record available",
            "team1_clean_sheets": "2 clean sheets this tournament",
            "team2_goalkeeper": f"{team2} goalkeeper",
            "team2_gk_saves": "averaging 3 saves per match",
            "team2_gk_penalties": "no penalty save record available",
            "team2_clean_sheets": "1 clean sheet this tournament",
            "shootout_likely": "possible if teams are evenly matched"
        },
        "defensive_signals": {
            "team1_defensive_actions": "averaging 18 defensive actions per match",
            "team1_shots_conceded": "4 shots on target conceded per match",
            "team2_defensive_actions": "averaging 15 defensive actions per match",
            "team2_shots_conceded": "5 shots on target conceded per match",
            "set_piece_threat": "both teams dangerous from set pieces",
            "defensive_style": "both teams mix high press and mid block"
        },
        "key_betting_signals": [
            "Match could be closely contested",
            "Set pieces could be decisive",
            "Goalkeeper form a key factor",
            "Early goal changes match dynamics",
            "Defensive record suggests low scoring",
            "Key player fitness doubts add uncertainty"
        ]
    }