# data/fetcher.py
import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()


def fetch_match_news(team1, team2):
    """
    Three layer fetcher:
    1. Local txt file (match specific rich data)
    2. NewsAPI (real time team specific search)
    3. BBC RSS (general football fallback)
    """
    print(f"Fetching news for {team1} vs {team2}...")
    combined = ""

    # Layer 1 — Local file
    local = load_local_file(team1, team2)
    if local:
        combined += "=== MATCH DATA ===\n"
        combined += local + "\n\n"
        print(f"Local file loaded")

    # Layer 2 — NewsAPI
    news = fetch_newsapi(team1, team2)
    if news:
        combined += "=== LIVE NEWS ===\n"
        combined += news + "\n\n"
        print(f"NewsAPI loaded")
    else:
        # Layer 3 — BBC RSS fallback
        bbc = fetch_bbc_rss()
        if bbc:
            combined += "=== FOOTBALL NEWS ===\n"
            combined += bbc + "\n\n"
            print(f"BBC RSS loaded")

    if not combined:
        return get_fallback(team1, team2)

    return combined


def load_local_file(team1, team2):
    filenames = [
        f"{team1.lower()}_{team2.lower()}.txt",
        f"{team2.lower()}_{team1.lower()}.txt"
    ]
    for filename in filenames:
        filepath = os.path.join("data", filename)
        if os.path.exists(filepath):
            with open(filepath, "r",
                      encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                return content
    return None


def fetch_newsapi(team1, team2):
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("No NEWS_API_KEY found")
        return None

    try:
        url = "https://newsapi.org/v2/everything"

        # Try specific search first
        params = {
            "q": f"{team1} {team2} World Cup",
            "apiKey": api_key,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5
        }

        response = requests.get(
            url, params=params, timeout=10
        )
        data = response.json()
        articles = data.get("articles", [])

        # Try broader search if nothing found
        if not articles:
            params["q"] = f"{team1} {team2} football"
            response = requests.get(
                url, params=params, timeout=10
            )
            data = response.json()
            articles = data.get("articles", [])

        if not articles:
            print("No articles found in NewsAPI")
            return None

        combined = ""
        for article in articles:
            title = article.get("title", "")
            description = article.get(
                "description", ""
            )
            if title:
                combined += f"{title}\n"
            if description:
                combined += f"{description}\n\n"

        print(f"Found {len(articles)} articles ✅")
        return combined if combined else None

    except Exception as e:
        print(f"NewsAPI failed: {e}")
        return None


def fetch_bbc_rss():
    try:
        url = "http://feeds.bbci.co.uk/sport/football/rss.xml"
        response = requests.get(url, timeout=10)
        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        news = ""
        for item in items[:5]:
            title = item.find("title")
            description = item.find("description")
            if title is not None:
                news += f"{title.text}\n"
            if description is not None:
                news += f"{description.text}\n\n"

        return news if news else None

    except Exception as e:
        print(f"BBC RSS failed: {e}")
        return None


def get_fallback(team1, team2):
    return f"""
{team1} face {team2} in the 2026 FIFA World Cup.
Both teams preparing for a crucial match.
Key players expected to feature on both sides.
High stakes match with significant implications.
"""