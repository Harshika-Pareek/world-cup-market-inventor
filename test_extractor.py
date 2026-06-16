# test_extractor_quick.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.extractor import extract_signals

# Mock news — same shape as what fetcher.py returns
mock_news = """
=== MATCH DATA ===
England vs Croatia World Cup 2026 Group B.
England striker Harry Kane is doubtful with a knee injury.
Croatia rely heavily on Luka Modric in midfield.
England playing 4-3-3, Croatia expected to use 4-2-3-1.
England won last 3 matches, Croatia drew 2 of last 3.
Jordan Pickford starting in goal for England.
Dominik Livakovic is Croatia goalkeeper, saved 2 penalties recently.
"""

# Run it
signals = extract_signals(mock_news, "England", "Croatia")

# Print everything so you can see what came back
print("\n===== SIGNALS OUTPUT =====")
print(f"Match: {signals.get('match')}")
print(f"Team1 form: {signals.get('team1_form')}")
print(f"Team2 form: {signals.get('team2_form')}")
print(f"Team1 tactics: {signals.get('team1_tactics')}")
print(f"Team2 tactics: {signals.get('team2_tactics')}")
print(f"Injuries: {signals.get('key_injuries')}")
print(f"Goalkeeper signals: {signals.get('goalkeeper_signals')}")
print(f"Betting signals: {signals.get('key_betting_signals')}")