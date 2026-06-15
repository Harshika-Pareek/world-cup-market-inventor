# pipeline/schemas.py
from pydantic import BaseModel
from typing import List, Optional


class Injury(BaseModel):
    player: str
    team: str
    status: str
    impact: str


class GoalkeeperSignals(BaseModel):
    team1_goalkeeper: Optional[str] = ""
    team1_gk_saves: Optional[str] = ""
    team1_gk_penalties: Optional[str] = ""
    team1_clean_sheets: Optional[str] = ""
    team2_goalkeeper: Optional[str] = ""
    team2_gk_saves: Optional[str] = ""
    team2_gk_penalties: Optional[str] = ""
    team2_clean_sheets: Optional[str] = ""
    shootout_likely: Optional[str] = ""


class DefensiveSignals(BaseModel):
    team1_defensive_actions: Optional[str] = ""
    team1_shots_conceded: Optional[str] = ""
    team2_defensive_actions: Optional[str] = ""
    team2_shots_conceded: Optional[str] = ""
    set_piece_threat: Optional[str] = ""
    defensive_style: Optional[str] = ""


class Signals(BaseModel):
    match: str
    key_injuries: List[dict] = []
    team1_form: str = ""
    team2_form: str = ""
    team1_tactics: str = ""
    team2_tactics: str = ""
    match_conditions: str = ""
    motivation: str = ""
    historical_context: str = ""
    goalkeeper_signals: dict = {}
    defensive_signals: dict = {}
    key_betting_signals: List[str] = []


class Market(BaseModel):
    """
    Single betting market with critic scores.

    Fields from generator:
    market_name, description

    Fields from critic:
    settleable_score, fun_score, exploit_risk,
    overall_confidence, reasoning, category, verdict

    Fields from ranker:
    calculated_confidence, confidence_explanation, status
    """
    market_name: str
    description: str = ""

    # Critic scores
    settleable_score: float = 0.5
    fun_score: float = 0.5
    exploit_risk: float = 0.5
    overall_confidence: float = 0.5
    reasoning: str = ""

    # New fields from revised critic
    category: str = "GENERAL"
    verdict: str = "REVIEW"

    # Ranker fields (added later)
    calculated_confidence: Optional[float] = None
    confidence_explanation: Optional[str] = None
    status: Optional[str] = None


class PipelineOutput(BaseModel):
    match: str
    total_generated: int
    approved: List[Market]
    review: List[Market]
    rejected: List[Market]
    approval_rate: float
    latency_seconds: float