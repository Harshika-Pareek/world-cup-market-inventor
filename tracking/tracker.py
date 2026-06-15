# tracking/tracker.py
import mlflow
import os

# Use SQLite — same as evaluator.py
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("WorldCup_Market_Inventor")


def log_run(match: str, results: dict, latency: float):
    """
    Log pipeline run metrics to MLflow.
    Enables drift detection across runs.
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%H%M%S")
        run_name = f"{match}_{timestamp}"

        with mlflow.start_run(run_name=run_name):
            mlflow.log_params({
                "match": match,
                "model": "llama-3.3-70b-versatile",
                "temperature_generation": 0.8,
                "temperature_critique": 0.0,
                "approve_threshold": 0.75,
                "review_threshold": 0.5
            })
            mlflow.log_metrics({
                "total_markets": results["total"],
                "approved": len(results["approved"]),
                "review": len(results["review"]),
                "rejected": len(results["rejected"]),
                "approval_rate": results["approval_rate"],
                "latency_seconds": latency
            })
        print(f"MLflow logged  ({run_name})")
    except Exception as e:
        print(f"MLflow logging failed: {e}")