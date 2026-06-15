# pipeline/critic.py
import json
from llm_client import call_llm
from pipeline.schemas import Market


# =========================
# 1. RULE ENGINE (deterministic)
# Classifies market BEFORE LLM call.
# No tokens used here.
# Fast. Consistent. Auditable.
# =========================
def classify_market(market: dict) -> str:
    """
    Deterministic keyword classification.
    Checks both market name AND description.
    Runs before LLM — zero token cost.

    Why deterministic not LLM:
    Classification must be consistent.
    Same market = same category every time.
    LLM classification varies run to run.
    """
    text = (
        market.get("market_name", "") + " " +
        market.get("description", "")
    ).lower()

    if any(w in text for w in [
        "referee", "stadium", "coin toss",
        "kickoff time", "nationality", "weather"
    ]):
        return "TRIVIAL"

    if any(w in text for w in [
        "yellow card", "red card", "booking",
        "sent off", "foul", "discipline", "card"
    ]):
        return "DISCIPLINE"

    if any(w in text for w in [
        "corner", "possession", "passes",
        "tackles", "shots", "crosses", "duels"
    ]):
        return "STATS"

    if any(w in text for w in [
        "first goal", "first half", "minute",
        "before", "within", "last 20", "opening",
        "early", "half time"
    ]):
        return "TIME"

    if any(w in text for w in [
        "goalkeeper", "save", "clean sheet",
        "penalty shootout", "keeper", "gk",
        "shot stopping", "saves"
    ]):
        return "GOALKEEPER"

    if any(w in text for w in [
        "formation", "tactical", "switch",
        "system", "shape", "4-3-3", "4-2-3-1"
    ]):
        return "TACTICAL"

    if any(w in text for w in [
        "score", "goal", "win", "result",
        "both teams", "extra time", "shootout"
    ]):
        return "OUTCOME"

    return "GENERAL"


# =========================
# 2. PROMPT BUILDER (category aware)
# LLM gets focused context per category.
# Better scores from focused prompt.
# =========================
def build_prompt(market: dict, category: str) -> str:
    """
    Build category-aware prompt.
    LLM knows which type of market it is evaluating.
    Focused prompt = more accurate scores.

    Alternative: one generic prompt for all categories.
    Rejected: LLM spreads attention across all rules.
    Category-aware prompt = LLM focuses on relevant criteria.
    """

    category_guidance = {
        "TRIVIAL": (
            "This is a TRIVIAL market. "
            "Trivial markets are about non-match events "
            "(referee, stadium, weather). "
            "fun_score MUST be below 0.2. "
            "overall_confidence MUST be below 0.4. "
            "Nobody bets on these."
        ),
        "DISCIPLINE": (
            "This is a DISCIPLINE market (cards/bookings). "
            "These are ESTABLISHED safe markets. "
            "settleable_score: 0.95 to 1.0 (official record). "
            "exploit_risk: 0.2 to 0.35 (cannot predict referee). "
            "fun_score: 0.7 to 0.85 (fans enjoy card drama). "
            "overall_confidence: 0.78 to 0.88."
        ),
        "STATS": (
            "This is a STATS market (corners/possession/passes). "
            "These need careful pricing. "
            "exploit_risk: 0.4 to 0.6 "
            "(match situation gives late information edge). "
            "settleable_score: 0.7 to 0.9 (needs data provider). "
            "overall_confidence: 0.55 to 0.70 (borderline)."
        ),
        "TIME": (
            "This is a TIME-BASED market. "
            "These are POPULAR proven markets. "
            "settleable_score: 0.95 to 1.0 (perfectly clear). "
            "fun_score: 0.8 to 0.9 (fans love time tension). "
            "exploit_risk: 0.2 to 0.35 (cannot predict timing). "
            "overall_confidence: 0.80 to 0.92."
        ),
        "GOALKEEPER": (
            "This is a GOALKEEPER market. "
            "These are ESTABLISHED safe markets. "
            "settleable_score: 0.85 to 1.0 (clear from stats). "
            "exploit_risk: 0.1 to 0.3 "
            "(cannot influence goalkeeper saves). "
            "fun_score: 0.7 to 0.9 (fans love GK drama). "
            "overall_confidence: 0.80 to 0.92."
        ),
        "TACTICAL": (
            "This is a TACTICAL market (formations/systems). "
            "These are RISKY markets. "
            "settleable_score: 0.2 to 0.5 (very ambiguous). "
            "exploit_risk: 0.6 to 0.8 (tactical insiders). "
            "overall_confidence: 0.15 to 0.40 (usually reject)."
        ),
        "OUTCOME": (
            "This is an OUTCOME market (goals/results). "
            "Standard market type. "
            "settleable_score: 0.9 to 1.0 (very clear). "
            "exploit_risk: 0.3 to 0.5 (standard risk). "
            "fun_score: 0.7 to 0.9 (fans love results). "
            "overall_confidence: 0.70 to 0.88."
        ),
        "GENERAL": (
            "Evaluate this market on its own merits. "
            "Be strict. Not every market is good."
        )
    }

    guidance = category_guidance.get(
        category,
        category_guidance["GENERAL"]
    )

    return f"""
You are a senior betting market analyst.

MARKET CATEGORY: {category}
CATEGORY GUIDANCE: {guidance}

MARKET TO EVALUATE:
Name: {market.get('market_name')}
Description: {market.get('description')}

Score each from 0.0 to 1.0.
Follow the category guidance above strictly.
Return ONLY valid JSON. No markdown.

{{
    "settleable_score": 0.0,
    "fun_score": 0.0,
    "exploit_risk": 0.0,
    "overall_confidence": 0.0,
    "reasoning": "one sentence explaining verdict"
}}

SCORING REMINDER:
settleable_score: can we objectively determine winner?
fun_score: would casual fan enjoy this bet?
exploit_risk: can experts beat our pricing? (high = bad)
overall_confidence: should we offer this market?
"""


# =========================
# 3. DECISION ENGINE (deterministic)
# Category rules override confidence score.
# Business rules in Python not LLM.
# Fully auditable. Always consistent.
# =========================
def decide(score: dict, category: str) -> str:
    """
    Deterministic routing decision.

    Why Python not LLM for this decision:
    Business rules must be consistent.
    TRIVIAL must always reject.
    LLM might approve a trivial market one day.
    Python rule never changes.

    Two types of rules:
    Category overrides: based on market type
    Score overrides: based on numeric thresholds
    Confidence routing: for everything else
    """
    conf = float(score.get("overall_confidence", 0))
    settleable = float(score.get("settleable_score", 0))
    exploit = float(score.get("exploit_risk", 1))

    # Category hard overrides
    if category == "TRIVIAL":
        return "REJECTED"  # always — no exceptions

    if category == "TACTICAL":
        return "REJECTED"  # always — too ambiguous

    if category == "STATS":
        return "REVIEW"  # never auto-approve stats needs trader review always
     

    # Score hard overrides
    if settleable < 0.4:
        return "REJECTED"  # cannot settle = always reject

    if exploit > 0.85:
        return "REJECTED"  # too exploitable = always reject

    # Confidence routing
    if conf >= 0.75:
        return "APPROVED"
    elif conf >= 0.5:
        return "REVIEW"
    else:
        return "REJECTED"


# =========================
# 4. MAIN CRITIC FUNCTION
# Orchestrates all four layers.
# LLM only provides scores.
# Business decisions in Python.
# =========================
def critique_market(market: dict) -> dict:
    """
    Four layer critic:
    1. Classify market (deterministic)
    2. Build focused prompt (category aware)
    3. Call LLM for scores (AI layer)
    4. Make routing decision (deterministic)

    LLM scores. Python decides.
    No black box. Fully auditable.
    Same pattern as RACM at Flutter:
    AI recommends. Business rules decide.
    Human reviews uncertain cases.
    """
    try:
        # Layer 1 — classify
        category = classify_market(market)

        # Layer 2 — build prompt
        prompt = build_prompt(market, category)

        # Layer 3 — LLM scores
        raw = call_llm(
            prompt,
            temperature=0.0,
            max_tokens=400
        )

        if raw is None:
            return fallback_critique(market)

        # Clean markdown
        raw = raw.replace(
            "```json", ""
        ).replace("```", "").strip()

        data = json.loads(raw)

        # Clamp all scores 0.0 to 1.0
        for k in [
            "settleable_score",
            "fun_score",
            "exploit_risk",
            "overall_confidence"
        ]:
            data[k] = max(
                0.0, min(1.0, float(data.get(k, 0.5)))
            )

        # Layer 4 — deterministic decision
        verdict = decide(data, category)

        # Attach metadata
        data["market_name"] = market.get("market_name")
        data["description"] = market.get("description")
        data["category"] = category
        data["verdict"] = verdict

        # Pydantic validation
        try:
            validated = Market(**data)
            return validated.model_dump()
        except Exception:
            return data

    except json.JSONDecodeError as e:
        print(f"[Critic] JSON error: {e}")
        return fallback_critique(market)

    except Exception as e:
        print(f"[Critic] Error: {e}")
        return fallback_critique(market)


# =========================
# 5. BATCH PROCESSING
# =========================
def critique_all_markets(markets: list) -> list:
    """
    Critique all markets one by one.

    Why sequential not parallel:
    Simple and reliable for prototype.
    Production: async parallel calls
    reduces N×latency to ~1×latency.
    """
    print(
        f"\n[Stage 3] Critiquing "
        f"{len(markets)} markets..."
    )
    results = []
    for i, m in enumerate(markets):
        print(
            f"  → {i+1}/{len(markets)}: "
            f"{m.get('market_name')}"
        )
        results.append(critique_market(m))
    print("Critique complete ✅")
    return results


# =========================
# 6. FALLBACK
# Returns 0.5 scores → routes to REVIEW
# Safe middle ground when LLM fails
# Trader reviews rather than auto decision
# =========================
def fallback_critique(market: dict) -> dict:
    """
    Fallback when LLM fails.
    Returns 0.5 scores → REVIEW queue.
    Trader reviews rather than auto approve/reject.
    Safe default — never auto-publishes on failure.
    """
    return {
        "market_name": market.get(
            "market_name", "Unknown"
        ),
        "description": market.get("description", ""),
        "settleable_score": 0.5,
        "fun_score": 0.5,
        "exploit_risk": 0.5,
        "overall_confidence": 0.5,
        "category": "FALLBACK",
        "verdict": "REVIEW",
        "reasoning": (
            "LLM evaluation failed — "
            "manual trader review required"
        )
    }