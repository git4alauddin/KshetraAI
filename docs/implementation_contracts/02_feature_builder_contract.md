# KshetraAI — Feature Builder Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the Feature Builder layer.

The Feature Builder is responsible for:

```text
Converting cleaned operational signals
into normalized intelligence-ready feature scores.
```

This layer acts as the bridge between:

```text
Raw operational data
        ↓
Intelligence engines
```

The feature layer is one of the most critical parts of the system because:

```text
Bad features → bad intelligence.
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Feature Builder |
| Layer | Feature Engineering Layer |
| Primary Responsibility | Generate normalized intelligence signals |
| Downstream Consumers | Priority Engine, Contextual Engine, Anomaly Engine |
| Architecture Dependency Level | Core Foundational |

---

# 3. Core Philosophy

The Feature Builder should:

- remain deterministic
- remain explainable
- remain transparent
- produce interpretable scores
- preserve operational meaning

The feature layer should NOT:

- perform final prioritization
- generate recommendations
- detect anomalies
- generate explanations
- recalibrate learning weights

---

# 4. Responsibilities

The Feature Builder IS responsible for:

- converting raw fields into normalized scores
- aggregating operational context
- generating domain-specific features
- preparing engine-consumable signals
- standardizing scoring ranges
- building feature-ready entity views

---

# 5. Non-Responsibilities

The Feature Builder is NOT responsible for:

- ranking entities
- next best action generation
- anomaly escalation
- recommendation confidence
- explanation generation
- API formatting
- frontend logic

These belong to downstream modules.

---

# 6. Core Feature Categories

The Feature Builder generates the following major feature groups:

| Feature Group | Purpose |
|---|---|
| Agronomic Features | Crop/pest/weather urgency |
| Sales Features | Commercial opportunity |
| Inventory Features | Stock urgency |
| Relationship Features | Rep engagement need |
| Competitive Features | Market pressure |
| Travel Features | Route feasibility |

---

# 7. Expected Inputs

Inputs originate from:

- cleaned pipeline outputs
- validated operational tables
- normalized contextual data

---

# Example Input

```json
{
  "humidity_percent": 87,
  "rainfall_7d_mm": 112,
  "crop_stage": "flowering",
  "current_stock_units": 12,
  "sales_last_30d": 48
}
```

---

# 8. Expected Outputs

The Feature Builder outputs:

```text
Normalized feature scores (0–100)
```

Example:

```json
{
  "weather_risk_score": 85,
  "crop_stage_risk_score": 80,
  "inventory_need_score": 88
}
```

---

# 9. Output Philosophy

Feature outputs should be:

- interpretable
- explainable
- bounded
- normalized
- operationally meaningful

Preferred range:

```text
0–100
```

---

# 10. Allowed File Ownership

The AI MAY modify:

```text
backend/features/
backend/utils/feature_utils.py
backend/config/feature_thresholds.yaml
```

---

# 11. Forbidden File Ownership

The AI MUST NOT modify:

```text
backend/engines/
backend/explainability/
backend/anomaly/
frontend/
contracts/
architecture_docs/
```

unless explicitly instructed.

---

# 12. Recommended Folder Structure

```text
backend/features/

├── agronomic_features.py
├── sales_features.py
├── inventory_features.py
├── relationship_features.py
├── competitor_features.py
├── travel_features.py
├── feature_registry.py
└── feature_pipeline.py
```

---

# 13. Agronomic Features

# Purpose

Represent crop-health and agronomic urgency.

---

# Example Features

| Feature | Purpose |
|---|---|
| weather_risk_score | Weather-driven urgency |
| pest_disease_risk_score | Pest/disease pressure |
| crop_stage_risk_score | Vulnerability stage |
| ndvi_stress_score | Crop stress severity |

---

# Example Logic

```text
High rainfall
+
High humidity
+
Cotton flowering stage
→ higher agronomic risk
```

---

# 14. Sales Features

# Purpose

Represent commercial opportunity.

---

# Example Features

| Feature | Purpose |
|---|---|
| historical_sales_score | Commercial importance |
| seasonal_product_relevance | Timing relevance |
| purchase_history_score | Purchase likelihood |
| sales_opportunity_score | Revenue potential |

---

# Example Logic

```text
High historical fungicide sales
+
Peak crop season
→ higher sales opportunity
```

---

# 15. Inventory Features

# Purpose

Represent stock urgency and replenishment need.

---

# Example Features

| Feature | Purpose |
|---|---|
| stock_level_score | Low stock urgency |
| sales_velocity_score | Stock movement speed |
| stockout_risk_score | Stock depletion probability |
| inventory_need_score | Restocking urgency |

---

# Example Logic

```text
Low inventory
+
High sales velocity
→ higher stock-out risk
```

---

# 16. Relationship Features

# Purpose

Represent engagement and relationship management need.

---

# Example Features

| Feature | Purpose |
|---|---|
| relationship_gap_score | Visit gap urgency |
| pending_issue_score | Follow-up importance |
| engagement_priority_score | Strategic relationship value |

---

# Example Logic

```text
Long visit gap
+
Pending issue
→ higher relationship need
```

---

# 17. Competitive Features

# Purpose

Represent market pressure.

---

# Example Features

| Feature | Purpose |
|---|---|
| competitor_pressure_score | Market threat |
| competitor_promotion_score | Competitive activity |
| regional_sales_drop_score | Defensive urgency |

---

# Example Logic

```text
Competitor promotion active
+
Regional sales declining
→ higher competitive pressure
```

---

# 18. Travel Features

# Purpose

Represent route practicality.

---

# Example Features

| Feature | Purpose |
|---|---|
| travel_cost_score | Travel penalty |
| route_efficiency_score | Cluster practicality |
| distance_penalty_score | Distance burden |

---

# Example Logic

```text
Far distance
+
Poor clustering
→ higher travel penalty
```

---

# 19. Feature Normalization Rules

All features should remain:

```text
normalized between 0–100
```

Preferred interpretation:

| Score Range | Meaning |
|---|---|
| 0–30 | Low |
| 31–60 | Moderate |
| 61–80 | High |
| 81–100 | Critical |

---

# 20. Deterministic Processing Rule

Feature generation MUST remain deterministic.

Given identical inputs:

```text
feature outputs must remain identical.
```

Avoid:

- randomness
- hidden state
- dynamic thresholds without configuration

---

# 21. Explainability Preservation Rule

Features must preserve:

```text
clear operational meaning.
```

Good:

```text
weather_risk_score = 85
```

Bad:

```text
feature_x = 0.82
```

All feature names should remain interpretable.

---

# 22. Feature Calculation Philosophy

The system should initially prioritize:

```text
simple explainable heuristics
```

instead of:

```text
opaque learned embeddings
```

Reason:

- easier debugging
- easier explainability
- safer demos
- operational clarity

---

# 23. Configuration Rules

Thresholds and weights should preferably remain configurable.

Recommended:

```text
backend/config/feature_thresholds.yaml
```

Avoid:

```text
hardcoded scattered constants
```

---

# 24. Logging Requirements

The Feature Builder should log:

- generated feature counts
- invalid feature rows
- normalization warnings
- missing source signals

Example:

```text
WARNING:
Missing NDVI signal for ENT009
```

---

# 25. Error Handling Rules

Preferred:

```text
Explicit operational warnings.
```

Avoid:

```text
silent feature failure
```

Example:

```text
ERROR:
Invalid humidity value > 100%
```

---

# 26. Schema Stability Rule

The Feature Builder MUST preserve:

- feature naming conventions
- score ranges
- entity relationships

The AI MUST NOT:

- rename established features
- alter score meanings
- create undocumented features

---

# 27. Output Integration View

Main expected output:

```text
priority_feature_view
```

This table/view feeds:

- priority engine
- contextual engine
- anomaly engine

---

# 28. Example Output Row

```json
{
  "entity_id": "ENT001",

  "weather_risk_score": 85,
  "pest_disease_risk_score": 90,
  "crop_stage_risk_score": 80,
  "ndvi_stress_score": 70,

  "sales_opportunity_score": 84,
  "inventory_need_score": 88,

  "relationship_need_score": 64,
  "competitive_pressure_score": 72,

  "travel_cost_score": 42
}
```

---

# 29. Allowed Dependencies

Allowed:

```text
pandas
numpy
typing
yaml
pathlib
```

---

# 30. Forbidden Dependencies

Avoid:

```text
heavy ML frameworks
distributed compute frameworks
black-box feature generation
```

unless explicitly requested later.

---

# 31. Testing Requirements

The Feature Builder should be testable for:

- score range validity
- deterministic outputs
- threshold behavior
- missing value handling
- feature consistency

---

# 32. Anti-Drift Rules

The AI MUST NOT:

- introduce recommendation logic
- generate priority rankings
- trigger anomalies
- create explanations
- merge intelligence responsibilities

The Feature Builder should remain:

```text
Pure feature engineering infrastructure.
```

---

# 33. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Are feature scores interpretable? | Yes/No |
| Are outputs normalized? | Yes/No |
| Is processing deterministic? | Yes/No |
| Are feature names meaningful? | Yes/No |
| Are no intelligence rules added? | Yes/No |
| Is scope respected? | Yes/No |

---

# 34. Final One-Line Definition

```text
A deterministic explainable feature-engineering layer
that converts agricultural, commercial,
inventory, relationship, competitive,
and travel signals into normalized intelligence-ready scores.
```