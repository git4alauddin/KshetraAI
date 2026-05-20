# Module 09: Frontend Dashboard and Workflow Layer

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
