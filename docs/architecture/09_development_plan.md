# KshetraAI — Implementation Roadmap & Development Plan (V1)

---

# 1. Objective

The purpose of this document is to define:

```text
How the KshetraAI prototype will be built
step-by-step in a structured engineering workflow.
```

This roadmap transforms the conceptual architecture into an executable implementation plan.

The roadmap focuses on:

- Controlled development sequencing
- Dependency-aware implementation
- Modular engineering
- Practical prototype delivery
- Explainable intelligence implementation

---

# 2. Core Development Philosophy

The prototype should be built:

- Incrementally
- Modularly
- Deterministically
- Explainably
- Demo-first
- Intelligence-first

The implementation should prioritize:

```text
Operational intelligence quality
over flashy UI complexity.
```

---

# 3. Engineering Strategy

The implementation will follow:

```text
Data → Features → Intelligence → APIs → UI → Feedback
```

This order is important because:

- Intelligence depends on features
- Features depend on data
- APIs depend on engines
- UI depends on APIs
- Learning depends on outcomes

---

# 4. High-Level Build Phases

| Phase | Goal |
|---|---|
| Phase 1 | Dataset & schema setup |
| Phase 2 | Feature generation pipeline |
| Phase 3 | Dynamic prioritization engine |
| Phase 4 | Contextual decision engine |
| Phase 5 | Anomaly detection engine |
| Phase 6 | Explainability engine |
| Phase 7 | Outcome logging & learning |
| Phase 8 | FastAPI backend integration |
| Phase 9 | Frontend dashboard/app |
| Phase 10 | Demo workflow & final polish |

---

# 5. Recommended Project Structure

```text
kshetraai/

├── backend/
│   ├── api/
│   ├── engines/
│   ├── rules/
│   ├── features/
│   ├── anomaly/
│   ├── explainability/
│   ├── learning/
│   ├── data/
│   ├── models/
│   ├── utils/
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   ├── state/
│   └── styles/
│
├── datasets/
│   ├── raw/
│   ├── processed/
│   └── synthetic/
│
├── docs/
│   ├── architecture/
│   ├── diagrams/
│   ├── scoring/
│   └── implementation/
│
├── notebooks/
│
├── scripts/
│
├── tests/
│
└── README.md
```

---

# 6. Phase 1 — Dataset & Schema Setup

# Goal

Create the foundational dataset required for the prototype.

---

# Tasks

## 1. Define schema tables

Implement:

- representatives
- territories
- visit_entities
- crop_context
- weather_signals
- pest_signals
- ndvi_signals
- sales_signals
- inventory_signals
- competitor_signals
- visit_history
- recommendation_log
- outcome_log

---

## 2. Create synthetic data

Generate:

- realistic retailers/farmers
- crop-stage combinations
- weather conditions
- inventory conditions
- sales patterns
- competitor scenarios

---

## 3. Validate logical consistency

Example:

```text
High humidity + rainfall + cotton flowering
→ higher fungal risk probability
```

---

# Deliverables

- CSV/SQLite/PostgreSQL dataset
- Synthetic data generator scripts
- Initial feature-ready dataset

---

# 7. Phase 2 — Feature Generation Pipeline

# Goal

Convert raw data into normalized intelligence signals.

---

# Responsibilities

Generate:

- weather risk score
- pest risk score
- NDVI stress score
- sales opportunity score
- inventory need score
- relationship need score
- competitive pressure score
- travel cost score

---

# Example

## Raw

```text
Humidity = 87%
Rainfall = 112 mm
```

## Feature

```text
weather_risk_score = 85
```

---

# Suggested Modules

```text
features/
├── agronomic_features.py
├── sales_features.py
├── inventory_features.py
├── relationship_features.py
├── competitor_features.py
└── travel_features.py
```

---

# Deliverables

- Feature generation scripts
- priority_feature_view table
- normalized score generation

---

# 8. Phase 3 — Dynamic Prioritization Engine

# Goal

Rank entities based on weighted multi-signal scoring.

---

# Responsibilities

Calculate:

```text
Final Priority Score
```

using:

```text
Component scores
+
Signal weights
```

---

# Inputs

- agronomic signals
- sales signals
- inventory signals
- relationship signals
- competitor signals
- travel signals

---

# Outputs

- priority score
- priority level
- ranked visit list

---

# Suggested Modules

```text
engines/
├── priority_engine.py
├── scoring_engine.py
└── ranking_engine.py
```

---

# Deliverables

- Working priority engine
- Ranked recommendation output
- Priority classification logic

---

# 9. Phase 4 — Contextual Decision Engine

# Goal

Generate:

```text
Next Best Action
```

for each prioritized entity.

---

# Responsibilities

Infer:

- risk/opportunity context
- product discussion
- advisory suggestions
- operational actions

---

# Implementation Strategy

Use:

```text
controlled rule-based templates
```

instead of unconstrained LLM logic.

---

# Suggested Modules

```text
engines/
├── contextual_decision_engine.py
└── recommendation_engine.py

rules/
├── agronomic_rules.yaml
├── inventory_rules.yaml
├── sales_rules.yaml
└── competitor_rules.yaml
```

---

# Deliverables

- Rule engine
- Structured recommendations
- Risk inference logic

---

# 10. Phase 5 — Anomaly Detection Engine

# Goal

Detect unusual or emerging events.

---

# Responsibilities

Detect:

- demand spikes
- stock-out risks
- crop stress changes
- competitor pressure
- coverage gaps

---

# Detection Methods

- threshold-based detection
- baseline comparison
- deviation scoring
- trend analysis

---

# Suggested Modules

```text
anomaly/
├── anomaly_engine.py
├── baseline_engine.py
├── threshold_rules.py
└── alert_generator.py
```

---

# Deliverables

- Working anomaly alerts
- Severity classification
- Alert escalation logic

---

# 11. Phase 6 — Explainability Engine

# Goal

Generate transparent operational reasoning.

---

# Responsibilities

Explain:

- why an entity is prioritized
- why a recommendation exists
- why an anomaly was triggered
- confidence levels

---

# Outputs

- evidence mapping
- signal attribution
- human-readable explanations

---

# Suggested Modules

```text
explainability/
├── explanation_engine.py
├── confidence_engine.py
├── evidence_mapper.py
└── template_generator.py
```

---

# Deliverables

- Structured explanation system
- Human-readable recommendation text
- Confidence assignment

---

# 12. Phase 7 — Outcome Logging & Learning

# Goal

Capture outcomes and create adaptive learning foundation.

---

# Responsibilities

Track:

- recommendation acceptance
- sales outcomes
- order placement
- rep feedback
- alert validation

---

# Initial Learning Strategy

Start with:

```text
basic logging + analytics
```

not full ML retraining.

---

# Suggested Modules

```text
learning/
├── outcome_logger.py
├── feedback_processor.py
├── recalibration_engine.py
└── analytics.py
```

---

# Deliverables

- Outcome logging pipeline
- Feedback storage
- Basic recalibration logic

---

# 13. Phase 8 — FastAPI Backend

# Goal

Expose all intelligence modules through APIs.

---

# Suggested APIs

| Endpoint | Purpose |
|---|---|
| /get-daily-plan | Ranked visits |
| /get-recommendation | Next best action |
| /get-alerts | Active anomalies |
| /submit-outcome | Feedback capture |
| /get-explanation | Explainability data |

---

# Suggested Structure

```text
api/
├── routes/
├── schemas/
├── services/
└── dependencies/
```

---

# Deliverables

- Working backend APIs
- JSON response structure
- API orchestration

---

# 14. Phase 9 — Frontend Dashboard/App

# Goal

Create a clean operational interface.

---

# Core Screens

| Screen | Purpose |
|---|---|
| Territory Selection | Start workflow |
| Daily Plan | Ranked entities |
| Recommendation Detail | Full explanation |
| Alert Panel | Anomaly alerts |
| Outcome Form | Feedback capture |

---

# UI Philosophy

The UI should prioritize:

- operational clarity
- explainability
- workflow simplicity

not visual overload.

---

# Suggested Stack

```text
React / Next.js
Tailwind
```

---

# Deliverables

- Working frontend
- API integration
- End-to-end workflow

---

# 15. Phase 10 — Demo Workflow & Final Polish

# Goal

Convert the system into a strong presentation/demo experience.

---

# Demo Focus

Show:

```text
Signal → Intelligence → Action → Learning
```

---

# Required Demo Capabilities

- Territory selection
- Ranked visit generation
- Recommendation explanation
- Alert generation
- Outcome submission
- Feedback learning loop

---

# Demo Story

```text
Before:
Static field planning

After:
Adaptive explainable AI-driven field intelligence
```

---

# 16. MVP vs Future Architecture

# MVP (Must Work)

| Capability | Status |
|---|---|
| Priority scoring | Required |
| Next best action | Required |
| Basic anomaly alerts | Required |
| Explainability | Required |
| Outcome logging | Required |

---

# Future Extensions

| Capability | Future Scope |
|---|---|
| Real-time APIs | Future |
| ML retraining | Future |
| Satellite pipeline | Future |
| Reinforcement learning | Future |
| Full offline sync | Future |
| Route optimization | Future |

---

# 17. Suggested Development Order

The implementation MUST follow this sequence:

```text
Dataset
    ↓
Feature Pipeline
    ↓
Priority Engine
    ↓
Decision Engine
    ↓
Anomaly Engine
    ↓
Explainability
    ↓
Outcome Logging
    ↓
FastAPI
    ↓
Frontend
    ↓
Demo Workflow
```

---

# 18. Important Engineering Principles

The implementation should remain:

- deterministic
- explainable
- modular
- testable
- extensible
- operationally realistic

---

# 19. Suggested Team Work Split

| Area | Responsibility |
|---|---|
| Data & Features | Dataset + feature generation |
| Intelligence Engines | Priority + contextual logic |
| Backend | APIs + orchestration |
| Frontend | Dashboard + workflow |
| Demo & Docs | Storytelling + presentation |

---

# 20. Final Engineering Goal

The prototype should demonstrate:

```text
How agricultural field-force planning can evolve
from static routing into explainable adaptive intelligence.
```

---

# 21. Final One-Line Definition

```text
A structured engineering roadmap
for building an explainable AI-driven
agricultural field intelligence prototype
through modular, phased implementation.
```