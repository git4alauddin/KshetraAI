# KshetraAI Demo Runbook

## Purpose

This runbook defines the deterministic Build 10 demo verification flow.
It is used to confirm that backend, frontend, and demo story are aligned before
presentation.

## Primary Scenario

Use:

```text
demo/scenarios/amritsar_crop_protection_scenario.md
```

Fixed inputs:

```text
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
```

## Pre-Demo Checklist

- Backend dependencies are installed.
- Frontend dependencies are installed.
- Processed demo outputs exist under `datasets/processed/`.
- No private raw company data is referenced in demo artifacts.
- Full backend regression tests pass.
- Frontend production build passes.
- Build 09 frontend workflow tests pass.

## Verification Commands

Run backend tests:

```powershell
python -m unittest discover tests
```

Run frontend production build:

```powershell
cd frontend
npm run build
```

Run Build 10 demo workflow verification:

```powershell
python demo\scripts\verify_demo_workflow.py
```

The verifier should show no `FAIL` rows. `WARN` rows are acceptable during early
Build 10 only when processed demo outputs have not been captured yet.

Generate derived demo outputs from the local ignored company data:

```powershell
python demo\scripts\generate_demo_outputs.py
```

This writes ignored processed CSVs under `datasets/processed/` and sanitized
API-level sample JSON files under `demo/sample_outputs/`.

Run final demo acceptance checks:

```powershell
python demo\scripts\run_acceptance_checks.py
```

This validates the committed sample outputs, presentation notes, scenario IDs,
and workflow wiring.

Start backend locally:

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Start frontend locally:

```powershell
cd frontend
npm run dev
```

Frontend URL:

```text
http://127.0.0.1:5173/
```

Backend URL:

```text
http://127.0.0.1:8000/
```

## API Smoke Path

Check the endpoints in this order:

```text
GET /health
GET /daily-plan?rep_id=REP_0164&territory_id=TER_0164&date=2026-05-17
GET /recommendations/{entity_id}
GET /explanations/{entity_id}
GET /alerts?territory_id=TER_0164
POST /outcomes
```

Use the first ranked entity from `/daily-plan` as `{entity_id}`.

## Frontend Smoke Path

1. Open `http://127.0.0.1:5173/`.
2. Confirm rep, territory, and date.
3. Open Daily Plan.
4. Open the top entity recommendation.
5. Review recommendation and explanation evidence.
6. Open Alerts.
7. Open Outcome.
8. Submit a valid outcome.
9. Confirm success state.

## Expected Demo Evidence

| Evidence | Location |
|---|---|
| Scenario definition | `demo/scenarios/amritsar_crop_protection_scenario.md` |
| Judge flow | `demo/judging_flow/amritsar_crop_protection_judging_flow.md` |
| Sample API outputs | `demo/sample_outputs/` |
| Screenshots | `demo/screenshots/` |
| Presentation notes | `demo/presentation_notes/` |

Sample outputs and screenshots are captured in later Build 10 slices after the
integrated workflow is verified.

## Acceptance Criteria

The demo is ready when:

- backend starts successfully
- frontend starts successfully
- frontend connects to backend
- daily plan loads for the fixed scenario
- recommendation loads for selected entity
- explanation loads for selected entity
- alerts load for fixed territory
- outcome submission returns confirmation
- tests pass
- no private raw data is exposed
- no new intelligence logic was added in Build 10

## Demo Readiness Notes

If any check fails, record:

- failing command or screen
- expected behavior
- actual behavior
- affected file or endpoint
- whether it blocks judging

Do not patch scoring, recommendation, anomaly, explanation, or learning logic
unless a verified integration bug explicitly requires it.
