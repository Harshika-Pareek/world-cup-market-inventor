from fastapi import FastAPI
from pipeline.generator import generate_markets
from pipeline.critic import critique_all_markets

app = FastAPI()

@app.get("/")
def home():
    return {"status": "World Cup Market API running"}

@app.post("/generate-markets")
def generate_markets_api(payload: dict):
    team1 = payload.get("team1")
    team2 = payload.get("team2")
    context = payload.get("context", "")

    markets = generate_markets(team1, team2, context)
    scored_markets = critique_all_markets(markets)

    return {"markets": scored_markets}