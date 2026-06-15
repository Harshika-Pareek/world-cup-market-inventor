# app.py
import streamlit as st
import sys
import os
import time

sys.path.insert(0, os.path.dirname(
    os.path.abspath(__file__)
))

from data.fetcher import fetch_match_news
from data.decision_store import (
    save_decision,
    get_decisions_summary
)
from pipeline.extractor import extract_signals
from pipeline.generator import generate_markets
from pipeline.critic import critique_all_markets
from pipeline.ranker import rank_and_route
from tracking.tracker import log_run

st.set_page_config(
    page_title="World Cup Market Inventor",
    page_icon="⚽",
    layout="wide"
)

# Initialise session state
if "results" not in st.session_state:
    st.session_state.results = None
if "signals" not in st.session_state:
    st.session_state.signals = None
if "match_label" not in st.session_state:
    st.session_state.match_label = None
if "decisions_made" not in st.session_state:
    st.session_state.decisions_made = {}

# Sidebar — always reads fresh from file
with st.sidebar:
    st.header("⚽ World Cup 2026")
    st.subheader("AI Market Inventor")
    st.divider()

    st.header("📊 Trader Decisions")
    summary = get_decisions_summary()
    st.metric("Total", summary["total"])
    st.metric("✅ Approved", summary["approved"])
    st.metric("❌ Rejected", summary["rejected"])

    if summary["total"] > 0:
        st.metric(
            "🤝 Agreement Rate",
            f"{summary['agreement_rate']*100:.0f}%"
        )

    st.divider()
    st.markdown("""
    **Pipeline stages:**
    1. Fetcher
    2. Extractor
    3. Generator
    4. Critic
    5. Ranker
    """)
    st.divider()
    st.caption("MLflow: http://127.0.0.1:5000")

# Main title
st.title("⚽ World Cup 2026 — AI Market Inventor")
st.caption(
    "Novel betting market generation with "
    "signal extraction, LLM self-critique, "
    "confidence scoring and human governance"
)

# Match selector
# In app.py replace match selector section with:

st.header("1️⃣ Select Match")

match_type = st.radio(
    "How to select match:",
    ["Choose from list", "Enter any match"],
    horizontal=True
)

if match_type == "Choose from list":
    matches = {
        "England vs Croatia — Group B": (
            "England", "Croatia"
        ),
        "Argentina vs France — World Cup Final": (
            "Argentina", "France"
        )
    }
    selected = st.selectbox(
        "Choose match:",
        list(matches.keys())
    )
    team1, team2 = matches[selected]

else:
    col1, col2 = st.columns(2)
    team1 = col1.text_input(
        "Team 1:",
        placeholder="e.g. Brazil"
    )
    team2 = col2.text_input(
        "Team 2:",
        placeholder="e.g. Germany"
    )
    if not team1 or not team2:
        st.warning(
            "Please enter both team names"
        )
        st.stop()

st.info(
    f"Generating markets for "
    f"**{team1} vs {team2}**"
)

# Generate button
if st.button(
    "🚀 Generate Novel Markets",
    type="primary",
    use_container_width=True
):
    # Clear previous results
    st.session_state.decisions_made = {}

    start_time = time.time()
    progress = st.progress(0)
    status = st.empty()

    status.text("Stage 1/5: Fetching news...")
    news = fetch_match_news(team1, team2)
    progress.progress(20)

    status.text("Stage 2/5: Extracting signals...")
    signals = extract_signals(news, team1, team2)
    progress.progress(40)

    status.text("Stage 3/5: Generating markets...")
    markets = generate_markets(signals, team1, team2)
    progress.progress(60)

    status.text("Stage 4/5: Critiquing markets...")
    critiqued = critique_all_markets(markets)
    progress.progress(80)

    status.text("Stage 5/5: Ranking and routing...")
    results = rank_and_route(critiqued)
    progress.progress(100)

    latency = round(time.time() - start_time, 2)
    status.text(f"✅ Done in {latency}s")

    # Save to session state
    st.session_state.results = results
    st.session_state.signals = signals
    st.session_state.match_label = (
        f"{team1} vs {team2}"
    )

    log_run(f"{team1} vs {team2}", results, latency)

# Show results if they exist in session state
if st.session_state.results is not None:

    results = st.session_state.results
    signals = st.session_state.signals
    match_label = st.session_state.match_label

    st.divider()

    # Signal summary
    st.header("3️⃣ Signal Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{team1}")
        st.write(f"**Form:** {signals.get('team1_form')}")
        st.write(
            f"**Tactics:** "
            f"{signals.get('team1_tactics')}"
        )
        gk = signals.get("goalkeeper_signals", {})
        st.write(
            f"**GK:** "
            f"{gk.get('team1_goalkeeper')}"
        )

    with col2:
        st.subheader(f"{team2}")
        st.write(f"**Form:** {signals.get('team2_form')}")
        st.write(
            f"**Tactics:** "
            f"{signals.get('team2_tactics')}"
        )
        st.write(
            f"**GK:** "
            f"{gk.get('team2_goalkeeper')}"
        )

    # Injuries
    injuries = signals.get("key_injuries", [])
    if injuries:
        st.subheader("🏥 Injuries")
        for injury in injuries:
            st.warning(
                f"**{injury.get('player')}** "
                f"({injury.get('team')}) — "
                f"{injury.get('status')}: "
                f"{injury.get('impact')}"
            )

    # Betting signals
    betting = signals.get("key_betting_signals", [])
    if betting:
        st.subheader("💡 Key Betting Signals")
        cols = st.columns(2)
        for i, s in enumerate(betting):
            cols[i % 2].info(f"→ {s}")

    st.divider()

    # Metrics
    st.header("4️⃣ Results Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", results["total"])
    c2.metric("✅ Approved", len(results["approved"]))
    c3.metric("⚠️ Review", len(results["review"]))
    c4.metric("❌ Rejected", len(results["rejected"]))

    st.divider()
    st.header("5️⃣ Trader Review")

    # Helper to show market card
    def show_market(market, bucket, idx):
        key = market["market_name"]

        # Check if decision already made
        if key in st.session_state.decisions_made:
            decision = st.session_state.decisions_made[key]
            if decision == "APPROVED":
                st.success(
                    f"✅ {key} — APPROVED by trader"
                )
            else:
                st.error(
                    f"❌ {key} — REJECTED by trader"
                )
            return

        conf = market.get("calculated_confidence")
        icon = "✅" if bucket == "approved" else "⚠️"

        with st.expander(
            f"{icon} {key} — Confidence: {conf}",
            expanded=(idx == 0 and bucket == "approved")
        ):
            st.write(f"**Description:** {market['description']}")

            c1, c2, c3 = st.columns(3)
            c1.metric("Settleable", market.get("settleable_score"))
            c2.metric("Fun", market.get("fun_score"))
            c3.metric("Exploit Risk", market.get("exploit_risk"))

            if bucket == "approved":
                st.success(
                    f"**AI Reasoning:** "
                    f"{market.get('reasoning')}"
                )
            else:
                st.warning(
                    f"**AI Reasoning:** "
                    f"{market.get('reasoning')}"
                )

            st.write(
                f"**Confidence:** "
                f"{market.get('confidence_explanation')}"
            )

            col_a, col_b = st.columns(2)

            if col_a.button(
                "✅ Approve",
                key=f"app_{bucket}_{idx}_{key}",
                use_container_width=True
            ):
                save_decision(
                    match=match_label,
                    market=market,
                    trader_decision="APPROVED"
                )
                st.session_state.decisions_made[key] = (
                    "APPROVED"
                )
                st.rerun()

            if col_b.button(
                "❌ Reject",
                key=f"rej_{bucket}_{idx}_{key}",
                use_container_width=True
            ):
                save_decision(
                    match=match_label,
                    market=market,
                    trader_decision="REJECTED"
                )
                st.session_state.decisions_made[key] = (
                    "REJECTED"
                )
                st.rerun()

    # Approved markets
    if results["approved"]:
        st.subheader(
            f"✅ Approved ({len(results['approved'])})"
        )
        for i, m in enumerate(results["approved"]):
            show_market(m, "approved", i)

    # Review markets
    if results["review"]:
        st.subheader(
            f"⚠️ Review ({len(results['review'])})"
        )
        for i, m in enumerate(results["review"]):
            show_market(m, "review", i)

    # Rejected markets
    if results["rejected"]:
        st.subheader(
            f"❌ Auto Rejected "
            f"({len(results['rejected'])})"
        )
        for m in results["rejected"]:
            with st.expander(
                f"❌ {m['market_name']} — "
                f"Confidence: "
                f"{m.get('calculated_confidence')}"
            ):
                st.write(
                    f"**Description:** {m['description']}"
                )
                st.error(
                    f"**Rejected:** {m.get('reasoning')}"
                )

    st.divider()
    st.success(
        f"Run logged to MLflow. "
        f"Approval rate: "
        f"{results['approval_rate']*100:.0f}%"
    )
    st.caption(
        "Full audit trail: http://127.0.0.1:5000"
    )