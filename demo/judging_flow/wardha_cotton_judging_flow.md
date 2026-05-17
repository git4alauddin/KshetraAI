# Wardha Cotton Judging Flow

## Goal

Show KshetraAI as a complete, explainable field-force intelligence workflow.
The judge should understand the operational value without needing to inspect
the code.

## One-Minute Setup

```text
KshetraAI helps an agricultural field representative decide who to visit,
why that visit matters, what action to take, what alert to watch, and how
the field outcome is captured for future improvement.
```

## Demo Path

| Order | Screen Or Endpoint | Presenter Action | Judge Takeaway |
|---|---|---|---|
| 1 | Dashboard | Show `REP001`, `TERR_WARDHA_01`, and `2026-05-17` | The workflow starts from a controlled field context |
| 2 | Daily Plan | Open ranked visit plan | The system prioritizes visits from signals |
| 3 | Recommendation | Open top entity details | The rep gets a concrete next best action |
| 4 | Explanation | Show evidence and confidence | The recommendation is traceable |
| 5 | Alerts | Show active risk or opportunity alert | The system detects operational exceptions |
| 6 | Outcome | Submit visit result | The loop closes with feedback |

## Presenter Talking Points

### Problem

Field reps often work from static schedules while field conditions, inventory,
demand, and crop risk shift quickly.

### Prioritization

KshetraAI creates a ranked daily plan so the representative can focus on the
most urgent and valuable visit first.

### Recommendation

For the selected entity, the system gives a contextual next best action rather
than a generic instruction.

### Alerts

The alert panel exposes the operational risk, such as low stock or crop stress,
so the rep can act before the opportunity is missed.

### Explainability

The explanation panel shows evidence and confidence, keeping the workflow
transparent and human-governed.

### Outcome

The outcome form records what happened, whether the advice was followed, and
whether a sale or order was placed.

## Success Metrics Connection

| Success Metric | Demo Evidence |
|---|---|
| Revenue per field day | Top visits are prioritized by opportunity and urgency |
| Coverage efficiency | The daily plan makes the rep's day more focused |
| Recommendation acceptance | Confidence and evidence improve trust |
| Adaptive improvement | Outcome capture creates a feedback signal |

## Fallback Path

If the frontend cannot reach the backend:

1. Show `GET /health` response if available.
2. Show saved sample output files once they are captured.
3. Explain the same Signal -> Priority -> Action -> Explanation -> Outcome flow.
4. Record the backend connection issue as demo readiness risk.

If an endpoint returns empty data:

1. Confirm the fixed scenario filters.
2. Verify processed output availability.
3. Use sample outputs only as a fallback, not as a replacement for integration.

## Do Not Show

- Private raw company files.
- Internal implementation traces that expose private data.
- Random or manually edited outputs.
- New unapproved business logic.
