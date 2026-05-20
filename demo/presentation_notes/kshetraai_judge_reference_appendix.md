---
title: "KshetraAI"
author: ""
date: "May 2026"
documentclass: book
classoption:
  - 11pt
  - oneside
  - openany
toc: true
toc-depth: 2
numbersections: true
top-level-division: chapter
geometry: "a4paper,margin=1in"
fontsize: 11pt
hidelinks: true
header-includes: |
  \usepackage{xcolor}
  \definecolor{KshetraGreen}{HTML}{0B6B45}
  \definecolor{KshetraLeaf}{HTML}{5FA777}
  \definecolor{KshetraSlate}{HTML}{334155}
  \pagestyle{plain}
  \renewcommand{\maketitle}{%
    \begin{titlepage}
    \centering
    \vspace*{1.2cm}
    {\color{KshetraGreen}\rule{0.82\textwidth}{1.2pt}\par}
    \vspace{1.8cm}
    {\Huge\bfseries\color{KshetraGreen} KshetraAI\par}
    \vspace{0.85cm}
    {\LARGE\bfseries\color{KshetraSlate} Judge Reference Appendix\par}
    \vspace{1.35cm}
    {\Large\color{KshetraSlate} Explainable Field-Force Intelligence\par}
    \vspace{0.18cm}
    {\Large\color{KshetraSlate} for Agricultural Sales Operations\par}
    \vfill
    {\large\bfseries\color{KshetraGreen} Stage 1 Submission\par}
    \vspace{0.28cm}
    {\large\color{KshetraSlate} Syngenta Hackathon\par}
    \vspace{0.28cm}
    {\large\color{KshetraSlate} May 2026\par}
    \vspace{1.4cm}
    {\color{KshetraLeaf}\rule{0.42\textwidth}{0.8pt}\par}
    \end{titlepage}
  }
  \makeatletter
  \def\@makechapterhead#1{\vspace*{18pt}{\parindent \z@ \raggedright \normalfont \Huge\bfseries \thechapter\quad #1\par\nobreak\vskip 28pt}}
  \def\@makeschapterhead#1{\vspace*{18pt}{\parindent \z@ \raggedright \normalfont \Huge\bfseries #1\par\nobreak\vskip 28pt}}
  \makeatother
---

\mainmatter

# Document Scope

This appendix consolidates the judge-reference notes for KshetraAI into one
reviewable document. It is intended to support the presentation deck with
implementation-grounded detail.

The claims in this appendix are limited to the current codebase, generated
artifacts, sample outputs, and verified demo workflow. Where a capability is a
foundation or future scope, it is labeled that way.

## Reference Roadmap

| Section | What It Covers |
|---|---|
| Data Foundation | source boundaries, schemas, public-data readiness |
| Feature Generation | normalized decision signals and generated feature views |
| Dynamic Prioritization | visit ranking, component weights, and demo scenario output |
| Contextual Decision | next best action rules and recommendation evidence |
| Anomaly Detection | alerts, severity, confidence, and current calibration limits |
| Explainability | evidence-backed reasoning for priority, recommendations, and alerts |
| Outcome Learning | outcome capture and human-governed feedback foundation |
| API Integration | FastAPI contracts and processed-output serving boundary |
| Frontend Workflow | React dashboard path and UI behavior |
| Demo Integration | deterministic scenario, sample outputs, and acceptance checks |

\newpage

# Data Foundation

## Purpose

Build a reliable data foundation for KshetraAI by separating raw source data from processed, demo-safe operational views.

## Implementation Summary

- Implemented schema definitions for the company-provided internal dataset.
- Created a deterministic Build 01 pipeline for loading, validating, normalizing, and joining source files.
- Established a private raw data boundary through ignored `private-data/`.
- Established a public raw data boundary through ignored `public-data/`.
- Added a public-data processing workflow for weather, crop context, NDVI metadata, and pest references.

## How It Works

Internal CSV files are validated against schema definitions, normalized into canonical forms, joined into feature-ready views, and written as processed outputs. Public data is processed separately into public signal tables so it can be integrated later without mixing raw private and public sources.

## Data Sources

Internal schemas implemented in code:

- `reps_territory.csv`
- `retailers.csv`
- `retailer_visit_log.csv`
- `retailer_inventory_weekly.csv`
- `retailer_pos.csv`
- `growers.csv`
- `digital_funnel_weekly.csv`
- `whatsapp_campaign.csv`

Public-data foundation:

- weather signals from fetched Open-Meteo data
- controlled crop-stage context
- Sentinel-2 scene metadata / NDVI reference tables
- pest surveillance source references

## Demo Evidence

Canonical processed views include:

- `representatives`
- `territories`
- `retailers`
- `growers`
- `visit_entities`
- `crop_context`
- `retailer_pos_clean`
- `retailer_inventory_weekly_clean`
- `retailer_visit_log_clean`
- `campaign_engagement_clean`

Public processed outputs include:

- `datasets/processed/public/weather_signals.csv`
- `datasets/processed/public/crop_context.csv`
- `datasets/processed/public/ndvi_scene_inventory.csv`
- `datasets/processed/public/ndvi_signals.csv`
- `datasets/processed/public/pest_source_references.csv`
- `datasets/processed/public/pest_signals.csv`

## Current Public Signal Truth

- Weather data is usable as public signal data.
- Crop-stage context is curated/controlled for the demo.
- NDVI is currently metadata/reference level, not raster-derived crop health scoring.
- Pest data is currently reference-level, not active live pest outbreak detection.
- Public processed tables exist, but are not fully merged into the main private/public feature generation run yet.

## Verification

Relevant implementation areas:

- `backend/data/schemas/dataset_schemas.py`
- `backend/pipelines/pipeline_runner.py`
- `scripts/process_public_data.py`
- `tests/test_public_data_processing.py`

## Current Limits

- Raw private data is local only and should not be shared.
- Live public API calls are not used during the judge demo.
- Public NDVI and pest signals are foundations, not full production-grade integrations.

## Judge Takeaway

KshetraAI starts from a controlled, schema-driven data foundation with clear privacy boundaries and a dedicated path for public-domain signal integration.


\newpage

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


\newpage

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


\newpage

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


\newpage

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


\newpage

# Explainability and Trust

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


\newpage

# Outcome Learning and Feedback

## Purpose

Capture field outcomes so recommendations and alerts can later be measured, reviewed, and improved under human governance.

## Implementation Summary

- Implemented outcome submission normalization.
- Implemented outcome logging logic.
- Implemented feedback signal processing.
- Implemented performance metric and analytics modules.
- Implemented recalibration signal generation with human-review constraints.
- Exposed outcome submission through `POST /outcomes`.

## How It Works

The outcome layer accepts a structured visit result, validates required fields, normalizes the outcome, and produces feedback signals that can support future analytics or human-reviewed recalibration.

## Outcome Fields

The current outcome flow captures:

- recommendation ID
- entity ID
- rep ID
- visit completed
- recommendation followed
- sale made
- order placed
- order value
- alert validated
- feedback category
- rep feedback
- optional alert ID

## Demo Evidence

Sample outcome response:

```text
status: success
message: Outcome recorded successfully.
outcome_id: OUTCOME_RTL_01300_POSSIBLE_FAST_MOVING_STOCK_PRESSURE
```

Frontend outcome capture is available in:

```text
frontend/pages/OutcomeSubmission.tsx
frontend/components/OutcomeForm.tsx
```

Backend outcome service is available in:

```text
backend/api/services/outcome_service.py
```

## Verification

Relevant implementation areas:

- `backend/learning/outcome_logger.py`
- `backend/learning/feedback_processor.py`
- `backend/learning/metrics_tracker.py`
- `backend/learning/performance_analytics.py`
- `backend/learning/recalibration_engine.py`
- `backend/api/routes/outcome_routes.py`
- `backend/api/schemas/outcome_schema.py`
- `tests/test_build07_outcome_logger.py`
- `tests/test_build07_feedback_processor.py`
- `tests/test_build07_metrics_analytics.py`
- `tests/test_build07_recalibration_engine.py`
- `tests/test_build08_outcome_routes.py`

Focused Build 07 and outcome API tests were verified during development.

## Current Limits

- The current repository does not contain a persistent historical outcome dataset.
- Generated performance metric artifacts are not part of the current demo outputs.
- Recalibration signals are human-review only and do not automatically mutate weights, rules, thresholds, or models.

## Judge Takeaway

KshetraAI closes the workflow loop by capturing field outcomes, while keeping future learning and recalibration controlled by humans.


\newpage

# FastAPI Backend Integration

## Purpose

Expose the generated intelligence outputs through stable, schema-backed API endpoints for the frontend and demo workflow.

## Implementation Summary

- Implemented a FastAPI backend entrypoint.
- Added six stable API routes.
- Added Pydantic request and response schemas.
- Added service modules that format processed outputs into API responses.
- Added local frontend CORS support.
- Preserved a thin API boundary so route handlers do not duplicate intelligence logic.

## How It Works

The API layer reads existing processed outputs and delegates response formatting to service modules. It does not recompute the full data pipeline, feature generation, prioritization, recommendation, anomaly, or explanation logic per request.

## API Contract

Implemented endpoints:

```text
GET  /health
GET  /daily-plan
GET  /recommendations/{entity_id}
GET  /alerts
GET  /explanations/{entity_id}
POST /outcomes
```

Backend app metadata:

```text
title: KshetraAI Backend
version: 0.1.0
```

Local frontend CORS origins:

```text
http://127.0.0.1:5173
http://localhost:5173
```

## Demo Evidence

Current fixed scenario API sample outputs are stored under:

```text
demo/sample_outputs/
```

Files:

- `daily_plan_response.json`
- `recommendation_response.json`
- `alerts_response.json`
- `explanation_response.json`
- `outcome_submission_response.json`

Current daily-plan sample:

```text
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
page_size: 3
total_count: 23
total_pages: 8
```

## Swagger / OpenAPI

FastAPI provides interactive documentation by default when the backend server is running:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
```

This is framework-provided documentation, not a custom API documentation tool.

## Verification

Relevant implementation areas:

- `backend/main.py`
- `backend/api/routes/`
- `backend/api/services/`
- `backend/api/schemas/`
- `tests/test_build08_api_contract.py`
- `tests/test_build08_api_schemas.py`
- `tests/test_build08_fastapi_entrypoint.py`
- `tests/test_build08_planning_recommendation_routes.py`
- `tests/test_build08_alert_explainability_routes.py`
- `tests/test_build08_outcome_routes.py`

Focused Build 08 API tests were verified during development.

## Current Limits

- No authentication or role-based access control is implemented.
- No production database persistence is implemented.
- The API reads processed CSV outputs for the demo workflow.
- The backend is local-demo ready, not cloud-deployed.

## Judge Takeaway

KshetraAI has a working FastAPI layer that exposes daily plan, recommendation, alerts, explanations, and outcome submission without mixing transport logic with intelligence logic.


\newpage

# Frontend Dashboard and Workflow Layer

## Purpose

Turn backend intelligence outputs into a usable field-force workflow that a judge or representative can follow end to end.

## Implementation Summary

- Built a React + TypeScript frontend using Vite.
- Implemented a dashboard workflow shell.
- Added pages for overview, daily plan, recommendation/explanation, alerts, and outcome submission.
- Added a typed API client for backend endpoints.
- Added hooks for API data loading.
- Added loading, error, empty, and success states.
- Added pagination for daily plan and alerts.
- Refined the UI with compact cards, status badges, and clearer action buttons.

## How It Works

The frontend stores a selected rep, territory, date, and entity. It calls backend endpoints through one API client and renders the returned intelligence outputs without recalculating scores, recommendations, alerts, or explanations in the browser.

## Frontend Workflow

Implemented workflow steps:

- Overview
- Daily Plan
- Recommendation
- Alerts
- Outcome

Default demo selection:

```text
rep_id: REP_0164
territory_id: TER_0164
plan_date: 2026-05-17
selected_entity_id: RTL_01300
```

## Demo Evidence

Frontend app files:

- `frontend/main.tsx`
- `frontend/App.tsx`
- `frontend/pages/Dashboard.tsx`
- `frontend/pages/VisitPlan.tsx`
- `frontend/pages/RecommendationView.tsx`
- `frontend/pages/AlertsView.tsx`
- `frontend/pages/OutcomeSubmission.tsx`
- `frontend/services/apiClient.ts`

Current UI behavior:

- daily plan page size: `3`
- alerts page size: `3`
- daily-plan cards show score, priority, and action button
- alert cards show score, severity, and confidence
- recommendation appears before explanation
- low / medium / high labels use shared color styling

## Verification

Relevant implementation areas:

- `frontend/components/`
- `frontend/hooks/`
- `frontend/pages/`
- `frontend/services/apiClient.ts`
- `frontend/state/workflowStore.ts`
- `frontend/styles/global.css`
- `tests/test_build09_frontend_workflow.py`

Focused Build 09 tests and the frontend production build were verified during development:

```text
python -m unittest tests.test_build09_frontend_workflow
npm run build
```

## Current Limits

- The frontend does not implement authentication.
- The frontend does not include a map or route optimization view.
- The frontend does not compute intelligence logic; it displays backend outputs.
- Current frontend checks are Python static workflow tests plus TypeScript/Vite build, not a full browser automation suite.

## Judge Takeaway

KshetraAI includes a working frontend workflow that makes the backend intelligence usable: plan, action, explanation, alert, and outcome.


\newpage

# Demo Integration, Testing, and Final Polish

## Purpose

Package the implemented system into a deterministic, judge-facing demo path with supporting artifacts, verification scripts, and sanitized sample outputs.

## Implementation Summary

- Created a deterministic demo scenario.
- Added a runbook, judging flow, presentation script, and checklist.
- Added a demo output generator.
- Added workflow verification and acceptance-check scripts.
- Generated sanitized API-level sample JSON outputs.
- Added Build 10 regression tests for demo readiness.

## How It Works

The demo uses one fixed scenario, verifies that backend/frontend artifacts exist, checks that processed outputs support the scenario, and validates sample API payloads for the final judge-facing workflow.

## Fixed Demo Scenario

Scenario file:

```text
demo/scenarios/amritsar_crop_protection_scenario.md
```

Scenario identity:

```text
scenario_id: AMRITSAR_CROP_PROTECTION_001
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
selected_entity: RTL_01300
```

Demo path:

```text
Dashboard -> Daily Plan -> Recommendation -> Explanation -> Alerts -> Outcome
```

## Demo Evidence

Sample API-level outputs:

- `demo/sample_outputs/daily_plan_response.json`
- `demo/sample_outputs/recommendation_response.json`
- `demo/sample_outputs/alerts_response.json`
- `demo/sample_outputs/explanation_response.json`
- `demo/sample_outputs/outcome_submission_response.json`

Current sample facts:

- top daily-plan entity: `RTL_01300`
- fixed scenario daily-plan rows: `23`
- recommendation rows for top entity: `3`
- explanation rows for top entity: `6`
- alert rows for fixed territory: `19`
- outcome response status: `success`

## Verification

Demo verification scripts:

```text
python demo\scripts\verify_demo_workflow.py
python demo\scripts\run_acceptance_checks.py
```

Current checks verify:

- required demo docs exist
- required frontend workflow files exist
- backend API route contract is present
- processed outputs exist
- fixed scenario rows exist
- top entity is stable
- sample output files exist
- sample payload shapes are valid
- configured forbidden raw-field terms are not present in sample outputs

Relevant tests:

- `tests/test_build10_demo_workflow.py`
- `tests/test_build10_acceptance_checks.py`

## Current Limits

- The demo is local and deterministic, not cloud-deployed.
- Screenshots are not the primary committed evidence; sample API outputs and the live frontend/backend path are.
- The sanitization check is a configured demo-artifact check, not a complete enterprise privacy audit.
- Build 10 does not add new intelligence behavior; it integrates and verifies the existing system.

## Judge Takeaway

KshetraAI is packaged with a repeatable demo scenario, verified outputs, and acceptance checks that connect the data, backend intelligence, API, frontend, and outcome workflow.

\newpage
\thispagestyle{empty}
\begin{center}
\vspace*{3.2cm}
{\color{KshetraGreen}\rule{0.62\textwidth}{1pt}\par}
\vspace{1.7cm}
{\Huge\bfseries\color{KshetraGreen} KshetraAI\par}
\vspace{1.0cm}
{\Large\color{KshetraSlate} Explainable. Deterministic. Human-governed.\par}
\vfill
{\LARGE\bfseries\color{KshetraSlate} Thank you.\par}
\vfill
{\large\color{KshetraSlate} Stage 1 Submission\par}
\vspace{0.22cm}
{\large\color{KshetraSlate} Syngenta Hackathon\par}
\vspace{0.22cm}
{\large\color{KshetraSlate} May 2026\par}
\vspace{1.2cm}
{\color{KshetraLeaf}\rule{0.36\textwidth}{0.8pt}\par}
\end{center}
