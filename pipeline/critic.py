# pipeline/critic.py
import json
from llm_client import call_llm


def critique_market(market: dict) -> dict:
    """
    Evaluate a single betting market.

    Design decisions:
    - Temperature 0.0: evaluation needs consistency
      Same market should get same score every time
    - LLM as judge: understands nuance rules cannot catch
    - Five rules: trivial, goalkeeper, subjective,
      tactical, time-based
    - Fallback: returns 0.5 scores if LLM fails

    Alternative approaches:
    - Rule based scoring: brittle, misses nuanced cases
    - Human evaluation only: does not scale
    - Separate smaller model: good for production cost saving
    """

    prompt = f"""
You are a senior betting market analyst at a
World Cup trading company.
Evaluate this betting market STRICTLY and HONESTLY.
Not every market is good. Be critical.

MARKET TO EVALUATE:
Name: {market.get('market_name')}
Description: {market.get('description')}

MANDATORY RULES — apply these before scoring:

Rule 1 — TRIVIAL MARKETS:
Referee details, stadium info, coin toss,
kick off time = fun_score below 0.2,
overall_confidence below 0.4.
Nobody bets on these. They waste market slots.

Rule 2 — GOALKEEPER MARKETS:
Goalkeeper saves, clean sheets, penalty saves,
penalty shootout markets are ESTABLISHED and SAFE.
exploit_risk = 0.1 to 0.3
(customers cannot influence whether goalkeeper saves)
settleable_score = 0.85 to 1.0
(clear from official stats)
overall_confidence = 0.80 to 0.92
Do NOT score these as high exploit risk.

Rule 3 — SUBJECTIVE MARKETS:
Most creative, most entertaining, best performance
= settleable_score below 0.2
= overall_confidence below 0.3
These always cause customer disputes.

Rule 4 — TACTICAL AND FORMATION MARKETS:
Formation changes, tactical switches
= settleable_score below 0.5
Too ambiguous to settle fairly.

Rule 5 — TIME BASED MARKETS:
First goal before X minutes, goals in first half
= settleable_score 0.95 to 1.0
= fun_score 0.8 to 0.9
= exploit_risk 0.2 to 0.35
These are proven popular markets.

Score each dimension from 0.0 to 1.0.
Return ONLY valid JSON. No markdown. No explanation.

{{
    "market_name": "{market.get('market_name')}",
    "description": "{market.get('description')}",
    "settleable_score": 0.0,
    "fun_score": 0.0,
    "exploit_risk": 0.0,
    "overall_confidence": 0.0,
    "reasoning": "one clear sentence explaining verdict"
}}

SCORING GUIDE:
settleable_score: objectively determine winner?
1.0=perfectly clear | 0.5=needs data | 0.0=impossible

fun_score: casual fan enjoy this bet?
1.0=very exciting | 0.5=moderate | 0.0=boring

exploit_risk: experts exploit easily?
1.0=very exploitable BAD | 0.5=moderate | 0.0=safe GOOD

overall_confidence: offer to customers?
1.0=definitely yes | 0.5=borderline | 0.0=definitely no
"""

    try:
        raw = call_llm(prompt, temperature=0.0, max_tokens=400)

        if raw is None:
            return fallback_critique(market)

        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)

        for score_field in [
            "settleable_score",
            "fun_score",
            "exploit_risk",
            "overall_confidence"
        ]:
            score = result.get(score_field, 0.5)
            result[score_field] = max(
                0.0, min(1.0, float(score))
            )

        return result

    except json.JSONDecodeError as e:
        print(f"JSON parse failed for "
              f"{market.get('market_name')}: {e}")
        return fallback_critique(market)

    except Exception as e:
        print(f"Critique failed for "
              f"{market.get('market_name')}: {e}")
        return fallback_critique(market)


def critique_all_markets(markets: list) -> list:
    """
    Critique all markets one by one.

    Why sequential not parallel:
    Simple and reliable for prototype.
    Production version would use async
    parallel calls to reduce latency
    from N*latency to ~1*latency.
    """
    print(f"\n[Stage 3] Critiquing {len(markets)} markets...")

    results = []
    for i, market in enumerate(markets):
        print(f"  Critiquing {i+1}/{len(markets)}: "
              f"{market.get('market_name')}")
        result = critique_market(market)
        results.append(result)

    print(f"Critique complete ✅")
    return results


def fallback_critique(market: dict) -> dict:
    """
    Fallback if LLM critique fails.
    Returns 0.5 scores — routes to human review.
    Safe middle ground when evaluation fails.
    Trader reviews rather than auto approve or reject.
    """
    return {
        "market_name": market.get("market_name", "Unknown"),
        "description": market.get("description", ""),
        "settleable_score": 0.5,
        "fun_score": 0.5,
        "exploit_risk": 0.5,
        "overall_confidence": 0.5,
        "reasoning": "Auto-evaluation failed — manual trader review required"
    }