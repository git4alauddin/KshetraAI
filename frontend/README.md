# KshetraAI Console (Frontend)

Brutalist minimal interactive demo dashboard. Single HTML file, opens in any browser, no build step required.

Matches the design language of the team's prior project (ClaimDrift): black borders, white surfaces, sharp corners, monospace for data, sparing color only for status.

## How to open it

Just double-click `index.html`. Or:

```bash
# From the project root
open frontend/index.html              # macOS
xdg-open frontend/index.html          # Linux
start frontend/index.html             # Windows
```

It works offline. The page pulls Tailwind, React, and Babel from CDN on first load, then everything runs locally. Once loaded, no further network calls are made.

## What is inside

Four views, accessible from the left sidebar.

**Dashboard** -- 4 stat cards across the top (territories active, average priority score, anomaly alerts, NDCG at 5) and a table of the top territories ranked by priority. Click any row to open the beat plan for that territory.

**Beat Plan** -- The ordered visit sequence for one territory, with each retailer's score, tier, recommended pitch, and SHAP reasoning (top three signals plus one watch signal). Right rail shows the CHETAVANI alerts for that territory and a route summary. Switcher at the top lets you flip between sample territories.

**CHETAVANI** -- Full priority-ranked alert feed across all territories, with severity scores. Demand spikes and price anomalies in one place.

**SEEKHO** -- The outcome log. Acceptance rate, sale success rate, and recent visit outcomes. There is a demo button to append a new outcome so the table updates live.

## How it ties to the pipeline

The frontend has two data modes:

**Demo mode (default).** Opens with built-in mock data that matches the exact schema of pipeline outputs. Use this for design review, presentations without internet, or when the pipeline has not been run yet.

**Live mode.** After running `python run_pipeline.py` (which calls `build_frontend.py` automatically), a file `frontend/data.js` is generated with the real numbers from your run. Reload `index.html` and the dashboard switches to live data. A green indicator in the header says "Live pipeline data" instead of "Demo data".

The mock-versus-live switch is automatic. The frontend looks for `window.KSHETRA_DATA` (set by `data.js`) on load. If absent, it falls back to mock. Same UI either way.

| View          | Real source                          |
|---------------|--------------------------------------|
| Dashboard     | `outputs/final_scores.csv` aggregated by territory_id |
| Beat Plan     | `outputs/optimized_routes.csv` + `outputs/shap_values.csv` |
| CHETAVANI     | `outputs/anomaly_alerts.csv` |
| SEEKHO        | `outputs/visit_outcomes.csv` |
| NDCG numbers  | `models/model_meta.json` |

To regenerate after a new training run:

```bash
python run_pipeline.py        # auto-runs build_frontend at the end
# or, to refresh just the frontend without re-training:
python build_frontend.py
```

## Design tokens

| Token | Value |
|---|---|
| Borders | `1px solid #000000` |
| Background | `#FFFFFF` |
| Text muted | `#666666` |
| Background tint | `#F5F5F5` |
| Success | `#0D7A5F` (dark teal-green) |
| Warning | `#E67700` (dark orange) |
| Danger | `#C92A2A` (dark red) |
| Link | `#0066CC` (deep blue) |
| Font sans | system-ui (matches host OS) |
| Font mono | ui-monospace / SF Mono / Menlo |
| Corner radius | none (sharp brutalist) |
| Selection | inverted black on white |

No gradients, no shadows, no glow effects, no decorative motion. Every element is functional.

## For the hackathon demo

The flow for the panel walkthrough:

1. **Open with Dashboard.** Point at the stat cards: 500 reps deployed, NDCG@5 of 0.78 vs a 0.51 baseline. That's a real number, computed by `src/ranker.py`.
2. **Click the top territory (TER_0048, Akola).** Beat plan appears. Walk through stop 1: RTL_00045, score 92, urgent. Read the SHAP reasoning aloud: long gap, low stock, humidity. Mention the suggested pitch (Score 250 EC) is grounded in mustard flowering + humidity.
3. **Point at the right rail.** Two CHETAVANI alerts. The Vertimec price anomaly is a real example from the data (RTL_03909, CV 0.70). Anchor the demo in actual data, not slideware.
4. **Switch to CHETAVANI tab.** Show all alerts ranked by severity. Mention the demand spike fix: the original compared monthly totals against daily means and flagged 90 percent of retailers; the corrected version uses matched weekly rates.
5. **Switch to SEEKHO.** Show the outcome log. Click the demo button to append a row. Explain this is the feedback loop that lets the model retrain every 500 outcomes.

The whole walkthrough takes about 4 minutes.
