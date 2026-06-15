# test_critic.py
from pipeline.critic import critique_market, classify_market

markets = [
    {
        "market_name": "Referee nationality",
        "description": "What nationality is the referee?"
    },
    {
        "market_name": "Goalkeeper saves penalty",
        "description": "Will goalkeeper save a penalty in normal time?"
    },
    {
        "market_name": "Total yellow cards over 3.5",
        "description": "Will there be 4 or more yellow cards?"
    },
    {
        "market_name": "Croatia formation switch",
        "description": "Will Croatia change their tactical formation?"
    },
    {
        "market_name": "First goal before 10 minutes",
        "description": "Will either team score in first 10 minutes?"
    },
    {
        "market_name": "Total corners over 9.5",
        "description": "Will there be 10 or more corners?"
    }
]

print("CRITIC TEST RESULTS")
print("="*50)

for m in markets:
    category = classify_market(m)
    result = critique_market(m)
    print(f"\nMarket: {m['market_name']}")
    print(f"  Category:   {category}")
    print(f"  Verdict:    {result['verdict']}")
    print(f"  Confidence: {result['overall_confidence']}")
    print(f"  Settleable: {result['settleable_score']}")
    print(f"  Fun:        {result['fun_score']}")
    print(f"  Exploit:    {result['exploit_risk']}")
    print(f"  Reasoning:  {result['reasoning']}")