# KshetraAI — Contextual Decision Engine Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the Contextual Decision Engine.

The Contextual Decision Engine is responsible for:

```text
Generating contextual next best actions
for prioritized farmers, retailers, and distributors.
```

This engine determines:

```text
What the field representative should do,
discuss, recommend, or inspect during a visit.
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Contextual Decision Engine |
| Layer | Core Intelligence Layer |
| Primary Responsibility | Next Best Action generation |
| Upstream Dependencies | Feature Builder, Priority Engine |
| Downstream Consumers | Dashboard, APIs, Explainability Layer |
| Architecture Criticality | High |

---

# 3. Core Philosophy

The Contextual Decision Engine should remain:

- deterministic
- explainable
- rule-driven
- context-aware
- operationally grounded

The engine should NOT:

- generate final explanations
- perform anomaly escalation
- recalibrate learning weights
- redesign scoring logic
- perform black-box reasoning

Its responsibility is ONLY:

```text
Generate operational recommendations
from contextual signals.
```

---

# 4. Responsibilities

The Contextual Decision Engine IS responsible for:

- contextual risk inference
- opportunity inference
- next best action generation
- advisory recommendation generation
- product discussion recommendation
- operational follow-up suggestions
- action prioritization

---

# 5. Non-Responsibilities

The Contextual Decision Engine is NOT responsible for:

- priority ranking
- anomaly severity escalation
- explanation formatting
- frontend rendering
- API route handling
- learning recalibration
- score generation

These belong to other modules.

---

# 6. Core Decision Philosophy

The engine should use:

```text
Controlled explainable operational logic.
```

NOT:

```text
Unconstrained generative reasoning.
```

---

# 7. Primary Decision Categories

| Category | Purpose |
|---|---|
| Agronomic Actions | Crop/pest-related actions |
| Inventory Actions | Restocking-related actions |
| Sales Actions | Revenue opportunity actions |
| Relationship Actions | Engagement/follow-up actions |
| Competitive Actions | Defensive market actions |

---

# 8. Expected Inputs

Inputs originate from:

- priority_feature_view
- priority engine outputs
- contextual feature tables

---

# Example Input

```json
{
  "entity_id": "ENT001",
  "priority_score": 83.7,

  "weather_risk_score": 85,
  "pest_disease_risk_score": 90,
  "crop_stage_risk_score": 80,

  "inventory_need_score": 88,
  "sales_opportunity_score": 84,

  "relationship_need_score": 64,
  "competitive_pressure_score": 72
}
```

---

# 9. Expected Outputs

The engine outputs:

- next best action
- contextual recommendation
- inferred operational risk/opportunity
- suggested product category
- advisory actions
- action confidence level

---

# Example Output

```json
{
  "entity_id": "ENT001",

  "risk_or_opportunity": "Possible fungal disease risk",

  "recommended_actions": [
    "Inspect cotton crop symptoms",
    "Discuss fungicide advisory",
    "Recommend fungicide restocking"
  ],

  "recommended_product_category": "Fungicide",

  "confidence_level": "High"
}
```

---

# 10. Decision Generation Philosophy

The engine should operate using:

```text
Signals
        ↓
Contextual inference
        ↓
Operational recommendation
```

NOT direct unsupported conclusions.

---

# 11. Important Safety Rule

The engine MUST infer:

```text
Possible risk/opportunity.
```

NOT:

```text
Confirmed diagnosis.
```

Correct:

```text
Possible fungal disease risk.
```

Incorrect:

```text
Crop is infected with fungus.
```

---

# 12. Agronomic Action Logic

# Purpose

Generate crop/pest/weather-related recommendations.

---

# Example Inputs

- high humidity
- high rainfall
- NDVI stress
- vulnerable crop stage

---

# Example Output

```text
Inspect crop symptoms
Discuss fungicide advisory
```

---

# 13. Inventory Action Logic

# Purpose

Generate restocking and inventory recommendations.

---

# Example Inputs

- low inventory
- high sales velocity
- stockout risk

---

# Example Output

```text
Recommend inventory replenishment
```

---

# 14. Sales Opportunity Logic

# Purpose

Generate commercial opportunity actions.

---

# Example Inputs

- seasonal relevance
- strong purchase history
- high demand signals

---

# Example Output

```text
Discuss insecticide promotion
```

---

# 15. Relationship Action Logic

# Purpose

Generate engagement and follow-up actions.

---

# Example Inputs

- long visit gap
- pending issue
- strategic account importance

---

# Example Output

```text
Conduct relationship follow-up visit
```

---

# 16. Competitive Action Logic

# Purpose

Generate market-defense actions.

---

# Example Inputs

- competitor campaign active
- regional sales drop
- competitive pressure high

---

# Example Output

```text
Deploy defensive retailer engagement
```

---

# 17. Rule-Based Architecture

The engine should initially rely on:

```text
controlled rule templates
```

Recommended storage:

```text
backend/rules/
```

---

# Example Rule

```yaml
rule_id: COTTON_FUNGAL_RISK_01

conditions:
  humidity: high
  rainfall: high
  crop_stage: flowering
  ndvi_stress: moderate_or_high

actions:
  - inspect_crop
  - discuss_fungicide
```

---

# 18. Allowed File Ownership

The AI MAY modify:

```text
backend/engines/contextual_decision_engine.py
backend/engines/recommendation_engine.py
backend/rules/
backend/config/decision_thresholds.yaml
```

---

# 19. Forbidden File Ownership

The AI MUST NOT modify:

```text
backend/explainability/
backend/anomaly/
frontend/
contracts/
architecture_docs/
```

unless explicitly instructed.

---

# 20. Recommended Folder Structure

```text
backend/engines/

├── contextual_decision_engine.py
├── recommendation_engine.py
├── advisory_engine.py
└── action_selector.py
```

---

# Rules Folder

```text
backend/rules/

├── agronomic_rules.yaml
├── inventory_rules.yaml
├── sales_rules.yaml
├── relationship_rules.yaml
└── competitor_rules.yaml
```

---

# 21. Deterministic Decision Rule

The engine MUST remain:

```text
Fully deterministic.
```

Given identical inputs:

```text
recommendation outputs must remain identical.
```

Avoid:

- random recommendation generation
- non-configurable dynamic behavior
- uncontrolled generative responses

---

# 22. Explainability Preservation Rule

Recommendations MUST remain traceable.

Every recommendation should preserve:

- triggering signals
- matched rules
- contextual evidence
- operational reasoning

Avoid:

```text
opaque recommendation generation
```

---

# 23. Confidence Assignment Rule

Confidence should remain:

- interpretable
- rule-driven
- explainable

Suggested confidence categories:

| Level | Meaning |
|---|---|
| High | Strong aligned evidence |
| Medium | Partial evidence |
| Low | Weak/incomplete evidence |

---

# 24. Product Recommendation Rule

The engine may recommend:

```text
Product categories
```

NOT:

```text
unsupported brand claims
```

Preferred:

```text
Fungicide
Insecticide
Herbicide
```

Avoid unsupported medical/agronomic certainty.

---

# 25. Logging Requirements

The engine should log:

- matched rules
- generated actions
- inferred risks/opportunities
- confidence assignments

Example:

```text
INFO:
Triggered COTTON_FUNGAL_RISK_01 for ENT001
```

---

# 26. Error Handling Rules

Preferred:

```text
Explicit operational warnings.
```

Example:

```text
WARNING:
No matching contextual rule for ENT007
```

Avoid silent fallback behavior.

---

# 27. Schema Stability Rule

The engine MUST preserve:

- output structure
- action naming conventions
- confidence categories

The AI MUST NOT:

- silently alter schemas
- rename operational outputs
- invent undocumented output fields

---

# 28. API Independence Rule

The engine should remain:

```text
Pure operational intelligence logic.
```

The engine MUST NOT contain:

- HTTP logic
- frontend rendering
- UI formatting
- API routing

---

# 29. Allowed Dependencies

Allowed:

```text
pandas
numpy
yaml
typing
dataclasses
```

---

# 30. Forbidden Dependencies

Avoid:

```text
LLM-based uncontrolled reasoning
heavy ML frameworks
distributed orchestration
```

unless explicitly requested later.

---

# 31. Testing Requirements

The engine should be testable for:

- rule matching
- deterministic recommendations
- confidence assignment
- action generation
- schema consistency
- operational safety

---

# 32. Anti-Drift Rules

The AI MUST NOT:

- generate explanations
- redesign scoring
- trigger anomaly escalation
- recalibrate weights
- merge responsibilities across modules

The engine should remain:

```text
Pure contextual recommendation intelligence.
```

---

# 33. Example Processing Flow

```text
Feature Scores
        ↓
Contextual Rule Matching
        ↓
Risk / Opportunity Inference
        ↓
Recommended Actions
        ↓
Confidence Assignment
        ↓
Structured Recommendation Output
```

---

# 34. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Are outputs deterministic? | Yes/No |
| Are recommendations explainable? | Yes/No |
| Are rules traceable? | Yes/No |
| Are confidence levels interpretable? | Yes/No |
| Is operational safety preserved? | Yes/No |
| Is scope respected? | Yes/No |

---

# 35. Final One-Line Definition

```text
A deterministic explainable contextual intelligence engine
that converts operational agricultural signals
into actionable next best recommendations
for field-force decision-making.
```