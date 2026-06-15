# evaluation/evaluator.py

import sys
import os
import json

# Fix 1: Add project root to Python path
project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, project_root)

# Fix 2: Change working directory to project root
os.chdir(project_root)

# Fix 3: Set MLflow tracking URI once
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("WorldCup_Market_Inventor")


def load_golden_dataset() -> list:
    """Load golden dataset from JSON file."""
    filepath = os.path.join(
        project_root, "data", "golden_dataset.json"
    )
    print(f"Loading from: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    print(f"Loaded {len(data['markets'])} golden markets")
    return data["markets"]


def calculate_confidence(market: dict) -> float:
    """
    Formula based confidence.
    Settleable 50% + Fun 30% + (1-Exploit) 20%
    """
    settleable = float(market.get("settleable_score", 0.5))
    fun = float(market.get("fun_score", 0.5))
    exploit = float(market.get("exploit_risk", 0.5))
    confidence = (
        settleable * 0.5 +
        fun * 0.3 +
        (1 - exploit) * 0.2
    )
    return round(confidence, 2)


def get_verdict(confidence: float,
                settleable: float,
                exploit: float) -> str:
    """Same routing logic as ranker.py."""
    if settleable < 0.4:
        return "REJECTED"
    if exploit > 0.85:
        return "REJECTED"
    if confidence >= 0.75:
        return "APPROVED"
    elif confidence >= 0.5:
        return "REVIEW"
    else:
        return "REJECTED"


def evaluate_critic() -> dict:
    """
    Compare LLM critic scores against golden dataset.
    Proves confidence scores are trustworthy.
    Same as unit testing in software engineering.
    """
    from pipeline.critic import critique_market

    print("\n" + "="*55)
    print("GOLDEN DATASET EVALUATION")
    print("="*55)

    golden = load_golden_dataset()
    results = []
    correct_verdicts = 0
    score_diffs = []
    category_results = {}

    for gold in golden:
        market = {
            "market_name": gold["market_name"],
            "description": gold["description"]
        }

        print(f"\nEvaluating: {gold['market_name']}")
        llm_result = critique_market(market)

        llm_confidence = calculate_confidence(llm_result)
        llm_settleable = float(
            llm_result.get("settleable_score", 0.5)
        )
        llm_exploit = float(
            llm_result.get("exploit_risk", 0.5)
        )
        llm_verdict = get_verdict(
            llm_confidence, llm_settleable, llm_exploit
        )

        expert_scores = gold["expert_scores"]
        expert_confidence = float(
            expert_scores["overall_confidence"]
        )
        expert_verdict = gold["expert_verdict"]
        category = gold.get("category", "unknown")

        verdict_correct = llm_verdict == expert_verdict
        if verdict_correct:
            correct_verdicts += 1

        score_diff = abs(llm_confidence - expert_confidence)
        score_diffs.append(score_diff)

        if category not in category_results:
            category_results[category] = {
                "correct": 0, "total": 0
            }
        category_results[category]["total"] += 1
        if verdict_correct:
            category_results[category]["correct"] += 1

        status = "✅" if verdict_correct else "❌"
        print(f"{status} {gold['market_name']}")
        print(f"   Category:          {category}")
        print(f"   LLM confidence:    {llm_confidence}")
        print(f"   Expert confidence: {expert_confidence}")
        print(f"   Score difference:  {score_diff:.3f}")
        print(f"   LLM verdict:       {llm_verdict}")
        print(f"   Expert verdict:    {expert_verdict}")
        print(f"   LLM reasoning:     "
              f"{llm_result.get('reasoning', 'none')}")

        results.append({
            "market": gold["market_name"],
            "category": category,
            "verdict_correct": verdict_correct,
            "llm_confidence": llm_confidence,
            "expert_confidence": expert_confidence,
            "score_difference": round(score_diff, 3),
            "llm_verdict": llm_verdict,
            "expert_verdict": expert_verdict,
            "llm_reasoning": llm_result.get("reasoning", "")
        })

    total = len(golden)
    accuracy = correct_verdicts / total
    avg_diff = sum(score_diffs) / len(score_diffs)

    print(f"\n{'='*55}")
    print(f"OVERALL RESULTS")
    print(f"{'='*55}")
    print(f"Verdict accuracy:     {accuracy*100:.0f}%")
    print(f"Avg score difference: {avg_diff:.3f}")
    print(f"Correct verdicts:     {correct_verdicts}/{total}")

    print(f"\n{'='*55}")
    print(f"ACCURACY BY CATEGORY")
    print(f"{'='*55}")
    for cat, data in category_results.items():
        cat_accuracy = data["correct"] / data["total"]
        bar = "█" * int(cat_accuracy * 10)
        empty = "░" * (10 - int(cat_accuracy * 10))
        print(f"{cat:20} {bar}{empty} "
              f"{cat_accuracy*100:.0f}% "
              f"({data['correct']}/{data['total']})")

    failures = [r for r in results
                if not r["verdict_correct"]]
    if failures:
        print(f"\n{'='*55}")
        print(f"MISMATCHES TO INVESTIGATE ({len(failures)})")
        print(f"{'='*55}")
        for f in failures:
            print(f"\n❌ {f['market']}")
            print(f"   LLM said:    {f['llm_verdict']} "
                  f"({f['llm_confidence']})")
            print(f"   Expert said: {f['expert_verdict']} "
                  f"({f['expert_confidence']})")
            print(f"   Fix: adjust critic prompt "
                  f"for {f['category']} markets")

    log_to_mlflow(accuracy, avg_diff, results)
    print(f"\n{'='*55}")

    return {
        "accuracy": accuracy,
        "avg_difference": avg_diff,
        "correct_verdicts": correct_verdicts,
        "total": total,
        "results": results,
        "category_results": category_results
    }


# evaluation/evaluator.py
# Update log_to_mlflow function

def log_to_mlflow(accuracy: float,
                  avg_diff: float,
                  results: list):
    try:
        from datetime import datetime
        import mlflow

        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("WorldCup_Market_Inventor")

        # Add timestamp so each run is unique
        timestamp = datetime.now().strftime("%H%M%S")
        run_name = f"evaluation_{timestamp}"

        with mlflow.start_run(run_name=run_name):
            mlflow.log_metrics({
                "verdict_accuracy": accuracy,
                "avg_score_difference": avg_diff,
                "markets_evaluated": len(results)
            })
            results_path = os.path.join(
                project_root,
                "evaluation_results.json"
            )
            with open(results_path, "w") as f:
                json.dump(results, f, indent=2)
            mlflow.log_artifact(results_path)

        print(f"Evaluation logged to MLflow ({run_name})")

    except Exception as e:
        print(f"MLflow logging skipped: {e}")

if __name__ == "__main__":
    evaluate_critic()