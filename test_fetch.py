# test_fetch.py
from data.fetcher import fetch_match_news

# Test known match
print("=== England vs Croatia ===")
news1 = fetch_match_news("England", "Croatia")
print(news1[:300])

print("\n=== Brazil vs Germany ===")
news2 = fetch_match_news("Brazil", "Germany")
print(news2[:300])

print("\n=== Spain vs Portugal ===")
news3 = fetch_match_news("Spain", "Portugal")
print(news3[:300])