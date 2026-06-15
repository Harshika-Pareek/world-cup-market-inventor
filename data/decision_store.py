# data/decision_store.py
import json
import os
from datetime import datetime

DECISIONS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "decisions.json"
)


def load_decisions() -> list:
    """Load all trader decisions."""
    if not os.path.exists(DECISIONS_FILE):
        return []
    with open(DECISIONS_FILE, "r") as f:
        data = json.load(f)
    return data.get("decisions", [])


def save_decision(
    match: str,
    market: dict,
    trader_decision: str,
    rejection_reason: str = None
):
    """
    Save trader decision.
    This IS the human in the loop feedback.
    Trader decisions become ground truth over time.
    Same pattern as RACM at Flutter where Finance
    reviewer decisions validated LLM outputs.
    """
    decisions = load_decisions()

    ai_recommendation = market.get("status", "UNKNOWN")
    ai_agrees = ai_recommendation == trader_decision

    decision = {
        "match": match,
        "market_name": market.get("market_name"),
        "description": market.get("description"),
        "ai_recommendation": ai_recommendation,
        "ai_confidence": market.get(
            "calculated_confidence", 0
        ),
        "trader_decision": trader_decision,
        "trader_agrees_with_ai": ai_agrees,
        "rejection_reason": rejection_reason,
        "settleable_score": market.get("settleable_score"),
        "fun_score": market.get("fun_score"),
        "exploit_risk": market.get("exploit_risk"),
        "ai_reasoning": market.get("reasoning"),
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    decisions.append(decision)

    with open(DECISIONS_FILE, "w") as f:
        json.dump({"decisions": decisions}, f, indent=2)

    print(f"Decision saved: {market.get('market_name')} "
          f"→ {trader_decision} ✅")

    return decision


def get_decisions_summary() -> dict:
    """Summary of all trader decisions."""
    decisions = load_decisions()

    if not decisions:
        return {
            "total": 0,
            "approved": 0,
            "rejected": 0,
            "agreement_rate": 0.0
        }

    approved = sum(
        1 for d in decisions
        if d.get("trader_decision") == "APPROVED"
    )
    rejected = sum(
        1 for d in decisions
        if d.get("trader_decision") == "REJECTED"
    )
    agreed = sum(
        1 for d in decisions
        if d.get("trader_agrees_with_ai")
    )
    agreement_rate = round(agreed / len(decisions), 2)

    return {
        "total": len(decisions),
        "approved": approved,
        "rejected": rejected,
        "agreement_rate": agreement_rate
    }
# Update data/decision_store.py save_decision function
# Add proper MLflow logging

def save_decision(
    match: str,
    market: dict,
    trader_decision: str,
    rejection_reason: str = None
):
    decisions = load_decisions()

    ai_recommendation = market.get("status", "UNKNOWN")
    ai_agrees = ai_recommendation == trader_decision

    decision = {
        "match": match,
        "market_name": market.get("market_name"),
        "description": market.get("description"),
        "ai_recommendation": ai_recommendation,
        "ai_confidence": market.get(
            "calculated_confidence", 0
        ),
        "trader_decision": trader_decision,
        "trader_agrees_with_ai": ai_agrees,
        "rejection_reason": rejection_reason,
        "settleable_score": market.get("settleable_score"),
        "fun_score": market.get("fun_score"),
        "exploit_risk": market.get("exploit_risk"),
        "ai_reasoning": market.get("reasoning"),
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    decisions.append(decision)

    with open(DECISIONS_FILE, "w") as f:
        json.dump({"decisions": decisions}, f, indent=2)

    # Log each trader decision to MLflow
    try:
        import mlflow
        from datetime import datetime as dt
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("WorldCup_Market_Inventor")

        timestamp = dt.now().strftime("%H%M%S")
        run_name = f"trader_decision_{timestamp}"

        with mlflow.start_run(run_name=run_name):
            mlflow.log_params({
                "match": match,
                "market": market.get("market_name", "")[:50],
                "ai_recommendation": ai_recommendation,
                "trader_decision": trader_decision,
                "rejection_reason": rejection_reason or "none"
            })
            mlflow.log_metrics({
                "trader_approved": 1 if trader_decision == "APPROVED" else 0,
                "trader_rejected": 1 if trader_decision == "REJECTED" else 0,
                "ai_trader_agreement": 1 if ai_agrees else 0,
                "ai_confidence": float(
                    market.get("calculated_confidence", 0)
                )
            })
        print(f"Decision logged to MLflow ✅")
    except Exception as e:
        print(f"MLflow decision logging skipped: {e}")

    print(
        f"Decision saved: {market.get('market_name')} "
        f"→ {trader_decision} ✅"
    )
    return decision