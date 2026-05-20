# Dynamic Prioritization

## Purpose

Generate a ranked daily visit plan so a field representative can focus on the most relevant visit first.

## Implementation Summary

- Implemented component scorers for major operational signal groups.
- Implemented weighted priority scoring.
- Implemented priority classification thresholds.
- Implemented stable ranking logic.
- Generated a processed `ranked_visit_list.csv`.
- Exposed ranked visits through the `/daily-plan` API and frontend daily-plan view.

## How It Works

The priority engine reads feature views, calculates component scores, applies configured weights, classifies the final score into a priority level, and ranks entities deterministically.

## Scoring Logic

Current component weights:

- agronomic: `0.30`
- sales: `0.25`
- inventory: `0.20`
- relationship: `0.10`
- competitive: `0.10`
- travel cost: `-0.05`

Priority thresholds:

- Critical: `80+`
- High: `65+`
- Medium: `50+`
- Low: `0+`

## Demo Evidence

Current ranked output:

- `datasets/processed/ranked_visit_list.csv`
- 10,000 rows
- 25 columns

Fixed demo scenario:

```text
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
```

Current daily-plan sample:

- total rows for scenario: `23`
- page size: `3`
- top entity: `RTL_01300`
- priority score: `37.1125`
- priority level: `Low`
- main reason: `Highest signal: inventory need (92.5)`

## Verification

Relevant implementation areas:

- `backend/engines/component_scorers.py`
- `backend/engines/scoring_engine.py`
- `backend/engines/priority_classifier.py`
- `backend/engines/ranking_engine.py`
- `backend/engines/priority_engine.py`
- `tests/test_build03_priority_config.py`
- `tests/test_build03_priority_scoring.py`
- `tests/test_build03_priority_classifier.py`
- `tests/test_build03_priority_engine_integration.py`

Focused Build 03 tests were verified during development.

## Current Limits

- The current generated demo data produces Low absolute priority levels for all rows.
- The engine supports Critical, High, Medium, and Low levels, but the current demo feature values do not reach the higher thresholds.
- The daily-plan API reads generated ranked outputs rather than recomputing all priority logic live per request.

## Judge Takeaway

KshetraAI has a deterministic priority engine that ranks visits by traceable component scores, even when the current demo dataset produces low absolute scores.
