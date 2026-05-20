# KshetraAI Final Presentation Outline

## Purpose

This file summarizes the actual Stage 1 presentation deck for judges who want a text reference beside the editable PowerPoint.

Deck file:

```text
demo/presentation_deck/output.pptx
```

Current deck length:

```text
13 slides
```

## Slide 1: KshetraAI

Introduces KshetraAI as an explainable field-force intelligence workflow for agricultural sales operations.

Core message:

- move from static visit planning to signal-driven execution
- preserve explainability and human governance
- support daily planning, action guidance, alerts, and outcome capture

## Slide 2: Problem

Frames the operating problem faced by field representatives.

Problem points:

- fixed routes do not adapt to field reality
- inventory, demand, crop context, and retailer signals change quickly
- reps need help deciding who to visit, what to discuss, and why it matters

Ground truth:

- This is the business problem the implemented workflow is designed to demonstrate.

## Slide 3: Approach

Shows the system workflow:

```text
Data -> Features -> Priority -> Action -> Alerts -> Explanation -> Outcome
```

Core design choices:

- deterministic scoring and rules
- explainable outputs
- modular implementation
- local demo readiness
- human-governed improvement

Ground truth:

- The codebase follows this modular flow across data, features, engines, API, frontend, and demo artifacts.

## Slide 4: Data Foundation

Explains how the system handles source data and public-data preparation.

Implemented truth:

- private raw internal data is read locally from ignored `private-data/`
- processed operational views are generated under `datasets/processed/`
- public-data preparation exists for weather, crop context, NDVI references, and pest references

Important caveat:

- public processed tables exist, but are not fully merged into the main private/public feature generation run yet

Reference:

- [01_data_foundation.md](01_data_foundation.md)

## Slide 5: Intelligence Core

Summarizes the implemented intelligence modules.

Implemented modules:

- feature generation
- dynamic prioritization
- contextual next best action
- anomaly and opportunity detection
- explainability
- outcome learning foundation

Ground truth:

- These modules exist in code and produce the processed/API/demo artifacts referenced in the appendix.

References:

- [02_feature_generation.md](02_feature_generation.md)
- [03_dynamic_prioritization.md](03_dynamic_prioritization.md)
- [04_contextual_decision.md](04_contextual_decision.md)
- [05_anomaly_and_opportunity_detection.md](05_anomaly_and_opportunity_detection.md)
- [06_explainability_and_trust.md](06_explainability_and_trust.md)
- [07_outcome_learning_and_feedback.md](07_outcome_learning_and_feedback.md)

## Slide 6: Component Logic

Shows how each component contributes to the workflow.

Component logic:

- data foundation validates and joins source records
- feature builder converts records into normalized signals
- priority engine ranks visit entities
- next best action rules select operational recommendations
- alert engine surfaces stock, sales, and demand exceptions
- explainability maps outputs back to evidence
- outcome layer captures what happened after the visit
- API and UI expose the workflow without recalculating intelligence in the browser

Ground truth:

- This slide is a concise map of the implemented system, not a claim of production deployment.

## Slide 7: Priority

Presents the dynamic prioritization output for the fixed demo scenario.

Demo scenario:

```text
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
top_entity: RTL_01300
```

Current sample truth:

- priority score: `37.1125`
- priority level: `Low`
- strongest signal: inventory need `92.5`
- daily-plan page size: `3`

Important caveat:

- the current generated demo output classifies all rows as Low by absolute threshold, while relative ranking still works

Reference:

- [03_dynamic_prioritization.md](03_dynamic_prioritization.md)

## Slide 8: Action + Trust

Combines next best action, alerting, and explanation for the selected entity.

Selected entity:

```text
RTL_01300
```

Current sample truth:

- recommendation: possible fast-moving stock pressure
- product category: Relevant Seasonal SKU
- recommendation confidence: Medium
- top alert: Possible stock-out risk
- alert severity score: `78.5`
- alert severity level: High
- alert confidence: High
- explanation output exists for priority, recommendation, and anomaly reasoning

References:

- [04_contextual_decision.md](04_contextual_decision.md)
- [05_anomaly_and_opportunity_detection.md](05_anomaly_and_opportunity_detection.md)
- [06_explainability_and_trust.md](06_explainability_and_trust.md)

## Slide 9: Outcome

Shows how the workflow closes the loop after a visit.

Outcome flow captures:

- visit completion
- recommendation followed
- sale/order information
- alert validation
- rep feedback

Current sample truth:

```text
status: success
outcome_id: OUTCOME_RTL_01300_POSSIBLE_FAST_MOVING_STOCK_PRESSURE
```

Important caveat:

- the repository does not currently contain a persistent historical outcome dataset
- recalibration is human-review only

Reference:

- [07_outcome_learning_and_feedback.md](07_outcome_learning_and_feedback.md)

## Slide 10: Product

Shows that the intelligence workflow is exposed through a working backend and frontend.

Implemented backend endpoints:

- `GET /health`
- `GET /daily-plan`
- `GET /recommendations/{entity_id}`
- `GET /alerts`
- `GET /explanations/{entity_id}`
- `POST /outcomes`

Implemented frontend screens:

- overview
- daily plan
- recommendation and explanation
- alerts
- outcome submission

Ground truth:

- the frontend consumes backend API responses and does not compute intelligence logic itself

References:

- [08_fastapi_backend_integration.md](08_fastapi_backend_integration.md)
- [09_frontend_dashboard_and_workflow.md](09_frontend_dashboard_and_workflow.md)

## Slide 11: Demo Readiness

Summarizes the repeatable demo package.

Demo identity:

```text
scenario_id: AMRITSAR_CROP_PROTECTION_001
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
selected_entity: RTL_01300
```

Demo checks:

- workflow verification script
- acceptance-check script
- sample API output files
- Build 10 regression tests

Reference:

- [10_demo_integration_testing_final_polish.md](10_demo_integration_testing_final_polish.md)

## Slide 12: Truth + Roadmap

States what works today and what remains future scope.

Works today:

- data pipeline
- feature generation
- priority ranking
- next best action
- alert outputs
- explanations
- outcome submission
- FastAPI backend
- React frontend workflow
- deterministic demo artifacts

Current limits:

- no production database persistence
- no authentication
- no cloud deployment
- public NDVI and pest signals are reference/foundation level
- public processed tables are not fully merged into the main feature run
- anomaly thresholds are prototype-level
- no map or route optimization view

## Slide 13: Final Impact

Closes the deck with the product outcome.

KshetraAI helps answer:

- who to visit
- why that visit matters
- what action to take
- what risk or opportunity exists
- what happened after the visit

Final claim:

- KshetraAI demonstrates an explainable, deterministic, human-governed field-force intelligence workflow for agricultural sales operations.

## Appendix Reading Path

For deeper review, use:

- [00_judge_reference_index.md](00_judge_reference_index.md)
- [01_data_foundation.md](01_data_foundation.md)
- [02_feature_generation.md](02_feature_generation.md)
- [03_dynamic_prioritization.md](03_dynamic_prioritization.md)
- [04_contextual_decision.md](04_contextual_decision.md)
- [05_anomaly_and_opportunity_detection.md](05_anomaly_and_opportunity_detection.md)
- [06_explainability_and_trust.md](06_explainability_and_trust.md)
- [07_outcome_learning_and_feedback.md](07_outcome_learning_and_feedback.md)
- [08_fastapi_backend_integration.md](08_fastapi_backend_integration.md)
- [09_frontend_dashboard_and_workflow.md](09_frontend_dashboard_and_workflow.md)
- [10_demo_integration_testing_final_polish.md](10_demo_integration_testing_final_polish.md)
