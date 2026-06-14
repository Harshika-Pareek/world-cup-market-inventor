# data/fetcher.py

import os
import requests
import xml.etree.ElementTree as ET

def fetch_match_news(team1, team2):
    """
    Combine local match file + BBC RSS news.
    Local file = match specific signals.
    BBC RSS = general football context.
    Together = richer input for AI pipeline.
    """
    print(f"Fetching news for {team1} vs {team2}...")

    combined = ""

    # Source 1 — Local match specific file
    local = load_local_file(team1, team2)
    if local:
        combined += "=== MATCH SPECIFIC NEWS ===\n"
        combined += local + "\n\n"
        print(f"Local file loaded ")
    else:
        print(f"No local file found for this match")

    # Source 2 — BBC RSS general football news
    bbc = fetch_bbc_rss()
    if bbc:
        combined += "=== LATEST FOOTBALL NEWS ===\n"
        combined += bbc + "\n\n"
        print(f"BBC RSS loaded ")
    else:
        print(f"BBC RSS unavailable")

    # If nothing loaded use fallback
    if not combined:
        print(f"Using fallback text")
        return get_fallback(team1, team2)

    return combined


def load_local_file(team1, team2):
    """Load local txt file if exists and has content."""
    filenames = [
        f"{team1.lower()}_{team2.lower()}.txt",
        f"{team2.lower()}_{team1.lower()}.txt"
    ]
    for filename in filenames:
        filepath = os.path.join("data", filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                return content
    return None


def fetch_bbc_rss():
    """Fetch general football news from BBC RSS."""
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
    Both teams preparing for crucial group stage match.
    Key players expected to feature on both sides.
    High stakes match with significant implications.
    """

