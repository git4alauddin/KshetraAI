# KshetraAI — Demo Integration Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the final Demo Integration Layer.

The Demo Integration Layer is responsible for:

```text
Combining all KshetraAI components
into a coherent,
stable,
and presentation-ready prototype workflow.
```

This layer determines:

```text
How the final system experience is demonstrated.
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Demo Integration Layer |
| Layer | End-to-End System Integration Layer |
| Primary Responsibility | Prototype orchestration and demo workflow |
| Upstream Dependencies | All Backend + Frontend Components |
| Downstream Consumers | Judges, Demo Audience, Reviewers |
| Architecture Criticality | High |

---

# 3. Core Philosophy

The Demo Integration Layer should remain:

- stable
- deterministic
- presentation-oriented
- workflow-focused
- explainability-centric
- operationally coherent

The layer should NOT:

- redesign architecture
- introduce new business logic
- create hidden intelligence
- rewrite engine behavior
- introduce unstable experimentation

Its responsibility is ONLY:

```text
Integrate and demonstrate the system cleanly.
```

---

# 4. Responsibilities

The Demo Integration Layer IS responsible for:

- orchestrating end-to-end workflows
- validating full system integration
- preparing demo scenarios
- ensuring UI/API alignment
- ensuring workflow continuity
- validating explainability visibility
- ensuring stable demo execution

---

# 5. Non-Responsibilities

The Demo Integration Layer is NOT responsible for:

- redesigning engines
- modifying scoring logic
- creating new anomaly logic
- altering schemas
- inventing new business workflows

These belong to upstream modules.

---

# 6. Core Demo Philosophy

The demo should communicate:

```text
Signal
        ↓
Intelligence
        ↓
Action
        ↓
Learning
```

The demo is NOT about:

```text
Showing maximum technical complexity.
```

The demo IS about:

```text
Showing operational intelligence clearly.
```

---

# 7. Core Demo Narrative

The demo should tell this story:

---

## Before KshetraAI

```text
Field representatives followed static visit schedules
with limited contextual intelligence.
```

---

## After KshetraAI

```text
Field representatives receive adaptive,
explainable,
signal-driven operational guidance.
```

---

# 8. Primary Demo Workflow

The final workflow should remain:

```text
Rep Selects Territory
        ↓
Daily Plan Generated
        ↓
Priority Ranking Displayed
        ↓
Recommendation Selected
        ↓
Contextual Action Displayed
        ↓
Anomaly Alerts Displayed
        ↓
Explainability Displayed
        ↓
Outcome Submitted
        ↓
Learning Feedback Captured
```

---

# 9. Required Integrated Components

The final demo must integrate:

| Component | Required |
|---|---|
| Data Pipeline | Yes |
| Feature Builder | Yes |
| Priority Engine | Yes |
| Contextual Engine | Yes |
| Anomaly Engine | Yes |
| Explainability Engine | Yes |
| Outcome Learning Engine | Yes |
| API Layer | Yes |
| Frontend Dashboard | Yes |

---

# 10. Demo Scope Philosophy

The prototype should prioritize:

```text
Depth of intelligence quality
over breadth of features.
```

Better:

```text
5 strong explainable workflows
```

than:

```text
50 unstable features.
```

---

# 11. Recommended Demo Scenario

Suggested V1 scenario:

| Field | Value |
|---|---|
| Territory | Wardha |
| Crop | Cotton |
| Current Risk | Fungal disease risk |
| Inventory State | Low fungicide stock |
| Competitive Context | Competitor promotion active |

---

# 12. Expected Demo Outputs

The demo should clearly display:

- ranked visit plan
- urgency scoring
- anomaly alerts
- contextual recommendations
- operational reasoning
- confidence visibility
- feedback capture

---

# 13. Daily Plan Demonstration

The demo should show:

```text
Why ENT001 is ranked above ENT002.
```

NOT just:

```text
A random ranked list.
```

Priority explanation visibility is critical.

---

# 14. Recommendation Demonstration

The demo should show:

```text
Why a fungicide discussion is recommended.
```

The recommendation should visibly connect to:

- weather signals
- crop stage
- NDVI stress
- inventory conditions

---

# 15. Anomaly Demonstration

The demo should clearly show:

```text
What abnormal operational event was detected.
```

Example:

```text
Stock-Out Risk
Critical Severity
Inventory significantly below baseline
```

---

# 16. Explainability Demonstration

The explainability layer must remain:

```text
Highly visible.
```

The demo should clearly show:

- evidence
- reasoning
- contributing signals
- confidence levels

This is one of the strongest differentiators of the system.

---

# 17. Outcome Learning Demonstration

The demo should demonstrate:

```text
The system learns from field outcomes.
```

Example:

```text
Recommendation followed
        +
Order placed
→ positive feedback signal logged
```

---

# 18. Allowed File Ownership

The AI MAY modify:

```text
frontend/
backend/api/
demo/
```

ONLY for integration purposes.

---

# 19. Forbidden File Ownership

The AI MUST NOT:

- redesign engine internals
- alter intelligence architecture
- rewrite schemas
- modify contracts silently

unless explicitly instructed.

---

# 20. Recommended Demo Folder Structure

```text
demo/

├── scenarios/
├── scripts/
├── sample_outputs/
├── screenshots/
├── judging_flow/
└── presentation_notes/
```

---

# 21. Demo Scenario Requirements

Each scenario should contain:

| Element | Purpose |
|---|---|
| Territory | Context |
| Crop | Operational relevance |
| Risk/Opportunity | Intelligence trigger |
| Recommendation | Operational action |
| Alert | Anomaly visibility |
| Explanation | Explainability |
| Outcome | Learning demonstration |

---

# 22. Deterministic Demo Rule

The demo MUST remain:

```text
Fully deterministic.
```

Avoid:

- unstable live API dependencies
- uncontrolled randomness
- unpredictable outputs

The demo should behave consistently.

---

# 23. Explainability Preservation Rule

Explainability should remain visible in ALL workflows.

The audience should always understand:

```text
Why the system produced the output.
```

Avoid hidden reasoning.

---

# 24. Offline-Friendly Demonstration Rule

The demo should remain resilient even with:

```text
No internet connectivity.
```

Preferred:

- local synthetic data
- local APIs
- cached assets
- deterministic workflows

---

# 25. Demo Stability Rule

The demo should prioritize:

- stability
- reliability
- operational coherence

over:

- experimental features
- risky live integrations
- unstable dependencies

---

# 26. API Integration Rules

The demo should consume:

```text
Stable backend APIs only.
```

Avoid:

- direct engine access from frontend
- hidden frontend-side calculations
- duplicated business logic

---

# 27. Presentation Philosophy

The demo should communicate:

```text
Operational impact.
```

NOT just technical implementation.

The audience should clearly understand:

- why the system matters
- what operational problem it solves
- how intelligence improves decisions

---

# 28. Logging Requirements

The demo should log:

- successful workflow execution
- API failures
- outcome submissions
- integration failures

Avoid silent demo failure.

---

# 29. Allowed Dependencies

Allowed:

```text
React
FastAPI
SQLite
Pandas
TailwindCSS
```

---

# 30. Forbidden Dependencies

Avoid:

```text
unstable live integrations
experimental cloud dependencies
complex distributed systems
```

unless explicitly required later.

---

# 31. Testing Requirements

The integrated demo should be testable for:

- full workflow execution
- API connectivity
- deterministic outputs
- UI consistency
- explanation visibility
- outcome submission flow

---

# 32. Anti-Drift Rules

The AI MUST NOT:

- redesign architecture during integration
- create hidden business logic
- silently alter schemas
- merge engine responsibilities

The demo layer should remain:

```text
Pure orchestration and presentation integration.
```

---

# 33. Example End-to-End Flow

```text
Synthetic Dataset
        ↓
Feature Builder
        ↓
Priority Engine
        ↓
Contextual Engine
        ↓
Anomaly Engine
        ↓
Explainability Engine
        ↓
FastAPI Layer
        ↓
Frontend Dashboard
        ↓
Outcome Submission
        ↓
Outcome Learning
```

---

# 34. Final Demo Goal

The final system should demonstrate:

```text
How agricultural field-force operations
can become adaptive,
signal-driven,
explainable,
and continuously improving.
```

---

# 35. Review Checklist

Before accepting integration:

| Question | Check |
|---|---|
| Does the full workflow execute correctly? | Yes/No |
| Is explainability visible everywhere? | Yes/No |
| Are outputs deterministic? | Yes/No |
| Are APIs stable? | Yes/No |
| Is the demo operationally coherent? | Yes/No |
| Is scope respected? | Yes/No |

---

# 36. Final One-Line Definition

```text
A deterministic end-to-end orchestration layer
that integrates explainable agricultural intelligence
into a stable,
workflow-driven,
and presentation-ready operational prototype.
```