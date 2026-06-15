# run_pipeline.py
import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)
))

from data.fetcher import fetch_match_news
from pipeline.extractor import extract_signals
from pipeline.generator import generate_markets
from pipeline.critic import critique_all_markets
from pipeline.ranker import rank_and_route
from tracking.tracker import log_run


def run_pipeline(team1: str, team2: str) -> dict:
    """
    Run complete 5-stage pipeline for one match.

    Stage 1: Fetch news (local txt + BBC RSS)
    Stage 2: Extract signals (LLM temp 0.0)
    Stage 3: Generate markets (LLM temp 0.8)
    Stage 4: Critique markets (LLM as judge temp 0.0)
    Stage 5: Rank and route (formula confidence)
    """
    print(f"\n{'='*60}")
    print(f"WORLD CUP MARKET INVENTOR")
    print(f"Match: {team1} vs {team2}")
    print(f"{'='*60}")

    start_time = time.time()

    # Stage 1
    print(f"\n[1/5] Fetching match news...")
    news = fetch_match_news(team1, team2)
    print(f"News loaded: {len(news)} characters")

    # Stage 2
    print(f"\n[2/5] Extracting signals...")
    signals = extract_signals(news, team1, team2)
    print(f"Signals: "
          f"{len(signals.get('key_betting_signals', []))} "
          f"key signals found")

    # Stage 3
    print(f"\n[3/5] Generating novel markets...")
    markets = generate_markets(signals, team1, team2)
    print(f"Markets generated: {len(markets)}")

    # Stage 4
    print(f"\n[4/5] Critiquing markets...")
    critiqued = critique_all_markets(markets)

    # Stage 5
    print(f"\n[5/5] Ranking and routing...")
    results = rank_and_route(critiqued)

    latency = round(time.time() - start_time, 2)

    # Log to MLflow
    log_run(f"{team1} vs {team2}", results, latency)

    # Print results
    print(f"\n{'='*60}")
    print(f"RESULTS: {team1} vs {team2}")
    print(f"Time: {latency} seconds")
    print(f"{'='*60}")

    print(f"\n✅ APPROVED ({len(results['approved'])}):")
    for m in results["approved"]:
        print(f"   • {m['market_name']}")
        print(f"     {m.get('confidence_explanation', '')}")

    print(f"\n⚠️  REVIEW ({len(results['review'])}):")
    for m in results["review"]:
        print(f"   • {m['market_name']}")
        print(f"     {m.get('confidence_explanation', '')}")

    print(f"\n❌ REJECTED ({len(results['rejected'])}):")
    for m in results["rejected"]:
        print(f"   • {m['market_name']}")
        print(f"     {m.get('confidence_explanation', '')}")

    print(f"\n{'='*60}")
    print(f"Total: {results['total']} | "
          f"Approval rate: {results['approval_rate']*100:.0f}%")
    print(f"{'='*60}\n")

    return results, signals


if __name__ == "__main__":
    run_pipeline("England", "Croatia")
    print("\n" + "="*60 + "\n")
    run_pipeline("Argentina", "France")