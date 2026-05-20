# Contextual Decision Engine

## Purpose

Generate a next best action for a selected visit entity so the field representative knows what to discuss or inspect during the visit.

## Implementation Summary

- Implemented deterministic rule matching for contextual recommendations.
- Added controlled YAML rule definitions.
- Generated recommendation outputs and advisory outputs.
- Preserved rule-match and recommendation trace logs.
- Exposed selected recommendations through the `/recommendations/{entity_id}` API.

## How It Works

The contextual engine reads contextual feature rows, evaluates controlled rules, creates recommendation records for matching rules, and writes advisory/recommendation outputs with confidence and evidence fields.

## Rule Areas

Implemented rule categories include:

- agronomic risk
- inventory replenishment
- sales opportunity
- relationship / campaign engagement
- competitive pressure

Current rule set:

- 10 YAML rules
- deterministic rule evaluation
- no black-box recommendation model

## Demo Evidence

Current processed recommendation output:

- `datasets/processed/recommendation_outputs.csv`
- 10,041 rows
- 14 columns

Current rule distribution:

- `NO_CONTEXTUAL_RULE_MATCH`: 9,300 rows
- `SALES_PURCHASE_HISTORY`: 391 rows
- `RELATIONSHIP_CAMPAIGN`: 226 rows
- `INVENTORY_REPLENISHMENT`: 102 rows
- `INVENTORY_FAST_MOVING`: 20 rows
- `SALES_SEASONAL`: 2 rows

Sample recommendation for `RTL_01300`:

```text
risk_or_opportunity: Possible fast-moving stock pressure
recommended_product_category: Relevant Seasonal SKU
confidence_level: Medium
```

Recommended actions:

- `review_fast_moving_sku_availability`
- `check_reorder_timing`
- `plan_inventory_follow_up`

## Verification

Relevant implementation areas:

- `backend/engines/contextual_decision_engine.py`
- `backend/engines/rule_matcher.py`
- `backend/engines/recommendation_engine.py`
- `backend/engines/advisory_engine.py`
- `backend/engines/action_selector.py`
- `backend/config/contextual_rules.yaml`
- `tests/test_build04_recommendation_engine.py`
- `tests/test_build04_advisory_action_selection.py`

Focused Build 04 tests were verified during development.

## Current Limits

- Most current generated rows do not trigger contextual rules.
- The current API returns one recommendation response for a selected entity, not the full advisory bundle.
- Recommendations are rule-based and deterministic, not ML-generated.

## Judge Takeaway

KshetraAI converts feature signals into concrete next best actions while keeping the recommendation logic rule-based and auditable.
