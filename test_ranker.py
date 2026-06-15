# test_ranker.py
from pipeline.ranker import (
    calculate_confidence,
    explain_confidence,
    route_market
)

# Test 1 — Great goalkeeper market
market1 = {
    "market_name": "Martinez Saves A Penalty",
    "settleable_score": 0.95,
    "fun_score": 0.90,
    "exploit_risk": 0.20
}
conf1 = calculate_confidence(market1)
market1["calculated_confidence"] = conf1
print(f"Test 1: {market1['market_name']}")
print(f"Confidence: {conf1}")
print(f"Explanation: {explain_confidence(market1, conf1)}")
print(f"Route: {route_market(market1)}")
print()

# Test 2 — Bad formation market
market2 = {
    "market_name": "Croatia Formation Switch",
    "settleable_score": 0.30,
    "fun_score": 0.20,
    "exploit_risk": 0.70
}
conf2 = calculate_confidence(market2)
market2["calculated_confidence"] = conf2
print(f"Test 2: {market2['market_name']}")
print(f"Confidence: {conf2}")
print(f"Explanation: {explain_confidence(market2, conf2)}")
print(f"Route: {route_market(market2)}")
print()

# Test 3 — Borderline corners market
market3 = {
    "market_name": "Total Corners Over 9.5",
    "settleable_score": 0.85,
    "fun_score": 0.60,
    "exploit_risk": 0.50
}
conf3 = calculate_confidence(market3)
market3["calculated_confidence"] = conf3
print(f"Test 3: {market3['market_name']}")
print(f"Confidence: {conf3}")
print(f"Explanation: {explain_confidence(market3, conf3)}")
print(f"Route: {route_market(market3)}")