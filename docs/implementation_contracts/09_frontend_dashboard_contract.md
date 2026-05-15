# KshetraAI — Frontend Dashboard Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the Frontend Dashboard Layer.

The Frontend Dashboard is responsible for:

```text
Presenting agricultural operational intelligence
through a clear, explainable,
and workflow-oriented user interface.
```

This layer acts as the operational interaction surface between:

```text
Field Representatives
        ↓
KshetraAI Intelligence System
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Frontend Dashboard |
| Layer | User Interaction Layer |
| Primary Responsibility | Operational intelligence visualization |
| Upstream Dependencies | API Layer |
| Downstream Consumers | Field Representatives, Demo Users |
| Architecture Criticality | High |

---

# 3. Core Philosophy

The Frontend Dashboard should remain:

- operationally clear
- explainability-focused
- workflow-oriented
- lightweight
- responsive
- deterministic

The frontend should NOT:

- contain business logic
- contain scoring logic
- contain anomaly logic
- contain recommendation generation
- recreate backend intelligence

Its responsibility is ONLY:

```text
Display intelligence outputs clearly
and support operational workflows.
```

---

# 4. Responsibilities

The Frontend Dashboard IS responsible for:

- rendering prioritized visit plans
- displaying contextual recommendations
- visualizing anomaly alerts
- presenting explainability outputs
- capturing outcome feedback
- supporting demo workflows
- managing UI state

---

# 5. Non-Responsibilities

The Frontend Dashboard is NOT responsible for:

- score calculation
- anomaly inference
- recommendation generation
- feature engineering
- business rule execution
- backend orchestration

These belong to backend intelligence modules.

---

# 6. UI Philosophy

The dashboard should prioritize:

```text
Operational clarity over visual complexity.
```

The interface should help users answer:

```text
Who should I visit?
Why?
What should I discuss?
What risk exists?
What happened after the visit?
```

---

# 7. Core Dashboard Screens

| Screen | Purpose |
|---|---|
| Territory Selection | Start workflow |
| Daily Visit Plan | Ranked entities |
| Recommendation Detail | Next best action |
| Alert Panel | Active anomalies |
| Explainability Panel | Operational reasoning |
| Outcome Submission | Feedback capture |

---

# 8. Territory Selection Screen

# Purpose

Allow selection of:

- field representative
- territory
- date

---

# Expected Inputs

```text
Rep selection
Territory selection
Date selection
```

---

# Expected Output

```text
Generate daily visit plan
```

---

# 9. Daily Visit Plan Screen

# Purpose

Display prioritized field visits.

---

# Displayed Information

| Field | Purpose |
|---|---|
| Entity Name | Visit target |
| Priority Score | Urgency |
| Priority Level | Classification |
| Main Reason | Operational summary |
| Action Summary | Short recommendation |

---

# Example UI Row

```text
Ramesh Agro Center
Priority: 84 (Critical)
Reason: Pest risk + low inventory
```

---

# 10. Recommendation Detail Screen

# Purpose

Display contextual next best actions.

---

# Displayed Information

- recommended actions
- recommended product category
- risk/opportunity summary
- confidence level

---

# Example Output

```text
Recommended Actions:
- Inspect crop symptoms
- Discuss fungicide advisory
- Recommend inventory replenishment
```

---

# 11. Alert Panel Screen

# Purpose

Display active anomalies and opportunities.

---

# Displayed Information

- anomaly type
- severity level
- evidence summary

---

# Example Output

```text
Stock-Out Risk — Critical
Inventory significantly below baseline
```

---

# 12. Explainability Panel

# Purpose

Display operational reasoning.

---

# Displayed Information

- explanation text
- evidence list
- contributing signals
- confidence reasoning

---

# Example Output

```text
High rainfall and humidity increase fungal disease risk for cotton crops currently in the flowering stage.
```

---

# 13. Outcome Submission Screen

# Purpose

Capture field visit results.

---

# Input Fields

| Field | Purpose |
|---|---|
| Visit Completed | Execution tracking |
| Recommendation Followed | Acceptance tracking |
| Sale Made | Conversion tracking |
| Order Placed | Commercial outcome |
| Rep Feedback | Human feedback |

---

# Example Submission

```text
Visit completed: Yes
Recommendation followed: Yes
Order placed: Yes
```

---

# 14. Allowed File Ownership

The AI MAY modify:

```text
frontend/
```

including:

```text
frontend/components/
frontend/pages/
frontend/services/
frontend/hooks/
frontend/state/
frontend/styles/
```

---

# 15. Forbidden File Ownership

The AI MUST NOT modify:

```text
backend/engines/
backend/explainability/
backend/anomaly/
contracts/
architecture_docs/
```

unless explicitly instructed.

---

# 16. Recommended Frontend Structure

```text
frontend/

├── components/
├── pages/
├── services/
├── hooks/
├── state/
├── styles/
├── layouts/
└── utils/
```

---

# 17. Recommended Component Structure

```text
frontend/components/

├── PriorityCard.tsx
├── RecommendationPanel.tsx
├── AlertPanel.tsx
├── ExplanationPanel.tsx
├── OutcomeForm.tsx
└── LoadingState.tsx
```

---

# 18. Recommended Pages Structure

```text
frontend/pages/

├── Dashboard.tsx
├── VisitPlan.tsx
├── RecommendationView.tsx
├── AlertsView.tsx
└── OutcomeSubmission.tsx
```

---

# 19. State Management Philosophy

The frontend should initially prioritize:

```text
Simple predictable state management.
```

Recommended:

```text
React Context
Zustand
```

Avoid:

```text
overengineered state architectures
```

---

# 20. API Interaction Rule

The frontend MUST consume:

```text
Backend API outputs only.
```

The frontend MUST NOT:

- recreate scoring logic
- infer anomalies
- compute recommendations
- duplicate backend reasoning

---

# 21. Explainability Preservation Rule

Explainability must remain highly visible.

The frontend should clearly display:

- reasoning
- evidence
- confidence
- score breakdowns

Avoid:

```text
hidden AI reasoning
```

---

# 22. Deterministic Rendering Rule

The frontend should remain:

```text
predictable and stable.
```

Avoid:

- uncontrolled dynamic rendering
- inconsistent component behavior
- hidden UI-side logic

---

# 23. UI Complexity Rule

The prototype UI should prioritize:

- readability
- operational workflow
- explainability visibility

NOT:

- advanced animations
- heavy dashboards
- visual overload

---

# 24. Styling Philosophy

Preferred:

```text
Clean operational dashboard styling.
```

Recommended:

```text
TailwindCSS
```

Avoid:

```text
heavy design systems
```

unless explicitly needed later.

---

# 25. Responsive Design Rule

The UI should support:

- desktop demo
- tablet usage
- future mobile adaptability

without heavy optimization requirements in V1.

---

# 26. Loading & Error Handling Rules

The frontend should clearly display:

- loading states
- API failures
- empty states
- validation errors

Example:

```text
Unable to load daily plan.
```

Avoid silent UI failure.

---

# 27. Logging Philosophy

Frontend logging should remain lightweight.

Useful logs:

- failed API calls
- UI rendering failures
- submission failures

Avoid excessive frontend telemetry in V1.

---

# 28. Schema Stability Rule

Frontend components should assume:

```text
API schemas are stable contracts.
```

The frontend MUST NOT:

- silently mutate API payloads
- invent undocumented fields
- reshape backend responses unpredictably

---

# 29. Allowed Dependencies

Allowed:

```text
React
Next.js
TypeScript
TailwindCSS
Zustand
Axios
```

---

# 30. Forbidden Dependencies

Avoid:

```text
heavy dashboard frameworks
complex microfrontend systems
large enterprise UI frameworks
```

unless explicitly requested later.

---

# 31. Testing Requirements

The frontend should be testable for:

- component rendering
- API integration
- state consistency
- form submission
- deterministic rendering
- explainability visibility

---

# 32. Anti-Drift Rules

The AI MUST NOT:

- embed backend business logic
- duplicate intelligence logic
- recreate scoring systems
- introduce hidden reasoning

The frontend should remain:

```text
Pure operational intelligence visualization infrastructure.
```

---

# 33. Example Frontend Workflow

```text
Select Territory
        ↓
Load Daily Plan
        ↓
Open Recommendation Detail
        ↓
View Alerts
        ↓
Read Explanation
        ↓
Submit Outcome
```

---

# 34. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Is the UI operationally clear? | Yes/No |
| Is explainability visible? | Yes/No |
| Is business logic absent from frontend? | Yes/No |
| Are API schemas preserved? | Yes/No |
| Is state management simple and predictable? | Yes/No |
| Is scope respected? | Yes/No |

---

# 35. Final One-Line Definition

```text
A lightweight explainability-focused operational dashboard
that visualizes agricultural field intelligence
through clear, workflow-oriented,
and backend-driven user interfaces.
```