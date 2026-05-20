# Anomaly and Opportunity Detection

## Purpose

Detect operational exceptions such as stock-out risk, sales decline, and demand spikes so the representative can respond before the opportunity or risk is missed.

## Implementation Summary

- Implemented deterministic anomaly and opportunity detectors.
- Added configured baseline comparisons.
- Generated alert outputs and anomaly trace logs.
- Classified alerts by severity and confidence.
- Exposed alerts through the `/alerts` API and frontend alert panel.

## How It Works

The anomaly engine reads feature rows, compares selected signals against configured baselines and thresholds, emits alert records, and preserves supporting evidence in a trace log.

## Detector Areas

Implemented detector categories:

- agronomic
- sales opportunity / sales risk
- inventory
- competitive
- operational

Current visible alert types:

- stock-out risk
- sales decline warning
- demand spike opportunity

## Demo Evidence

Current processed outputs:

- `datasets/processed/anomaly_baseline_view.csv`: 10,000 rows, 32 columns
- `datasets/processed/anomaly_alerts.csv`: 8,827 rows, 13 columns
- `datasets/processed/anomaly_trace_log.csv`: 8,827 rows, 16 columns

Alert type distribution:

- sales decline warning: 7,006 rows
- possible stock-out risk: 1,634 rows
- demand spike opportunity: 187 rows

Fixed demo territory:

```text
territory_id: TER_0164
alert_count: 19
```

Top sample alert:

```text
entity_id: RTL_01300
alert_type: Possible stock-out risk
severity_score: 78.5
severity_level: High
confidence_level: High
```

## Verification

Relevant implementation areas:

- `backend/anomaly/anomaly_engine.py`
- `backend/anomaly/baseline_builder.py`
- `backend/anomaly/detectors.py`
- `backend/anomaly/alert_generator.py`
- `backend/api/services/anomaly_service.py`
- `tests/test_build05_anomaly_engine_integration.py`
- `tests/test_build05_alert_generation.py`

Focused Build 05 tests were verified during development.

## Current Limits

- Alert volume is high because baselines and thresholds are prototype-level.
- Alert calibration should not be presented as production-tuned.
- The API reads generated alert outputs rather than detecting anomalies live per request.

## Judge Takeaway

KshetraAI has a working deterministic alerting layer that surfaces operational risk and opportunity signals with severity, confidence, and evidence.
