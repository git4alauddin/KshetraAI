# KshetraAI — Data Pipeline Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the KshetraAI data pipeline layer.

This module is responsible for:

```text
Loading, validating, normalizing,
and preparing raw operational data
for downstream intelligence engines.
```

The data pipeline is the foundational layer of the system.

All intelligence components depend on it.

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Data Pipeline |
| Layer | Data Processing Layer |
| Primary Responsibility | Raw data preparation |
| Downstream Consumers | Feature Builder, Engines, APIs |
| Architecture Dependency Level | Foundational |

---

# 3. Core Philosophy

The data pipeline should:

- remain deterministic
- remain explainable
- avoid hidden transformations
- preserve schema consistency
- remain operationally transparent

The pipeline should NOT:

- contain business intelligence logic
- contain recommendation logic
- contain anomaly inference
- contain explainability generation

---

# 4. Responsibilities

The data pipeline IS responsible for:

- loading raw datasets
- validating schemas
- validating required fields
- handling missing values
- performing lightweight normalization
- standardizing datatypes
- joining related datasets
- preparing feature-ready datasets
- generating clean intermediate tables

---

# 5. Non-Responsibilities

The data pipeline is NOT responsible for:

- weighted scoring
- recommendation generation
- anomaly detection
- confidence estimation
- explanation generation
- rule triggering
- learning/recalibration
- frontend formatting

These belong to downstream intelligence modules.

---

# 6. Input Data Sources

The pipeline may process:

| Source | Purpose |
|---|---|
| representatives | Rep data |
| territories | Territory mapping |
| visit_entities | Farmer/retailer entities |
| crop_context | Crop stage information |
| weather_signals | Weather risk data |
| pest_signals | Pest alerts |
| ndvi_signals | Crop stress indicators |
| sales_signals | Sales opportunity context |
| inventory_signals | Inventory need context |
| competitor_signals | Competitive pressure |
| visit_history | Relationship context |
| recommendation_log | Historical recommendations |
| outcome_log | Historical outcomes |

---

# 7. Allowed Inputs

Input formats allowed:

```text
CSV
SQLite
PostgreSQL
Pandas DataFrames
```

Future support may include:

```text
REST APIs
Streaming data
Cloud object storage
```

but NOT required for V1.

---

# 8. Expected Outputs

The pipeline should output:

- clean validated datasets
- normalized tables
- merged entity views
- feature-ready views
- intermediate processing tables

---

# 9. Primary Output View

Main expected output:

```text
priority_feature_view
```

This view will later feed:

- priority engine
- contextual engine
- anomaly engine

---

# 10. Example Output Schema

```json
{
  "entity_id": "ENT001",
  "territory_id": "TERR001",

  "weather_risk_score": 85,
  "pest_disease_risk_score": 90,
  "ndvi_stress_score": 70,

  "sales_opportunity_score": 84,
  "inventory_need_score": 88,

  "relationship_need_score": 64,
  "competitive_pressure_score": 72,

  "travel_cost_score": 42
}
```

---

# 11. Allowed File Ownership

The AI MAY modify:

```text
backend/data/
backend/pipelines/
backend/utils/data_utils.py
datasets/processed/
```

---

# 12. Forbidden File Ownership

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

# 13. Recommended Folder Structure

```text
backend/

├── data/
│   ├── loaders/
│   ├── validators/
│   ├── normalizers/
│   ├── joins/
│   └── schemas/
│
├── pipelines/
│   ├── build_priority_view.py
│   ├── build_context_view.py
│   └── pipeline_runner.py
```

---

# 14. Required Submodules

## Data Loaders

Purpose:

```text
Load raw datasets into memory.
```

Examples:

```text
csv_loader.py
sqlite_loader.py
```

---

## Validators

Purpose:

```text
Validate schema integrity and required fields.
```

Checks:

- missing columns
- datatype mismatches
- invalid values
- duplicate IDs

---

## Normalizers

Purpose:

```text
Normalize raw values into standardized formats.
```

Examples:

- lowercase categorical fields
- normalize dates
- handle missing values
- standardize IDs

---

## Join Layer

Purpose:

```text
Combine multiple tables into feature-ready datasets.
```

---

# 15. Missing Value Handling Rules

The pipeline MUST handle:

| Case | Strategy |
|---|---|
| Missing numeric values | safe defaults or null |
| Missing categorical values | unknown category |
| Missing IDs | reject row |
| Missing critical signals | log warning |

---

# 16. Validation Rules

The pipeline MUST validate:

- unique entity IDs
- valid territory mapping
- valid score ranges
- non-negative inventory
- valid dates
- valid categorical values

---

# 17. Data Quality Rules

The pipeline should reject or warn on:

- impossible values
- broken relationships
- inconsistent IDs
- corrupted rows

---

# Example

Invalid:

```text
humidity = 240%
```

Invalid:

```text
negative inventory
```

Invalid:

```text
missing entity_id
```

---

# 18. Logging Requirements

The pipeline MUST log:

- rows processed
- rows rejected
- validation failures
- missing values
- join mismatches

Example:

```text
WARNING:
Missing weather signal for ENT004
```

---

# 19. Transformation Rules

The data pipeline may perform:

- lightweight normalization
- formatting
- joins
- safe cleaning

The data pipeline MUST NOT:

- infer business logic
- assign final intelligence scores
- trigger recommendations
- infer anomalies

---

# 20. Schema Preservation Rule

The pipeline MUST preserve:

- column naming conventions
- table structures
- ID consistency

The AI MUST NOT:

- rename schema fields
- silently alter output formats
- create undocumented fields

---

# 21. Deterministic Processing Rule

The pipeline must remain:

```text
Fully deterministic.
```

Given identical inputs:

```text
Outputs must remain identical.
```

Avoid:

- random transformations
- non-deterministic ordering
- hidden state

---

# 22. Output Format Rules

Preferred output format:

```text
Pandas DataFrame
```

Persisted output options:

```text
CSV
SQLite
PostgreSQL tables
```

---

# 23. Error Handling Rules

The pipeline should fail clearly.

Preferred:

```text
ERROR:
Missing required column: entity_id
```

Avoid:

```text
silent row skipping
silent schema mutation
```

---

# 24. Performance Philosophy

V1 priorities:

- correctness
- clarity
- explainability

NOT:

- distributed scaling
- Spark optimization
- streaming optimization

Prototype-first engineering is preferred.

---

# 25. Testing Requirements

The pipeline should be testable for:

- schema validation
- joins
- missing values
- output integrity
- deterministic behavior

---

# 26. Allowed Dependencies

Allowed:

```text
pandas
numpy
pathlib
typing
sqlite3
sqlalchemy
```

---

# 27. Forbidden Dependencies

Avoid:

```text
spark
kafka
distributed orchestration frameworks
heavy ETL platforms
```

unless explicitly requested later.

---

# 28. Example Processing Flow

```text
Raw CSV Files
        ↓
Data Loader
        ↓
Validation
        ↓
Normalization
        ↓
Table Joins
        ↓
Feature-Ready Views
        ↓
Output Tables
```

---

# 29. Integration Dependencies

The pipeline feeds:

| Downstream Module | Dependency |
|---|---|
| Feature Builder | primary |
| Priority Engine | indirect |
| Contextual Engine | indirect |
| Anomaly Engine | indirect |

---

# 30. Anti-Drift Rules

The AI MUST NOT:

- add recommendation logic
- create hidden scoring
- mix feature engineering with intelligence logic
- alter contracts silently

The pipeline should remain:

```text
Pure data preparation infrastructure.
```

---

# 31. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Are schemas preserved? | Yes/No |
| Are joins deterministic? | Yes/No |
| Is logging clear? | Yes/No |
| Are missing values handled safely? | Yes/No |
| Are no intelligence rules added? | Yes/No |
| Is scope respected? | Yes/No |

---

# 32. Final One-Line Definition

```text
A deterministic foundational data-processing layer
that prepares clean, validated,
feature-ready operational datasets
for downstream agricultural intelligence engines.
```