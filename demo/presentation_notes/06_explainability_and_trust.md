# Module 06: Explainability and Trust

## Purpose

Make priority, recommendation, and anomaly outputs understandable by mapping them back to evidence, confidence, and human-readable reasoning.

## Implementation Summary

- Implemented evidence mapping for priority, recommendation, and anomaly outputs.
- Generated explanation outputs and trace logs.
- Added confidence reasoning and safety validation.
- Built frontend explanation presentation that groups evidence for readability.
- Exposed explanations through `/explanations/{entity_id}`.

## How It Works

The explainability layer takes generated intelligence outputs, extracts supporting evidence fields, applies deterministic explanation templates, assigns confidence information, and writes explanation records and traces.

## Demo Evidence

Current explanation outputs are generated for the selected demo entity:

```text
entity_id: RTL_01300
```

Current processed outputs:

- `datasets/processed/evidence_view.csv`: 6 rows, 9 columns
- `datasets/processed/explanation_outputs.csv`: 6 rows, 11 columns
- `datasets/processed/explanation_trace_log.csv`: 6 rows, 8 columns

Explanation type distribution:

- recommendation: 3
- anomaly: 2
- priority: 1

Confidence distribution:

- High: 3
- Medium: 3

Sample explanation types available:

- why the entity was ranked
- why recommendations were suggested
- why alerts were raised

## Verification

Relevant implementation areas:

- `backend/explainability/evidence_mapper.py`
- `backend/explainability/explanation_engine.py`
- `backend/explainability/confidence_explainer.py`
- `backend/api/services/explainability_service.py`
- `frontend/components/ExplanationPanel.tsx`
- `tests/test_build06_evidence_mapper.py`
- `tests/test_build06_explainability_integration.py`
- `tests/test_build06_explanation_generation.py`

Focused Build 06 tests were verified during development.

## Current Limits

- The current generated explanation set is focused on the selected demo entity, not every entity in the full dataset.
- Some explanation text is prototype wording, such as "current severity".
- Explanations are deterministic template-based outputs, not natural-language generation from an LLM.

## Judge Takeaway

KshetraAI does not hide recommendations behind opaque scoring; the demo entity has visible evidence for priority, recommendation, and alert decisions.
