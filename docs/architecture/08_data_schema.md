# KshetraAI — Data Schema & Synthetic Dataset Design (V1)

---

# 1. Objective

The purpose of this document is to define the minimum data structure required to build the KshetraAI prototype.

The dataset should support:

- Dynamic prioritization
- Contextual next best action
- Anomaly detection
- Explainability
- Outcome feedback learning

The goal is not to model every real-world agricultural detail.

The goal is to create a practical, realistic, and implementable dataset that can power the demo.

---

# 2. Data Design Philosophy

The data should be:

- Simple enough to build quickly
- Rich enough to demonstrate intelligence
- Explainable through clear fields
- Compatible with scoring logic
- Easy to extend later
- Close to the problem statement signals

Each field should answer:

```text
Does this help prioritize, recommend, detect, explain, or learn?
```

If not, it should not be included in V1.

---

# 3. Core Entities

The prototype will use the following main entities:

| Entity | Purpose |
|---|---|
| Rep | Field representative |
| Territory | Area assigned to rep |
| Farmer/Retailer | Visit target |
| Crop Context | Crop and growth-stage information |
| Weather Signal | Local weather risk |
| Pest Signal | Pest/disease alert context |
| NDVI Signal | Crop stress indicator |
| Sales Signal | Historical and current sales pattern |
| Inventory Signal | Stock availability and depletion risk |
| Competitor Signal | Competitive pressure |
| Visit History | Past rep visits |
| Recommendation Log | Generated recommendations |
| Outcome Log | Field result after visit |

---

# 4. Table 1 — Representatives

## Purpose

Stores field representative details.

## Table Name

```text
representatives
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| rep_id | string | REP001 | Unique rep ID |
| rep_name | string | Amit Sharma | Rep name |
| territory_id | string | TERR_WARDHA_01 | Assigned territory |
| base_location | string | Wardha Town | Starting location |
| experience_level | string | medium | Optional rep context |

---

# 5. Table 2 — Territories

## Purpose

Stores region-level context.

## Table Name

```text
territories
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| territory_id | string | TERR_WARDHA_01 | Unique territory ID |
| district | string | Wardha | District |
| state | string | Maharashtra | State |
| dominant_crop | string | Cotton | Main crop |
| season | string | Kharif | Current season |
| total_entities | integer | 20 | Number of mapped accounts |

---

# 6. Table 3 — Visit Entities

## Purpose

Stores farmers, retailers, and distributors that can be visited.

## Table Name

```text
visit_entities
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Unique entity ID |
| entity_name | string | Ramesh Agro Center | Farmer/retailer name |
| entity_type | string | retailer | farmer / retailer / distributor |
| territory_id | string | TERR_WARDHA_01 | Territory mapping |
| village_or_area | string | Seloo | Local area |
| latitude | float | 20.7391 | Routing |
| longitude | float | 78.6022 | Routing |
| primary_crop | string | Cotton | Crop relevance |
| account_importance | integer | 85 | Strategic importance score |
| preferred_language | string | Marathi | Communication language |

---

# 7. Table 4 — Crop Context

## Purpose

Stores crop-stage and seasonal context for each entity or region.

## Table Name

```text
crop_context
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| crop | string | Cotton | Crop |
| crop_stage | string | Flowering | Current crop stage |
| crop_stage_risk_score | integer | 80 | Vulnerability score |
| crop_acreage_nearby | float | 150.5 | Commercial opportunity |
| seasonal_product_relevance | integer | 88 | Product timing relevance |

---

# 8. Table 5 — Weather Signals

## Purpose

Stores weather-related risk signals.

## Table Name

```text
weather_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| date | date | 2026-05-15 | Signal date |
| rainfall_7d_mm | float | 112.0 | Recent rainfall |
| rainfall_deviation_score | integer | 82 | Deviation from normal |
| humidity_percent | float | 87.0 | Disease risk indicator |
| temperature_c | float | 29.5 | Crop/pest condition |
| weather_risk_score | integer | 85 | Normalized weather risk |

---

# 9. Table 6 — Pest & Disease Signals

## Purpose

Stores public or simulated pest/disease alert signals.

## Table Name

```text
pest_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| date | date | 2026-05-15 | Alert date |
| pest_alert_active | boolean | true | Whether alert exists |
| pest_or_disease_type | string | Bollworm | Risk type |
| alert_severity | string | high | low / medium / high |
| pest_disease_risk_score | integer | 90 | Normalized risk score |
| source_type | string | govt_bulletin | Source reference |

---

# 10. Table 7 — NDVI / Crop Stress Signals

## Purpose

Stores satellite-derived or simulated crop stress indicators.

## Table Name

```text
ndvi_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| date | date | 2026-05-15 | Signal date |
| ndvi_current | float | 0.48 | Current NDVI |
| ndvi_baseline | float | 0.62 | Expected NDVI |
| ndvi_drop_percent | float | 22.5 | Stress indicator |
| ndvi_stress_level | string | moderate | low / moderate / high |
| ndvi_stress_score | integer | 70 | Normalized stress score |

---

# 11. Table 8 — Sales Signals

## Purpose

Stores sales and commercial opportunity indicators.

## Table Name

```text
sales_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| product_category | string | Fungicide | Product class |
| historical_sales_score | integer | 82 | Past performance |
| sales_last_30d | integer | 48 | Recent sales |
| sales_baseline_30d | integer | 28 | Normal sales baseline |
| sales_growth_percent | float | 71.4 | Demand spike detection |
| purchase_history_score | integer | 76 | Buying likelihood |
| sales_opportunity_score | integer | 84 | Normalized sales opportunity |

---

# 12. Table 9 — Inventory Signals

## Purpose

Stores retailer inventory and stock-out risk context.

## Table Name

```text
inventory_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| product_category | string | Fungicide | Product class |
| current_stock_units | integer | 12 | Available stock |
| normal_stock_units | integer | 50 | Expected stock |
| stock_level_score | integer | 85 | Low stock urgency score |
| sales_velocity_score | integer | 88 | Rate of stock movement |
| stockout_risk_score | integer | 91 | Stock-out risk |
| inventory_need_score | integer | 88 | Normalized inventory need |

---

# 13. Table 10 — Competitor Signals

## Purpose

Stores market pressure signals.

## Table Name

```text
competitor_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| competitor_promotion_active | boolean | true | Whether competitor push exists |
| competitor_discount_level | string | medium | low / medium / high |
| competitor_availability_score | integer | 75 | Competitor product availability |
| regional_sales_drop_score | integer | 68 | Our sales decline signal |
| competitive_pressure_score | integer | 72 | Normalized competitive pressure |

---

# 14. Table 11 — Visit History

## Purpose

Stores past visit and relationship context.

## Table Name

```text
visit_history
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| rep_id | string | REP001 | Field rep |
| last_visit_date | date | 2026-04-25 | Previous visit |
| days_since_last_visit | integer | 20 | Relationship gap |
| last_visit_outcome | string | order_placed | Last outcome |
| pending_issue_active | boolean | true | Follow-up need |
| relationship_need_score | integer | 64 | Normalized relationship score |

---

# 15. Table 12 — Travel / Route Signals

## Purpose

Stores basic travel feasibility fields.

## Table Name

```text
travel_signals
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| entity_id | string | ENT001 | Linked visit entity |
| rep_id | string | REP001 | Assigned rep |
| distance_km | float | 18.5 | Travel distance |
| estimated_route_time_min | integer | 42 | Travel time |
| nearby_cluster_count | integer | 4 | Visit clustering |
| route_efficiency_score | integer | 65 | Route practicality |
| travel_cost_score | integer | 42 | Travel penalty score |

---

# 16. Table 13 — Recommendation Log

## Purpose

Stores generated recommendations.

## Table Name

```text
recommendation_log
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| recommendation_id | string | REC001 | Unique recommendation |
| entity_id | string | ENT001 | Visit entity |
| rep_id | string | REP001 | Field rep |
| date | date | 2026-05-15 | Recommendation date |
| priority_score | float | 83.7 | Final priority score |
| priority_level | string | Critical | Critical / High / Medium / Low |
| recommended_action | string | Discuss fungicide restocking | Next best action |
| risk_or_opportunity | string | Fungal disease risk | Main context |
| confidence_level | string | High | Confidence |
| explanation | text | Reasoning text | Explainability output |

---

# 17. Table 14 — Outcome Log

## Purpose

Stores visit results and feedback.

## Table Name

```text
outcome_log
```

## Columns

| Column | Type | Example | Purpose |
|---|---|---|---|
| outcome_id | string | OUT001 | Unique outcome |
| recommendation_id | string | REC001 | Linked recommendation |
| visit_completed | boolean | true | Whether visit happened |
| recommendation_followed | boolean | true | Rep acceptance |
| sale_made | boolean | true | Commercial outcome |
| order_placed | boolean | true | Strong positive signal |
| order_value | float | 18500.0 | Revenue |
| rep_feedback | string | Useful recommendation | Explicit feedback |
| alert_validated | boolean | true | Alert correctness |

---

# 18. Minimum Prototype Dataset Size

For a strong demo, use:

| Data Item | Suggested Count |
|---|---|
| Territories | 2–3 |
| Reps | 3–5 |
| Retailers/Farmers | 20–50 |
| Crops | 3–4 |
| Product Categories | 3–5 |
| Historical Records | 30–90 days |
| Recommendations | Generated dynamically |
| Outcomes | 20–50 sample outcomes |

---

# 19. Suggested Crops for Prototype

Use a small realistic crop set:

```text
Cotton
Paddy
Soybean
Wheat
```

---

# 20. Suggested Product Categories

Use broad categories instead of specific brand claims:

```text
Insecticide
Fungicide
Herbicide
Seed Treatment
Nutrient Support
```

---

# 21. Score Fields Required for Engines

The prototype should generate or store the following normalized scores:

| Score | Range | Used By |
|---|---|---|
| pest_disease_risk_score | 0–100 | Agronomic Urgency |
| crop_stage_risk_score | 0–100 | Agronomic Urgency |
| weather_risk_score | 0–100 | Agronomic Urgency |
| ndvi_stress_score | 0–100 | Agronomic Urgency |
| historical_sales_score | 0–100 | Sales Opportunity |
| seasonal_product_relevance | 0–100 | Sales Opportunity |
| purchase_history_score | 0–100 | Sales Opportunity |
| crop_acreage_score | 0–100 | Sales Opportunity |
| stock_level_score | 0–100 | Inventory Need |
| sales_velocity_score | 0–100 | Inventory Need |
| stockout_risk_score | 0–100 | Inventory Need |
| relationship_need_score | 0–100 | Relationship Need |
| competitive_pressure_score | 0–100 | Competitive Pressure |
| travel_cost_score | 0–100 | Travel Cost |

---

# 22. Priority Engine Input View

For implementation, combine required fields into one joined feature table:

## Table Name

```text
priority_feature_view
```

## Columns

```text
entity_id
rep_id
territory_id
entity_name
entity_type
primary_crop

pest_disease_risk_score
crop_stage_risk_score
weather_risk_score
ndvi_stress_score

historical_sales_score
seasonal_product_relevance
purchase_history_score
crop_acreage_score

stock_level_score
sales_velocity_score
stockout_risk_score

relationship_need_score
competitive_pressure_score
travel_cost_score
```

---

# 23. Example Priority Feature Row

```json
{
  "entity_id": "ENT001",
  "entity_name": "Ramesh Agro Center",
  "entity_type": "retailer",
  "territory_id": "TERR_WARDHA_01",
  "primary_crop": "Cotton",

  "pest_disease_risk_score": 90,
  "crop_stage_risk_score": 80,
  "weather_risk_score": 85,
  "ndvi_stress_score": 70,

  "historical_sales_score": 82,
  "seasonal_product_relevance": 88,
  "purchase_history_score": 76,
  "crop_acreage_score": 78,

  "stock_level_score": 85,
  "sales_velocity_score": 88,
  "stockout_risk_score": 91,

  "relationship_need_score": 64,
  "competitive_pressure_score": 72,
  "travel_cost_score": 42
}
```

---

# 24. Synthetic Data Generation Strategy

## Step 1 — Create base entities

Generate:

- Reps
- Territories
- Retailers/farmers
- Crops
- Product categories

---

## Step 2 — Add contextual signals

For each entity, generate:

- Weather scores
- Pest alert status
- NDVI stress
- Crop stage
- Sales signals
- Inventory signals

---

## Step 3 — Add realistic relationships

Examples:

```text
High rainfall + high humidity + vulnerable crop stage
→ higher disease risk score
```

```text
Low inventory + high sales velocity
→ higher stockout risk score
```

```text
Competitor promotion + regional sales drop
→ higher competitive pressure score
```

---

## Step 4 — Generate recommendations

Run the scoring engine to create:

- priority score
- priority level
- main reason
- next best action

---

## Step 5 — Generate outcomes

Create sample outcomes based on probability.

Example:

```text
Higher priority score + correct action
→ higher chance of order placed
```

---

# 25. Data Quality Rules

The dataset should avoid random disconnected numbers.

Each row should have logical consistency.

---

## Good Example

```text
Rainfall high
Humidity high
Cotton flowering stage
NDVI stress moderate
→ fungal risk high
```

---

## Bad Example

```text
No rainfall
Low humidity
No NDVI stress
→ fungal risk high
```

Unless a pest bulletin or other reason explains it.

---

# 26. Data-to-Component Mapping

| Data Signal | Used In |
|---|---|
| Weather | Prioritization, Agronomic Logic, Anomaly Detection |
| Pest Alert | Prioritization, Contextual Decision |
| NDVI | Prioritization, Anomaly Detection |
| Crop Stage | Prioritization, Contextual Decision |
| Sales | Sales Opportunity, Anomaly Detection |
| Inventory | Inventory Need, Next Best Action |
| Visit History | Relationship Need, Outcome Learning |
| Competitor Signal | Competitive Pressure |
| Travel Signal | Route Feasibility |
| Outcome Data | Learning Engine |

---

# 27. Final Data Design Summary

The prototype dataset must support this full flow:

```text
Raw Entity + Context Data
        ↓
Feature Scores
        ↓
Priority Ranking
        ↓
Next Best Action
        ↓
Explainable Recommendation
        ↓
Outcome Capture
        ↓
Learning Feedback
```

---

# 28. Final One-Line Definition

```text
A practical synthetic data schema
that converts agricultural, commercial,
inventory, operational, and competitive signals
into usable intelligence for field-force decision-making.
```