# test_fetch.py
from data.fetcher import fetch_match_news

print("=== England vs Croatia ===")
news1 = fetch_match_news("England", "Croatia")
print(news1[:200])

print("\n=== Argentina vs France ===")
news2 = fetch_match_news("Argentina", "France")
print(news2[:200])

print("\n=== Brazil vs Germany (no local file) ===")
news3 = fetch_match_news("Brazil", "Germany")
print(news3[:200])