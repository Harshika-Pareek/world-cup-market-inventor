# World Cup 2026 — AI Market Inventor

> **Novel betting market generation with signal extraction, LLM self-critique, confidence scoring and human governance**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)](https://streamlit.io)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue.svg)](https://mlflow.org)
[![Groq](https://img.shields.io/badge/LLM-Groq%20%7C%20Gemini%20%7C%20Ollama-orange.svg)](https://groq.com)

---

##  What This Does

Turns unstructured World Cup news into novel, scored, and ranked betting markets in under 60 seconds.

```
NewsAPI / BBC RSS / Local Data
            ↓
    Signal Extraction (LLM)
            ↓
    Market Generation (LLM)
            ↓
    Critic + Scoring (LLM as Judge)
            ↓
    Rank + Route (Deterministic Formula)
            ↓
    Trader Review (Human in the Loop)
```

**Without this:** Trader reads match previews manually — 40 minutes per match, 64 World Cup matches = weeks of work.

**With this:** AI surfaces ranked markets in 60 seconds. Trader approves or rejects with one click. 38 hours saved.

---

## 🏗️ Project Structure

```
world-cup-market-inventor/
│
├── app.py                          # Streamlit UI — main entry point
├── main.py                         # CLI pipeline runner
├── run_pipeline.py                 # Script to run pipeline directly
├── llm_client.py                   # LLM router — Groq → Gemini → Ollama fallback
├── requirement.txt                 # Python dependencies
├── .gitignore                      # API keys excluded
│
├── pipeline/                       # Core AI pipeline
│   ├── extractor.py                # Stage 2: Extract signals from raw news
│   ├── generator.py                # Stage 3: Generate novel markets from signals
│   ├── critic.py                   # Stage 4: Classify + score each market (LLM as Judge)
│   ├── ranker.py                   # Stage 5: Formula confidence + route to buckets
│   └── schemas.py                  # Pydantic models — Signals, Market, PipelineOutput
│
├── data/                           # Data layer
│   ├── fetcher.py                  # Stage 1: NewsAPI → BBC RSS → local file fallback
│   ├── decision_store.py           # Save/load trader decisions to JSON
│   ├── decisions.json              # Trader approve/reject history
│   ├── golden_dataset.json         # 15 expert-scored markets for evaluation
│   ├── england_croatia.txt         # Local match data file
│   └── argentina_france.txt        # Local match data file
│
├── evaluation/                     # Evaluation framework
│   └── evaluator.py                # LLM vs expert verdict comparison — 80% accuracy
│
├── tracking/                       # MLflow tracking
│   └── tracker.py                  # Log pipeline runs to MLflow
│
├── cache/                          # LLM response cache
│   └── cache_store.py              # Temperature 0.0 calls cached — 80% token saving
│
├── utils/                          # Utilities
│   └── helpers.py                  # Shared helper functions
│
└── test files                      # Test scripts
    ├── test_fetch.py               # Test fetcher with mock data
    ├── test_critic.py              # Test critic scoring
    ├── test_ranker.py              # Test routing logic
    ├── test_cache.py               # Test cache hit/miss
    ├── test_client.py              # Test LLM client connection
    ├── test_groq.py                # Test Groq API directly
    └── critic_test1.py             # Critic integration test
```

---

## 🧠 AI Design Decisions

| Decision | Problem | Solution |
|----------|---------|----------|
| **Temperature strategy** | Same temp everywhere = extraction varies run to run | temp 0.0 for extract + critic, temp 0.8 for generator |
| **LLM as a Judge** | How to score markets without hardcoding rules? | Second LLM call scores each market on 3 dimensions |
| **Formula over LLM verdict** | LLM verdict varies even at temp 0.0 | Weighted formula always decides: settleable×0.5 + fun×0.3 + exploit×0.2 |
| **Human governance** | Nothing should publish automatically | Every market needs trader click — AI recommends, human decides |
| **Separation of concerns** | One big prompt = poor quality on all | Each stage has one job, tuned independently |

---

## Confidence Formula

```
confidence = (settleable_score × 0.5) + (fun_score × 0.3) + ((1 - exploit_risk) × 0.2)
```

**Routing thresholds:**
- `≥ 0.75` → **APPROVED** — trader glances and clicks (10 seconds)
- `≥ 0.50` → **REVIEW** — trader reads carefully (2-3 minutes)
- `< 0.50` → **REJECTED** — auto-dropped, trader never sees it

**Hard gates (override everything):**
- `settleable < 0.4` → REJECTED immediately
- `exploit > 0.85` → REJECTED immediately
- `TRIVIAL / TACTICAL` category → REJECTED immediately
- `STATS` category → REVIEW always

---

## 🔄 Pipeline Stages

### Stage 1 — Fetcher (`data/fetcher.py`)
Three-layer data ingestion with automatic fallback:
1. Local `.txt` file (match-specific rich data)
2. NewsAPI (live search for team names)
3. BBC RSS (general football fallback)

### Stage 2 — Extractor (`pipeline/extractor.py`)
LLM at `temp=0.0` reads raw news and extracts structured signals:
- Team form, tactics, injuries, goalkeeper stats, motivation, conditions
- Validated by Pydantic `Signals` schema

### Stage 3 — Generator (`pipeline/generator.py`)
LLM at `temp=0.8` reads signal dict and invents novel markets:
- Signal-driven: markets reference specific match context
- Generates 8 markets per run
- Fallback markets if LLM fails (pipeline never breaks)

### Stage 4 — Critic (`pipeline/critic.py`)
Four-layer design — **LLM scores. Python decides.**
1. `classify_market()` — keyword scan (zero LLM cost)
2. `build_prompt()` — category-aware tailored prompt
3. LLM scores — `settleable_score`, `fun_score`, `exploit_risk`
4. `decide()` — deterministic routing using hard gates + confidence

### Stage 5 — Ranker (`pipeline/ranker.py`)
- Calculates `calculated_confidence` using weighted formula
- Generates plain English explanation for trader
- Routes to approved / review / rejected buckets
- Sorts approved by confidence — best market shown first

---

## 📈 Evaluation

Golden dataset of 15 expert-scored markets tests whether the critic is trustworthy.

```
Expert verdict vs LLM formula verdict
Current accuracy: 80%
Avg score difference: 0.09
Improved from: 73% → 80% after fixing 7 prompt rules
```

Every evaluation run logged to MLflow. Prompt changes must maintain 75%+ accuracy.

---

## 🛡️ Failure Mode Handling

| Failure | How it's caught |
|---------|----------------|
| **Hallucination** | Grounded prompts — LLM only uses provided data |
| **Nonsense JSON** | JSON parsing with fallback at every stage |
| **LLM rate limits** | Three-tier fallback: Groq → Gemini → Ollama |
| **Score variance** | temp=0.0 + deterministic formula replaces raw LLM verdict |
| **Silent drift** | MLflow tracks approval rate + trader agreement every run |
| **Bad markets** | Fallback critique returns 0.5 scores → REVIEW (never auto-rejects) |

---

## 🚀 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Harshika-Pareek/world-cup-market-inventor.git
cd world-cup-market-inventor
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirement.txt
```

### 2. Add API keys

Create a `.env` file:

```bash
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
NEWS_API_KEY=your_newsapi_key
```

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

Open `http://localhost:8501`

### 4. Run MLflow tracking

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Open `http://localhost:5000`

### 5. Run evaluation

```bash
python evaluation/evaluator.py
```

---

## 🧪 Testing

```bash
# Test fetcher
python test_fetch.py

# Test critic scoring
python test_critic.py

# Test ranker routing
python test_ranker.py

# Test LLM connection
python test_groq.py

# Test cache
python test_cache.py
```

---

## 🏭 Production Roadmap

| Area | Current | Production |
|------|---------|------------|
| **API** | Streamlit button | FastAPI + NewsAPI webhook |
| **Cache** | In-memory dict | Redis with TTL |
| **Database** | decisions.json | PostgreSQL |
| **LLM monitoring** | Print statements | Langfuse observability |
| **Prompt versioning** | Hardcoded strings | Git-versioned prompt files |
| **Evaluation** | Manual run | CI gate on every commit |
| **Deployment** | Local | Docker + env vars |

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI — trader review interface |
| `llm_client.py` | LLM router with Groq→Gemini→Ollama fallback + caching |
| `pipeline/schemas.py` | Pydantic models — data contracts between stages |
| `pipeline/critic.py` | LLM as Judge — 4-layer critic design |
| `pipeline/ranker.py` | Weighted formula + routing logic |
| `evaluation/evaluator.py` | Golden dataset evaluation — proves critic is trustworthy |
| `tracking/tracker.py` | MLflow logging — every run tracked |
| `data/decision_store.py` | Trader decision history — agreement rate tracking |

---

## 🤝 Governance

Nothing publishes automatically. Even 0.99 confidence needs trader sign-off.

```
AI recommends → Trader approves or rejects → Decision logged → Agreement rate tracked
```

Same pattern as RACM system at Flutter — AI recommends, human decides, full audit trail.

---

## 👩‍💻 Author

**Harshika Pareek** — Senior AI/Data Engineer

- LinkedIn: [harshika-pareek](https://www.linkedin.com/in/harshika-pareek-6b15697b/)
- GitHub: [Harshika471](https://github.com/Harshika471)
