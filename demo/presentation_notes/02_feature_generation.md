# Feature Generation

## Purpose

Convert canonical operational data into normalized, interpretable feature signals that downstream engines can score, rank, explain, and expose through the API.

## Implementation Summary

- Implemented a feature registry with 18 registered features.
- Built feature generators across agronomic, sales, inventory, relationship, competitive, and travel categories.
- Produced multiple feature views for different downstream modules.
- Preserved feature metadata so each signal remains interpretable.

## How It Works

The feature pipeline reads canonical views, computes normalized feature scores, and writes module-specific feature views. These feature views become the shared input layer for prioritization, recommendations, anomaly detection, and explanations.

## Generated Feature Views

Current processed feature artifacts:

- `combined_feature_view.csv`: 10,000 rows, 22 columns
- `priority_feature_view.csv`: 10,000 rows, 22 columns
- `contextual_feature_view.csv`: 10,000 rows, 13 columns
- `anomaly_feature_view.csv`: 10,000 rows, 9 columns
- `feature_registry.csv`: 18 rows, 10 columns

## Signal Categories

Implemented feature categories:

- agronomic signals
- sales opportunity signals
- inventory need signals
- relationship / engagement signals
- competitive pressure signals
- travel cost signals

## Demo Evidence

Feature generation supports the later demo outputs:

- the priority engine reads feature scores to rank entities
- contextual rules use feature values to trigger recommendations
- anomaly detection reads feature values against baselines
- explanations map final outputs back to evidence signals

## Verification

Relevant implementation areas:

- `backend/features/feature_registry.py`
- `backend/features/feature_pipeline.py`
- `backend/features/agronomic_features.py`
- `backend/features/sales_features.py`
- `backend/features/inventory_features.py`
- `backend/features/relationship_features.py`
- `backend/features/competitor_features.py`
- `backend/features/travel_features.py`
- `tests/test_build02_feature_registry.py`
- `tests/test_build02_feature_pipeline.py`

Focused Build 02 tests were verified during development.

## Current Limits

- Public processed signal tables are not yet fully merged into the main final feature generation run.
- Competitive and travel signals depend on matching input availability.
- Feature values are deterministic engineering signals, not trained ML predictions.

## Judge Takeaway

KshetraAI turns raw operational records into a reusable, explainable feature layer that powers the rest of the intelligence workflow.
