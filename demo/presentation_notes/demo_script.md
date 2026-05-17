# KshetraAI Demo Script

## Opening

KshetraAI is an explainable field-force intelligence workflow for agricultural
sales operations. The demo shows how a representative moves from a static visit
plan to a signal-driven plan, a contextual recommendation, visible alerts,
evidence-backed explanations, and outcome capture.

This demo uses the Amritsar crop protection scenario:

```text
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
selected_entity: RTL_01300
```

The sample outputs are derived from the locally provided company data and saved
as sanitized API-level JSON under `demo/sample_outputs/`.

## Demo Sequence

### 1. Start With The Problem

Say:

```text
Field representatives often work from fixed schedules, but field conditions,
inventory movement, demand, and risk signals change faster than the schedule.
KshetraAI turns those signals into an explainable daily workflow.
```

Show:

- dashboard context
- `REP_0164`
- `TER_0164`
- `2026-05-17`

### 2. Show Dynamic Prioritization

Open the daily plan.

Point out:

- the ranked visit list
- selected entity `RTL_01300`
- priority score
- priority level
- main reason: inventory need is the strongest signal

Use sample output:

```text
demo/sample_outputs/daily_plan_response.json
```

Say:

```text
The system is not just listing accounts. It is ranking visit priority from
available operational signals and keeping the reason visible.
```

### 3. Show The Next Best Action

Open the recommendation view for `RTL_01300`.

Point out:

- risk/opportunity: possible fast-moving stock pressure
- recommended action: review SKU availability and reorder timing
- product category: relevant seasonal SKU
- confidence level: Medium

Use sample output:

```text
demo/sample_outputs/recommendation_response.json
```

Say:

```text
The rep gets a concrete operational action, not a generic dashboard metric.
```

### 4. Show Explainability

Show the explanation panel.

Point out:

- priority explanation
- recommendation explanation
- anomaly explanation
- evidence items
- confidence levels

Use sample output:

```text
demo/sample_outputs/explanation_response.json
```

Say:

```text
Every recommendation is explainable. The user can see the evidence and decide
whether the advice makes operational sense.
```

### 5. Show Alerts

Open the alert view.

Point out:

- stock-out risk alert for `RTL_01300`
- severity score
- severity level
- confidence level

Use sample output:

```text
demo/sample_outputs/alerts_response.json
```

Say:

```text
This lets the representative act before an inventory or opportunity signal is
missed.
```

### 6. Close The Loop With Outcome Capture

Open the outcome form and submit a valid outcome.

Point out:

- visit completed
- recommendation followed
- sale/order captured
- alert validated
- rep feedback

Use sample output:

```text
demo/sample_outputs/outcome_submission_response.json
```

Say:

```text
The workflow does not stop at advice. It captures what happened in the field,
which creates the foundation for later performance tracking and human-reviewed
improvement.
```

## Success Metric Mapping

| Success Metric | Demo Evidence |
|---|---|
| Revenue per field day | The top visit is selected from opportunity and inventory signals |
| Coverage efficiency | The rep sees a ranked list instead of a static route |
| Recommendation acceptance | The recommendation includes evidence and confidence |
| Adaptive improvement | Outcome submission records what happened |

## Fallback Script

If the live frontend/backend path is unavailable, use the saved sample outputs:

1. Open `demo/sample_outputs/daily_plan_response.json`.
2. Show `RTL_01300` as the selected entity.
3. Open `recommendation_response.json`.
4. Open `alerts_response.json`.
5. Open `explanation_response.json`.
6. Open `outcome_submission_response.json`.

Say:

```text
These are sanitized API-level outputs generated from the same local data path.
The live workflow consumes this same response shape.
```

## Guardrails

Do not show:

- raw private data files
- full processed CSVs
- internal trace payloads unless needed for debugging
- any unapproved manual changes to scores or recommendations

Keep the story focused on:

```text
Signal -> Priority -> Action -> Alert -> Explanation -> Outcome
```
