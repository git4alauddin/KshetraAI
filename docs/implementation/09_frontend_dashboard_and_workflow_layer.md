# Build 09 — Frontend Dashboard & Workflow Layer

---

# 1. Build Objective

The purpose of this build is to implement the frontend dashboard that presents KshetraAI intelligence outputs in a clear, explainable, and workflow-oriented interface.

This build converts:

```text
Backend API outputs
```

into:

```text
Field-representative-facing operational workflows.
```

The frontend should allow users to:

- view daily prioritized visit plans
- inspect entity-level recommendations
- review anomaly alerts
- understand explanations and evidence
- submit visit outcomes and feedback

This build does not implement:

- backend intelligence logic
- priority scoring
- recommendation generation
- anomaly detection
- explanation generation
- data pipeline logic
- schema mutation
- autonomous frontend-side reasoning

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/06_prototype.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/09_frontend_dashboard_contract.md`
- `docs/implementation_contracts/00_global_implementation_protocol.md`
- `docs/prompts/01_coding_session_prompt.md`
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

- Implement frontend dashboard shell
- Implement territory/rep selection workflow
- Display ranked daily visit plan
- Display recommendation details
- Display anomaly alerts
- Display explanation and evidence panels
- Implement outcome submission form
- Connect frontend to FastAPI backend endpoints
- Handle loading states and errors
- Preserve API contract stability
- Maintain workflow clarity for demo

---

## Out of Scope

- Backend scoring logic
- Backend recommendation logic
- Backend anomaly detection logic
- Backend explanation generation logic
- Data pipeline implementation
- API schema redesign
- Advanced authentication
- Complex mobile offline sync
- Heavy dashboard analytics
- Frontend-side intelligence generation

---

# 4. Core Philosophy

The Frontend Dashboard should behave as:

```text
An operational intelligence interface.
```

The frontend should remain:

- simple
- clear
- workflow-driven
- explainability-focused
- backend-driven
- demo-stable

The frontend should NOT:

- recreate backend logic
- compute scores
- infer recommendations
- generate anomaly alerts
- mutate API schemas

Its responsibility is ONLY:

```text
Present backend intelligence outputs
and capture user workflow inputs.
```

---

# 5. Backend API Dependencies

This build consumes outputs from Build 08.

Expected API endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | Backend health check |
| `GET /daily-plan` | Ranked visit plan |
| `GET /recommendations/{entity_id}` | Entity recommendation |
| `GET /alerts` | Active alerts |
| `GET /explanations/{entity_id}` | Explanation details |
| `POST /outcomes` | Submit visit outcome |

---

# 6. Expected Frontend Screens

The frontend should implement:

| Screen | Purpose |
|---|---|
| Dashboard / Home | Entry point |
| Territory Selection | Select rep, territory, date |
| Daily Visit Plan | Show ranked visit recommendations |
| Recommendation Detail | Show entity-level next best action |
| Alert Panel | Show anomaly/opportunity alerts |
| Explanation Panel | Show reasoning and evidence |
| Outcome Submission | Capture visit result |

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
frontend/
tests/frontend/
docs/implementation/
```

If necessary, API endpoint URLs may be referenced through frontend config.

---

# 8. Forbidden File Scope

This build must not modify:

```text
private-data/
backend/
datasets/
docs/architecture/
docs/implementation_contracts/
```

Backend changes are forbidden unless explicitly requested.

---

# 9. Recommended Frontend Structure

Suggested structure:

```text
frontend/

├── components/
│   ├── PriorityCard.tsx
│   ├── RecommendationPanel.tsx
│   ├── AlertPanel.tsx
│   ├── ExplanationPanel.tsx
│   ├── OutcomeForm.tsx
│   ├── ScoreBadge.tsx
│   ├── EvidenceList.tsx
│   └── LoadingState.tsx
│
├── pages/
│   ├── Dashboard.tsx
│   ├── VisitPlan.tsx
│   ├── RecommendationView.tsx
│   ├── AlertsView.tsx
│   └── OutcomeSubmission.tsx
│
├── services/
│   └── apiClient.ts
│
├── hooks/
│   ├── useDailyPlan.ts
│   ├── useRecommendation.ts
│   ├── useAlerts.ts
│   ├── useExplanation.ts
│   └── useSubmitOutcome.ts
│
├── state/
│   └── workflowStore.ts
│
├── layouts/
├── styles/
└── utils/
```

---

# 10. UI Workflow

The frontend should support this flow:

```text
Open Dashboard
        ↓
Select Rep / Territory / Date
        ↓
Load Daily Plan
        ↓
Select Recommended Entity
        ↓
View Recommendation + Explanation + Alerts
        ↓
Submit Visit Outcome
        ↓
Show Confirmation
```

---

# 11. Territory Selection Requirements

The selection screen should capture:

| Field | Purpose |
|---|---|
| `rep_id` | Field representative |
| `territory_id` | Operational region |
| `date` | Planning date |

This input is used to fetch:

```text
Daily visit plan.
```

---

# 12. Daily Visit Plan Requirements

The daily plan view should show:

| Field | Purpose |
|---|---|
| Rank | Visit order |
| Entity Name | Retailer/grower |
| Entity Type | Retailer / grower |
| Priority Score | Urgency |
| Priority Level | Critical / High / Medium / Low |
| Main Reason | Short operational reason |
| Action CTA | Open details |

---

# 13. Recommendation Detail Requirements

The recommendation view should show:

| Field | Purpose |
|---|---|
| Entity Name | Visit target |
| Risk / Opportunity | Main context |
| Recommended Actions | Next best action |
| Product Category | Suggested discussion |
| Confidence Level | Trust signal |
| Priority Score | Operational urgency |

---

# 14. Alert Panel Requirements

The alert panel should show:

| Field | Purpose |
|---|---|
| Alert Type | Stock-out / demand spike / crop stress |
| Severity Level | Critical / High / Moderate / Low |
| Confidence Level | Evidence confidence |
| Supporting Evidence | Why alert exists |

---

# 15. Explanation Panel Requirements

The explanation panel should show:

- summary explanation
- evidence items
- confidence reasoning
- contributing signals
- source trace references if available

Explainability should remain visible and easy to understand.

---

# 16. Outcome Form Requirements

The outcome form should capture:

| Field | Type |
|---|---|
| `recommendation_id` | string |
| `entity_id` | string |
| `rep_id` | string |
| `visit_completed` | boolean |
| `recommendation_followed` | boolean |
| `sale_made` | boolean |
| `order_placed` | boolean |
| `order_value` | number |
| `rep_feedback` | text |
| `alert_validated` | boolean |

Submitted to:

```text
POST /outcomes
```

---

# 17. API Integration Rules

Frontend must consume backend APIs through:

```text
frontend/services/apiClient.ts
```

Avoid API calls scattered across components.

Components should use hooks such as:

```text
useDailyPlan
useRecommendation
useAlerts
useExplanation
useSubmitOutcome
```

---

# 18. State Management Requirements

State should remain simple and predictable.

Allowed:

```text
React state
React Context
Zustand
```

Avoid:

- overengineered global state
- complex state machines
- frontend-side derived intelligence

---

# 19. Explainability Visibility Rules

The UI must make explainability visible.

Do not hide:

- why entity was prioritized
- why action was suggested
- why alert was triggered
- confidence level
- supporting evidence

This is core to the project.

---

# 20. Frontend Anti-Intelligence Rule

The frontend MUST NOT:

- calculate priority score
- infer recommendation
- generate anomaly
- rewrite explanation
- mutate backend intelligence output

The frontend may only:

```text
format and display backend-provided intelligence.
```

---

# 21. Loading and Error Handling

The frontend must include:

- loading states
- empty states
- API error states
- form validation errors
- successful submission confirmation

Example:

```text
Unable to load daily plan. Please check backend connection.
```

---

# 22. Determinism Requirements

Given identical API responses:

```text
Frontend rendering must remain stable.
```

Requirements:

- stable list ordering from API
- no random UI ordering
- no client-side hidden filtering unless explicit
- no unstable derived intelligence

---

# 23. Styling Requirements

The UI should prioritize:

- clarity
- readability
- operational hierarchy
- clean visual grouping

Recommended:

```text
TailwindCSS
```

Avoid:

- heavy animations
- visual overload
- excessive charts
- dashboard clutter

---

# 24. Demo-Focused UI Requirements

The interface should clearly demonstrate:

```text
Signal → Priority → Action → Explanation → Outcome
```

The demo should be understandable without technical explanation.

---

# 25. Testing Requirements

Tests should validate:

- dashboard renders
- daily plan loads
- recommendation detail renders
- alerts render
- explanation panel renders
- outcome form validates
- API errors display
- no frontend-side scoring exists

---

# 26. Anti-Drift Rules

This build MUST NOT:

- modify backend code
- compute intelligence in frontend
- change API schemas
- invent hidden frontend logic
- add complex unrelated UI features
- redesign architecture

This build is ONLY responsible for:

```text
Frontend workflow and intelligence visualization.
```

---

# 27. Deliverables

Expected outputs:

- frontend dashboard shell
- territory selection workflow
- daily plan view
- recommendation detail view
- alert panel
- explanation panel
- outcome form
- API client layer
- frontend hooks
- loading and error states
- basic frontend tests

---

# 28. Completion Criteria

This build is complete when:

- frontend connects to backend APIs
- daily plan is visible
- recommendation detail is visible
- anomaly alerts are visible
- explanations are visible
- outcome form submits successfully
- UI remains backend-driven
- no business logic exists in frontend
- architecture boundaries remain preserved

---

# 29. Final One-Line Definition

```text
A backend-driven frontend dashboard
that presents KshetraAI operational intelligence
through a clear,
explainable,
workflow-oriented field-force interface
without duplicating backend logic.
```

---

# 30. Task Breakdown & Execution Order

Use `docs/implementation/build_execution_prompt.md` while working through this build.

Each task heading below is intended to be usable as the future commit heading. Work one task at a time: present the heading, short brief, expected file scope, and what will not be touched; then wait for explicit implementation approval.

| Order | Commit Heading | Scope | Primary Files |
|---|---|---|---|
| 1 | Build 09: Create frontend application shell | Establish the dashboard shell, routing/layout basics, and workflow frame. | `frontend/` |
| 2 | Build 09: Implement API client and state hooks | Connect frontend views to backend endpoints without duplicating backend business logic. | `frontend/services/`, `frontend/hooks/` |
| 3 | Build 09: Implement daily visit plan view | Present ranked daily visit priorities and supporting context from API responses. | `frontend/pages/`, `frontend/components/priority/` |
| 4 | Build 09: Implement recommendation and explanation views | Show next-best-action details, evidence, confidence, and explanation content from backend data. | `frontend/components/recommendations/`, `frontend/components/explainability/` |
| 5 | Build 09: Implement alert and outcome views | Display anomaly alerts and capture outcome feedback through backend APIs. | `frontend/components/alerts/`, `frontend/components/outcomes/` |
| 6 | Build 09: Add frontend workflow tests | Validate rendering, loading/error states, API-driven behavior, and outcome submission flow. | `frontend/`, `tests/` |
| 7 | Build 09: Verify frontend workflow checklist | Confirm this build is UI-only and does not compute intelligence, change API schemas, or modify backend logic. | `docs/implementation/09_frontend_dashboard_and_workflow_layer.md` |

Per-task completion rule: after the human commits and says done, verify the committed scope, confirm the matching checklist items, and propose the next task.

---

# 31. Build Verification Checklist

Build status:

```text
Under Review
```

This build has implemented the frontend workflow layer as a backend-driven interface. The frontend consumes Build 08 API outputs, displays operational intelligence, and captures outcome feedback without duplicating backend scoring, recommendation, anomaly, explanation, or learning logic.

## 31.1 Implemented Task Checklist

| Order | Commit Heading | Verification Status | Evidence |
|---|---|---|---|
| 1 | Build 09: Create frontend application shell | Complete | Frontend Vite/React shell, dashboard layout, navigation, workflow state, and base styling are implemented under `frontend/`. |
| 2 | Build 09: Implement API client and state hooks | Complete | `frontend/services/apiClient.ts` and hooks for health, daily plan, recommendation, alerts, explanations, and outcome submission are implemented. |
| 3 | Build 09: Implement daily visit plan view | Complete | `frontend/pages/VisitPlan.tsx` renders ranked entities from `GET /daily-plan` with loading, error, and empty states. |
| 4 | Build 09: Implement recommendation and explanation views | Complete | `frontend/pages/RecommendationView.tsx` renders `GET /recommendations/{entity_id}` and `GET /explanations/{entity_id}` outputs. |
| 5 | Build 09: Implement alert and outcome views | Complete | `frontend/pages/AlertsView.tsx` consumes `GET /alerts`; `frontend/pages/OutcomeSubmission.tsx` and `frontend/components/OutcomeForm.tsx` submit `POST /outcomes`. |
| 6 | Build 09: Add frontend workflow tests | Complete | `tests/test_build09_frontend_workflow.py` validates endpoint contracts, hook usage, UI states, outcome payload fields, and anti-intelligence boundaries. |
| 7 | Build 09: Verify frontend workflow checklist | Complete | This verification section records completed scope, boundary checks, and test evidence. |

## 31.2 API Integration Verification

The frontend consumes backend endpoints only through:

```text
frontend/services/apiClient.ts
```

Verified endpoint coverage:

| Endpoint | Frontend Consumer |
|---|---|
| `GET /health` | `useHealth` |
| `GET /daily-plan` | `useDailyPlan`, `VisitPlan` |
| `GET /recommendations/{entity_id}` | `useRecommendation`, `RecommendationView` |
| `GET /alerts` | `useAlerts`, `AlertsView` |
| `GET /explanations/{entity_id}` | `useExplanation`, `RecommendationView` |
| `POST /outcomes` | `useSubmitOutcome`, `OutcomeSubmission`, `OutcomeForm` |

No page component performs direct scattered API access. Page components use hooks, and hooks delegate to the API client.

## 31.3 UI Workflow Verification

The implemented frontend supports the intended workflow:

```text
Dashboard selection
        ->
Daily visit plan
        ->
Recommendation and explanation review
        ->
Alert review
        ->
Outcome submission
```

Verified UI states:

- daily plan loading, error, empty, and populated states
- recommendation loading, error, empty, and populated states
- explanation loading, error, empty, and populated states
- alert loading, error, empty, and populated states
- outcome form validation, submit, error, and success states

## 31.4 Outcome Capture Verification

The outcome form captures and submits the required Build 09 fields:

| Field | Status |
|---|---|
| `recommendation_id` | Captured |
| `entity_id` | Captured |
| `rep_id` | Captured |
| `visit_completed` | Captured |
| `recommendation_followed` | Captured |
| `sale_made` | Captured |
| `order_placed` | Captured |
| `order_value` | Captured and validated |
| `alert_validated` | Captured |
| `rep_feedback` | Captured |
| `feedback_category` | Captured as optional API-supported context |
| `alert_id` | Captured as optional API-supported context |

Validation preserves frontend responsibility only:

- required identifiers must be present
- order value must be zero or positive
- submitted payload shape follows the existing API contract

## 31.5 Anti-Drift Verification

Build 09 did not modify forbidden implementation areas:

```text
backend/
datasets/
private-data/
docs/architecture/
docs/implementation_contracts/
```

The frontend does not:

- calculate priority scores
- infer recommendations
- generate anomaly alerts
- rewrite explanations
- mutate API schemas
- implement backend learning logic

Frontend behavior is limited to:

```text
formatting backend responses,
displaying operational intelligence,
handling loading/error/empty states,
and submitting user outcome inputs.
```

## 31.6 Verification Commands

The following checks were run successfully:

```powershell
npm run build
python -m unittest discover tests
```

Observed result:

```text
Frontend production build passed.
Backend and contract regression suite passed with Build 09 workflow tests included.
```

## 31.7 Completion Decision

Build 09 satisfies the completion criteria for a V1 prototype frontend:

- frontend connects to backend APIs
- daily plan is visible
- recommendation detail is visible
- anomaly alerts are visible
- explanations are visible
- outcome form submits through the API client
- UI remains backend-driven
- no frontend-side intelligence logic was introduced
- architecture boundaries remain preserved

Build 09 is ready for human review and final project status update.
