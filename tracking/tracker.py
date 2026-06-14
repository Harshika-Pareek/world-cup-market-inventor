# tracking/tracker.py — complete updated version

import mlflow
import os

# Fix Windows path issue
os.makedirs("mlruns", exist_ok=True)
mlflow.set_tracking_uri("mlruns")
mlflow.set_experiment("WorldCup_Market_Inventor")

def log_run(match: str, results: dict, latency: float):
    """Log pipeline run to MLflow."""
    try:
        with mlflow.start_run(run_name=match):
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
        print(f"MLflow logged")
    except Exception as e:
        print(f"MLflow logging failed: {e}")