# pipeline/critic.py

import json
from llm_client import call_llm
from pipeline.schemas import Market


# =========================
# 1. RULE ENGINE (deterministic logic)
# =========================
def classify_market(market: dict) -> str:
    text = market.get("market_name", "").lower()

    if "referee" in text or "stadium" in text:
        return "TRIVIAL"

    if "yellow" in text or "red card" in text or "card" in text:
        return "DISCIPLINE"

    if "corner" in text or "possession" in text or "passes" in text:
        return "STATS"

    if "first goal" in text or "first half" in text:
        return "TIME"

    if "goalkeeper" in text or "save" in text:
        return "GOALKEEPER"

    return "GENERAL"


# =========================
# 2. LLM PROMPT (simplified, clean)
# =========================
def build_prompt(market: dict, category: str) -> str:
    return f"""
You are a senior betting market analyst.

Category: {category}

Market Name: {market.get('market_name')}
Description: {market.get('description')}

Return ONLY valid JSON:

{{
  "settleable_score": 0.0,
  "fun_score": 0.0,
  "exploit_risk": 0.0,
  "overall_confidence": 0.0,
  "reasoning": "one sentence explanation"
}}
"""


# =========================
# 3. DECISION ENGINE
# =========================
def decide(score: dict, category: str) -> str:
    conf = score.get("overall_confidence", 0)

    if category == "TRIVIAL":
        return "REJECT"

    if conf >= 0.8:
        return "APPROVE"

    if 0.5 <= conf < 0.8:
        return "REVIEW"

    return "REJECT"


# =========================
# 4. MAIN CRITIC FUNCTION
# =========================
def critique_market(market: dict) -> dict:
    try:
        category = classify_market(market)

        prompt = build_prompt(market, category)

        raw = call_llm(prompt, temperature=0.0, max_tokens=400)

        if raw is None:
            return fallback_critique(market)

        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)

        # clamp values (safety layer)
        for k in ["settleable_score", "fun_score", "exploit_risk", "overall_confidence"]:
            data[k] = max(0.0, min(1.0, float(data.get(k, 0.5))))

        # decision layer
        verdict = decide(data, category)

        # attach metadata
        data["market_name"] = market.get("market_name")
        data["description"] = market.get("description")
        data["category"] = category
        data["verdict"] = verdict

        # Pydantic validation (optional but strong)
        validated = Market(**data)

        return validated.model_dump()

    except Exception as e:
        print(f"[Critic Error] {e}")
        return fallback_critique(market)


# =========================
# 5. BATCH PROCESSING
# =========================
def critique_all_markets(markets: list) -> list:
    print(f"\n[Critic] Evaluating {len(markets)} markets...")

    results = []
    for i, m in enumerate(markets):
        print(f"  → {i+1}/{len(markets)}: {m.get('market_name')}")
        results.append(critique_market(m))

    return results


# =========================
# 6. FALLBACK SYSTEM (VERY IMPORTANT)
# =========================
def fallback_critique(market: dict) -> dict:
    return {
        "market_name": market.get("market_name", "Unknown"),
        "description": market.get("description", ""),
        "settleable_score": 0.5,
        "fun_score": 0.5,
        "exploit_risk": 0.5,
        "overall_confidence": 0.5,
        "category": "FALLBACK",
        "verdict": "REVIEW",
        "reasoning": "LLM failed → manual review required"
    }