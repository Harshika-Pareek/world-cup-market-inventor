# pipeline/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class Injury(BaseModel):
    player: str
    team: str
    status: str
    impact: str

class Signals(BaseModel):
    match: str
    key_injuries: List[Injury]
    team1_form: str
    team2_form: str
    team1_tactics: str
    team2_tactics: str
    match_conditions: str
    motivation: str
    historical_context: str
    key_betting_signals: List[str]

class Market(BaseModel):
    market_name: str
    description: str
    settleable_score: float = 0.0
    fun_score: float = 0.0
    exploit_risk: float = 0.0
    overall_confidence: float = 0.0
    reasoning: str = ""
    status: str = "PENDING"

class PipelineOutput(BaseModel):
    match: str
    total_generated: int
    approved: List[Market]
    review: List[Market]
    rejected: List[Market]
    approval_rate: float
    latency_seconds: float