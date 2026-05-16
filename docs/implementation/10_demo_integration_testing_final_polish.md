# Build 10 — Demo Integration, Testing & Final Polish

---

# 1. Build Objective

The purpose of this build is to integrate all completed KshetraAI components into a stable, deterministic, and presentation-ready prototype.

This build converts:

```text
Individual working components
```

into:

```text
A coherent end-to-end demo workflow.
```

The final demo should clearly show:

- field rep workflow
- daily prioritized plan
- contextual next best action
- anomaly alerts
- evidence-backed explanations
- outcome submission
- feedback learning signal

This build does not implement new core intelligence logic.

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/06_prototype.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/10_demo_integration_contract.md`
- `docs/implementation_contracts/00_global_implementation_protocol.md`
- `docs/prompts/01_coding_session_prompt.md`
- `docs/prompts/02_code_review_prompt.md`
- `docs/prompts/03_architecture_preservation_prompt.md`

If conflict exists, use this authority order:

```text
Architecture docs
        ↓
Implementation contracts
        ↓
This build checklist
        ↓
Implementation task prompt
```

---

# 3. Build Scope

## In Scope

- Integrate backend and frontend workflows
- Validate end-to-end demo flow
- Prepare deterministic demo scenario
- Prepare sample outputs
- Run integration tests
- Verify API/frontend alignment
- Verify explanation visibility
- Verify outcome submission flow
- Prepare presentation/demo notes
- Polish UI and workflow consistency

---

## Out of Scope

- New scoring logic
- New feature engineering logic
- New recommendation rules
- New anomaly detection logic
- New explainability engine behavior
- New architecture redesign
- Production deployment infrastructure
- Advanced authentication
- Advanced offline sync
- New ML models

---

# 4. Core Philosophy

The demo integration layer should behave as:

```text
A stable end-to-end orchestration and presentation layer.
```

The goal is not to add more features.

The goal is to make the existing system:

- reliable
- understandable
- demo-ready
- deterministic
- operationally coherent

---

# 5. Required Integrated Workflow

The final demo should support this workflow:

```text
Open Dashboard
        ↓
Select Rep / Territory / Date
        ↓
Load Daily Visit Plan
        ↓
Select Top Recommended Entity
        ↓
View Priority Score + Component Breakdown
        ↓
View Next Best Action
        ↓
View Anomaly Alerts
        ↓
View Evidence-Based Explanation
        ↓
Submit Visit Outcome
        ↓
Confirm Feedback Logged
```

---

# 6. Required Components to Integrate

| Component | Integration Required |
|---|---|
| Data Pipeline | Yes |
| Feature Builder | Yes |
| Priority Engine | Yes |
| Contextual Decision Engine | Yes |
| Anomaly Detection Engine | Yes |
| Explainability Engine | Yes |
| Outcome Learning Engine | Yes |
| FastAPI Backend | Yes |
| Frontend Dashboard | Yes |

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
frontend/
backend/api/
backend/main.py
demo/
tests/integration/
docs/demo/
docs/implementation/
```

Limited config changes are allowed only if needed for integration.

---

# 8. Forbidden File Scope

This build must not modify:

```text
private-data/
backend/features/
backend/engines/
backend/anomaly/
backend/explainability/
backend/learning/
docs/architecture/
docs/implementation_contracts/
```

unless explicitly required to fix a verified integration bug.

No architecture changes are allowed during final polish.

---

# 9. Demo Scenario Requirements

The demo should use one clear scenario.

Recommended scenario:

| Field | Value |
|---|---|
| Rep | REP001 |
| Territory | Wardha |
| Primary Crop | Cotton |
| Main Risk | Possible fungal disease risk |
| Commercial Context | Fungicide demand increasing |
| Inventory Context | Low fungicide stock |
| Alert | Stock-out risk / crop stress |
| Action | Visit retailer, inspect context, discuss fungicide advisory, recommend restocking |

---

# 10. Demo Data Requirements

Demo data should be:

- deterministic
- stable
- locally available
- explainable
- aligned with the story

Avoid:

- live API dependency
- random scenario generation
- inconsistent outputs
- unstable dates unless controlled

---

# 11. Demo Output Requirements

The final demo should visibly show:

## Daily Visit Plan

```text
Ranked entities with priority scores and levels.
```

## Recommendation Detail

```text
Next best action with product/advisory context.
```

## Alert Panel

```text
Anomaly or opportunity alert with severity.
```

## Explanation Panel

```text
Evidence-backed reasoning and confidence.
```

## Outcome Form

```text
Visit feedback and result capture.
```

---

# 12. Integration Validation Requirements

Validate:

- backend starts successfully
- frontend starts successfully
- frontend connects to backend
- daily plan loads
- recommendation detail loads
- alerts load
- explanations load
- outcome submission works
- no frontend-side intelligence logic exists
- no backend route business logic duplication exists

---

# 13. End-to-End Test Requirements

Integration tests should verify:

- health endpoint works
- daily plan endpoint returns expected schema
- recommendation endpoint returns expected schema
- alerts endpoint returns expected schema
- explanation endpoint returns expected schema
- outcome submission endpoint accepts valid payload
- frontend can render primary workflow
- deterministic demo scenario remains stable

---

# 14. Explainability Visibility Checklist

The demo must clearly show:

| Item | Visible |
|---|---|
| Priority score | Yes |
| Priority level | Yes |
| Main reason | Yes |
| Evidence items | Yes |
| Confidence level | Yes |
| Recommended action | Yes |
| Alert severity | Yes |

Explainability should not be hidden behind technical logs only.

---

# 15. Stability Requirements

The final demo must avoid:

- flaky API behavior
- unstable frontend state
- missing sample data
- random outputs
- broken routes
- missing explanations
- inconsistent entity IDs

---

# 16. Error Handling Requirements

The demo should gracefully handle:

- backend offline
- empty daily plan
- missing recommendation
- missing explanation
- failed outcome submission

Example:

```text
Unable to load recommendations. Please check backend connection.
```

---

# 17. Demo Folder Requirements

Recommended structure:

```text
demo/

├── scenarios/
│   └── wardha_cotton_scenario.md
│
├── sample_outputs/
│   ├── daily_plan_response.json
│   ├── recommendation_response.json
│   ├── alerts_response.json
│   ├── explanation_response.json
│   └── outcome_submission_response.json
│
├── screenshots/
│
├── presentation_notes/
│   └── demo_script.md
│
└── runbook.md
```

---

# 18. Demo Script Requirements

The demo script should explain:

```text
Before KshetraAI:
Field reps followed static visit schedules.

After KshetraAI:
The rep receives a prioritized plan based on signals,
understands why each visit matters,
knows what action to take,
and the system captures outcomes for future improvement.
```

---

# 19. Final Presentation Storyline

The final storyline should follow:

```text
Problem
   ↓
Signal-driven prioritization
   ↓
Contextual next best action
   ↓
Anomaly detection
   ↓
Explainability
   ↓
Outcome learning
   ↓
Operational impact
```

---

# 20. Success Metric Alignment

The demo should connect clearly to official success metrics:

| Success Metric | Demo Evidence |
|---|---|
| Revenue per field day | Prioritizes high-opportunity visits |
| Coverage efficiency | Ranks urgent and feasible accounts |
| Recommendation acceptance | Shows explainable reasoning and confidence |
| Adaptive improvement | Captures outcome feedback |

---

# 21. Anti-Drift Rules

This build MUST NOT:

- add new intelligence logic
- change scoring formulas
- change recommendation rules
- change anomaly thresholds unless fixing verified bugs
- redesign schemas
- redesign architecture
- introduce new infrastructure
- silently alter API contracts

This build is ONLY responsible for:

```text
Integration,
testing,
demo stability,
and presentation polish.
```

---

# 22. Logging Requirements

Final integration should log:

- backend startup
- API failures
- outcome submission events
- integration test failures
- demo scenario loading

Avoid noisy logs that distract from debugging.

---

# 23. Completion Criteria

This build is complete when:

- full workflow runs end-to-end
- backend and frontend integrate cleanly
- demo scenario is stable
- explanations are visible
- alerts are visible
- outcome submission works
- tests pass
- demo runbook exists
- presentation story is clear
- architecture boundaries remain preserved

---

# 24. Final One-Line Definition

```text
A deterministic end-to-end demo integration build
that combines all KshetraAI components
into a stable,
explainable,
workflow-driven,
presentation-ready prototype.
```
