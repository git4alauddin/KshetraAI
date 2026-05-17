# Amritsar Crop Protection Demo Scenario

## Purpose

This scenario is the primary judge-facing Build 10 demo path for KshetraAI.
It shows how a field representative moves from static planning to explainable,
signal-driven execution.

The scenario is intentionally deterministic. It should use fixed inputs,
stable processed outputs, and the existing backend API contract.

## Scenario Identity

| Field | Value |
|---|---|
| Scenario ID | `AMRITSAR_CROP_PROTECTION_001` |
| Rep ID | `REP_0164` |
| Territory ID | `TER_0164` |
| Plan Date | `2026-05-17` |
| Region Story | Amritsar west territory |
| Primary Crop | Mixed Rabi crop protection context |
| Commercial Context | Crop protection demand and stock movement signals are active |
| Operational Risk | Low stock or fast-moving SKU risk at priority retailer |
| Agronomic Risk | Context depends on generated feature and alert outputs |
| Alert Focus | Stock-out risk and opportunity signals |
| Expected Action | Visit priority retailer, review stock position, discuss relevant advisory, and capture outcome |

## Demo Narrative

Before KshetraAI, the field representative would follow a fixed visit list
or rely on manual intuition. In this scenario, the system uses available
operational signals to generate a ranked daily plan, explain why the top
visit matters, recommend the next best action, expose relevant alerts, and
capture the result after the field visit.

The demo should make this operational loop visible:

```text
Signals
  -> Priority
  -> Recommendation
  -> Alert
  -> Explanation
  -> Outcome
```

## Fixed Demo Inputs

Use these values throughout the demo:

```text
rep_id: REP001
territory_id: TERR_WARDHA_01
date: 2026-05-17
```

The selected entity should come from the first ranked entity returned by:

```text
GET /daily-plan?rep_id=REP_0164&territory_id=TER_0164&date=2026-05-17
```

If the processed output has no matching rows during local development, use
the default frontend entity selection only as a temporary fallback and record
that as a demo readiness issue.

## Expected Backend Flow

The demo should call these endpoints in order:

| Step | Endpoint | Expected Evidence |
|---|---|---|
| 1 | `GET /health` | Backend is available |
| 2 | `GET /daily-plan` | Ranked daily visit plan |
| 3 | `GET /recommendations/{entity_id}` | Next best action for selected entity |
| 4 | `GET /explanations/{entity_id}` | Evidence-backed explanation |
| 5 | `GET /alerts?territory_id=TERR_WARDHA_01` | Active anomaly or opportunity alerts |
| 6 | `POST /outcomes` | Outcome accepted and logged |

## Expected Frontend Flow

The judge-facing UI path should be:

1. Open the dashboard.
2. Confirm rep, territory, date, and selected entity context.
3. Open the daily plan.
4. Select the top ranked entity.
5. Review recommendation and explanation panels.
6. Review alert panel.
7. Submit outcome feedback.
8. Confirm the success state.

## What The Judge Should See

| Capability | Visible Evidence |
|---|---|
| Dynamic prioritization | Ranked entity list with score, level, and reason |
| Contextual action | Recommended action and product/advisory context |
| Anomaly detection | Alert type, severity, and confidence |
| Explainability | Summary, evidence items, and confidence |
| Outcome learning | Submitted visit result and confirmation |

## Outcome Submission Payload

Use this payload shape during the demo, replacing IDs with actual values
returned by the API when available:

```json
{
  "recommendation_id": "<matched_rule_id>",
  "entity_id": "<selected_entity_id>",
  "rep_id": "REP_0164",
  "visit_completed": true,
  "recommendation_followed": true,
  "sale_made": true,
  "order_placed": true,
  "order_value": 25000,
  "alert_validated": true,
  "feedback_category": "useful",
  "rep_feedback": "Retailer confirmed demand and requested follow-up stock planning.",
  "alert_id": "<alert_id_if_available>"
}
```

## Determinism Rules

- Use the same rep, territory, and date for every demo run.
- Do not use live external services during the judge demo.
- Do not generate random scenario values.
- Do not manually edit backend outputs during presentation.
- Keep private raw company data out of screenshots and shared artifacts.

## Readiness Risks To Check

- Processed output files may not exist yet.
- Matching `REP001` and `TERR_WARDHA_01` rows must be confirmed.
- Selected entity must have recommendation and explanation outputs.
- Alerts should be available for the demo territory.
- Outcome submission must return a clear confirmation.
