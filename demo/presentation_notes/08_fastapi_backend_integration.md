# Module 08: FastAPI Backend Integration

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
