# Demo Presentation Checklist

## Before Recording Or Presenting

- Run `python demo\scripts\generate_demo_outputs.py`.
- Run `python demo\scripts\verify_demo_workflow.py`.
- Run `python -m unittest discover tests`.
- Run `npm run build` from `frontend/`.
- Confirm `demo/sample_outputs/` contains the five API-level JSON files.
- Confirm no raw `private-data/` content is copied into demo artifacts.

## Live Demo Readiness

| Check | Expected |
|---|---|
| Backend health | `GET /health` returns available service status |
| Daily plan | `REP_0164`, `TER_0164`, `2026-05-17` returns ranked entities |
| Selected entity | top entity is `RTL_01300` |
| Recommendation | recommendation response is available for `RTL_01300` |
| Alerts | alerts response includes territory alerts for `TER_0164` |
| Explanation | explanation response includes evidence for `RTL_01300` |
| Outcome | valid outcome submission returns success |

## Presenter Reminders

- Keep the demo operational, not technical.
- Emphasize explainability and human governance.
- Mention that sample outputs are sanitized API-level artifacts.
- Avoid showing raw private data or large processed CSV files.
- Use the fallback sample outputs if the live server path is unstable.

## Final Close

End with:

```text
KshetraAI makes field execution adaptive, explainable, and measurable. It helps
the representative decide where to go, what to do, why it matters, and what
actually happened after the visit.
```
