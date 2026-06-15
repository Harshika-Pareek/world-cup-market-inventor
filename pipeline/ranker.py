# pipeline/ranker.py


def calculate_confidence(market: dict) -> float:
    """
    Formula based confidence calculation.

    Formula: settleable×0.5 + fun×0.3 + (1-exploit)×0.2

    SAME formula as evaluator.py — critical.
    Evaluation tests exactly what production does.
    If formulas differ — evaluation is meaningless.

    Why these weights:
    settleable 50%: cannot offer unsettleable market
    fun 30%: no fun = no bets = no revenue
    exploit 20%: inverted, manageable with price updates

    Why formula not raw LLM confidence:
    LLM score varies run to run even at temp 0.0
    Formula is deterministic — same inputs same output
    Trader can verify any score manually in seconds
    Regulator can audit any routing decision
    """
    settleable = float(
        market.get("settleable_score", 0.5)
    )
    fun = float(
        market.get("fun_score", 0.5)
    )
    exploit = float(
        market.get("exploit_risk", 0.5)
    )

    confidence = (
        settleable * 0.5 +
        fun * 0.3 +
        (1 - exploit) * 0.2
    )
    return round(confidence, 2)


def explain_confidence(market: dict,
                       confidence: float) -> str:
    """
    Plain English explanation for trader.

    Why this matters:
    Trader does not just see a number.
    They see exactly WHY the market scored as it did.
    Builds trust. Enables informed decisions.
    Satisfies regulatory audit requirements.

    No vague reasoning — specific actionable labels.
    """
    settleable = float(
        market.get("settleable_score", 0.5)
    )
    fun = float(
        market.get("fun_score", 0.5)
    )
    exploit = float(
        market.get("exploit_risk", 0.5)
    )

    parts = []

    # Settleable label
    if settleable >= 0.8:
        parts.append("Clearly settleable ✅")
    elif settleable >= 0.5:
        parts.append("Needs data provider ⚠️")
    else:
        parts.append("Hard to settle ❌")

    # Fun label
    if fun >= 0.7:
        parts.append("Fans will enjoy ✅")
    elif fun >= 0.5:
        parts.append("Moderate appeal ⚠️")
    else:
        parts.append("Low fan interest ❌")

    # Exploit label
    if exploit <= 0.3:
        parts.append("Low exploit risk ✅")
    elif exploit <= 0.6:
        parts.append("Moderate exploit risk ⚠️")
    else:
        parts.append("High exploit risk ❌")

    return f"Score {confidence} | " + " | ".join(parts)


def route_market(market: dict) -> str:
    """
    Route market to correct bucket.

    Two types of rules:

    HARD RULES (override everything):
    Cannot settle = REJECTED always
    Reason: paying out disputed markets
    costs money and damages trust

    Too exploitable = REJECTED always
    Reason: sharp bettors drain revenue
    and pricing team cannot manage safely

    CONFIDENCE ROUTING (for everything else):
    >= 0.75 = APPROVED
    Trader glances and publishes
    10 seconds human time

    0.5 to 0.74 = REVIEW
    Trader reads reasoning carefully
    2-3 minutes human time

    < 0.5 = REJECTED
    Trader never sees this
    0 seconds human time

    This is human in the loop properly:
    AI handles clear cases automatically
    Human focuses on genuinely uncertain cases
    Same pattern as RACM at Flutter
    """
    confidence = market.get(
        "calculated_confidence", 0
    )
    settleable = float(
        market.get("settleable_score", 0)
    )
    exploit = float(
        market.get("exploit_risk", 1)
    )

    # Hard rule 1 — cannot settle = always reject
    if settleable < 0.4:
        return "REJECTED"

    # Hard rule 2 — too exploitable = always reject
    if exploit > 0.85:
        return "REJECTED"

    # Confidence routing
    if confidence >= 0.75:
        return "APPROVED"
    elif confidence >= 0.5:
        return "REVIEW"
    else:
        return "REJECTED"


def rank_and_route(markets: list) -> dict:
    """
    Stage 4: Rank and route all critiqued markets.

    Process per market:
    1. Calculate formula confidence
    2. Generate plain English explanation
    3. Apply hard rules then confidence routing
    4. Add to correct bucket

    Why sort approved by confidence:
    Best market appears at top of trader view.
    Trader sees highest quality first.
    Reduces cognitive load.

    Business value:
    Without ranker: trader evaluates 8 markets manually
    Time: 40 minutes per match
    With ranker: trader reviews 2 borderline markets
    Time: 4 minutes per match
    Saving: 90% of trader evaluation time
    64 World Cup matches: ~38 hours saved
    """
    print(
        f"\n[Stage 4] Ranking and routing "
        f"{len(markets)} markets..."
    )

    approved = []
    review = []
    rejected = []

    for market in markets:

        # Step 1 — Calculate formula confidence
        calculated = calculate_confidence(market)
        market["calculated_confidence"] = calculated

        # Step 2 — Generate explanation
        market["confidence_explanation"] = (
            explain_confidence(market, calculated)
        )

        # Step 3 — Route to bucket
        decision = route_market(market)
        market["status"] = decision

        # Step 4 — Add to correct bucket
        if decision == "APPROVED":
            approved.append(market)
        elif decision == "REVIEW":
            review.append(market)
        else:
            rejected.append(market)

    # Sort approved by confidence — best first
    approved.sort(
        key=lambda x: x.get(
            "calculated_confidence", 0
        ),
        reverse=True
    )

    total = len(markets)
    approval_rate = (
        len(approved) / total if total > 0 else 0
    )

    print(
        f"✅ Approved: {len(approved)} | "
        f"⚠️  Review: {len(review)} | "
        f"❌ Rejected: {len(rejected)}"
    )

    return {
        "approved": approved,
        "review": review,
        "rejected": rejected,
        "total": total,
        "approval_rate": round(approval_rate, 2)
    }