## Example Output — Real Run

Screenshots from an actual pipeline run for England vs Croatia,
Group B.

### 1. Match selection and signal extraction

Signal extraction completed in 23.39 seconds — pulling real team
form, tactical setup, and goalkeeper data for both sides.

![Match selection and signal extraction](docs/screenshots/01_match_selection_signal_extraction.png)

### 2. Extracted signals — including injury detection

The extractor pulled specific, current injury information for both
teams (Bukayo Saka doubtful, Perišić injured) and derived six
distinct betting signals from the combined form, tactics, and
injury data.

![Injury detection and key signals](docs/screenshots/02_injury_detection_key_signals.png)

### 3. Generated markets — scored and approved

Eight markets were generated and approved in this run. Each shows
the full scoring breakdown — Settleable, Fun, and Exploit Risk —
plus the AI's plain-language reasoning for the score, before the
trader approve/reject decision.

Example: **"First Half Under 1.5 Goals"** scored 0.9 confidence —
Settleable 0.98, Fun 0.85, Exploit Risk 0.25 — with the reasoning
shown directly to the trader before they click Approve or Reject.

![Approved markets with confidence scores](docs/screenshots/03_approved_markets_confidence_scores.png)

**What this demonstrates:** the pipeline correctly identified a
current injury (Saka) not present in generic team news, tactically
grounded the signal summary in each team's actual setup, and
produced eight distinct, individually-scored markets — all in under
25 seconds, with every market requiring explicit human approval
before it would ever be considered live.
