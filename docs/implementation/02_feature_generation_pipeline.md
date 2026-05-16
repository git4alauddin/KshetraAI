# Build 02 — Feature Generation Pipeline

---

# 1. Build Objective

The purpose of this build is to transform validated operational data into normalized, explainable, deterministic intelligence features that can power downstream reasoning engines.

This build converts:

```text
Raw operational signals
```

into:

```text
Feature-ready intelligence scores and contextual indicators.
```

The generated features will support:

- dynamic prioritization
- contextual recommendations
- anomaly detection
- explainability generation
- outcome learning

This build does not implement:

- final priority scoring
- ranking logic
- next-best-action generation
- anomaly detection logic
- explainability text generation
- APIs
- frontend behavior

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/01_dynamic_prioritization_engine.md`
- `docs/architecture/02_contextual_decision_engine.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/02_feature_builder_contract.md`
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

- Read validated canonical datasets from `datasets/processed/`
- Generate normalized intelligence features
- Generate explainable intermediate scores
- Implement deterministic feature engineering pipelines
- Build reusable feature generation modules
- Build feature-ready processed views
- Validate feature ranges and feature completeness
- Generate stable feature outputs
- Create feature mapping documentation
- Preserve operational traceability

---

## Out of Scope

- Final weighted prioritization
- Ranking logic
- Recommendation generation
- Contextual reasoning
- Anomaly detection logic
- Explainability text generation
- Outcome learning recalibration
- API implementation
- Frontend implementation
- ML model training
- Autonomous AI reasoning

---

# 4. Core Philosophy

The Feature Generation Pipeline should produce:

```text
Operationally meaningful,
normalized,
interpretable intelligence signals.
```

The pipeline should remain:

- deterministic
- explainable
- modular
- auditable
- configurable

The pipeline should NOT:

- generate final decisions
- infer recommendations
- trigger anomalies
- generate human explanations

Its responsibility is ONLY:

```text
Convert raw operational data
into usable intelligence features.
```

---

# 5. Input Data Sources

This build consumes outputs from Build 01.

Expected processed inputs:

| Input Dataset | Purpose |
|---|---|
| `representatives.csv` | Rep context |
| `territories.csv` | Territory context |
| `visit_entities.csv` | Entity context |
| `crop_context.csv` | Crop-stage intelligence |
| `weather_signals.csv` | Weather context |
| `pest_signals.csv` | Pest/disease context |
| `ndvi_signals.csv` | Crop stress context |
| `sales_signals.csv` | Commercial opportunity context |
| `inventory_signals.csv` | Inventory health context |
| `competitor_signals.csv` | Competitive pressure context |
| `visit_history.csv` | Relationship & coverage context |

All input datasets are expected to be:

```text
Validated,
normalized,
and deterministic.
```

---

# 6. Expected Output Features

The pipeline should generate normalized feature outputs including:

| Feature | Purpose |
|---|---|
| `weather_risk_score` | Agronomic weather risk |
| `pest_disease_risk_score` | Pest/disease operational risk |
| `ndvi_stress_score` | Crop stress intensity |
| `inventory_need_score` | Stock replenishment urgency |
| `sales_opportunity_score` | Commercial opportunity strength |
| `relationship_need_score` | Rep engagement gap |
| `competitive_pressure_score` | Competitor market pressure |
| `travel_cost_score` | Operational routing cost |
| `account_priority_score` | Strategic account importance |
| `campaign_engagement_score` | Grower/retailer engagement quality |

Implementation aliases are preserved in the feature registry for older wording:

| Alias | Canonical Feature |
|---|---|
| `pest_risk_score` | `pest_disease_risk_score` |
| `relationship_gap_score` | `relationship_need_score` |
| `travel_feasibility_score` | `travel_cost_score` |

---

# 7. Expected Canonical Feature Views

This build should generate:

| Output View | Purpose |
|---|---|
| `priority_feature_view.csv` | Prioritization-ready features |
| `contextual_feature_view.csv` | Contextual recommendation-ready features |
| `anomaly_feature_view.csv` | Baseline anomaly indicators |
| `feature_registry.csv` | Feature metadata registry |

Outputs should be written to:

```text
datasets/processed/
```

---

# 8. Expected File Scope

Implementation for this build may modify only:

```text
backend/features/
backend/pipelines/
backend/utils/feature_utils.py
backend/config/
datasets/processed/
tests/
docs/implementation/
```

---

# 9. Forbidden File Scope

This build must not modify:

```text
private-data/
backend/engines/
backend/anomaly/
backend/explainability/
backend/learning/
backend/api/
frontend/
docs/architecture/
docs/implementation_contracts/
```

Architecture and contracts remain read-only unless explicitly revised by humans.

---

# 10. Recommended Feature Modules

Suggested structure:

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

# 11. Agronomic Feature Responsibilities

Generate:

- weather risk indicators
- crop-stage vulnerability indicators
- pest escalation indicators
- NDVI stress indicators

---

## Example

### Raw Signals

```text
Humidity = 87%
Rainfall = 112 mm
Cotton flowering stage
```

### Generated Feature

```text
weather_risk_score = 85
```

---

# 12. Inventory Feature Responsibilities

Generate:

- stock depletion indicators
- replenishment urgency
- stock-out probability indicators

---

## Example

### Raw Signals

```text
Current stock = 12
Normal stock = 50
```

### Generated Feature

```text
inventory_need_score = 91
```

---

# 13. Sales Feature Responsibilities

Generate:

- demand momentum
- purchase probability
- seasonal opportunity indicators
- historical sales strength

---

## Example

### Raw Signals

```text
Sales last 30d = 48
Baseline = 28
```

### Generated Feature

```text
sales_opportunity_score = 84
```

---

# 14. Relationship Feature Responsibilities

Generate:

- visit coverage gaps
- relationship freshness indicators
- rep engagement urgency

---

## Example

### Raw Signals

```text
Last visit = 24 days ago
```

### Generated Feature

```text
relationship_gap_score = 78
```

---

# 15. Competitive Feature Responsibilities

Generate:

- competitor pressure indicators
- defensive market urgency
- market-share risk indicators

---

# 16. Travel Feature Responsibilities

Generate:

- route feasibility indicators
- distance cost estimates
- operational accessibility indicators

This build should remain:

```text
Lightweight and heuristic-driven.
```

NOT:

```text
full route optimization.
```

---

# 17. Campaign Engagement Features

Generate:

- WhatsApp engagement quality
- campaign participation quality
- digital funnel responsiveness

---

## Example

### Raw Signals

```text
WhatsApp click-through high
Campaign attendance high
```

### Generated Feature

```text
campaign_engagement_score = 82
```

---

# 18. Feature Normalization Rules

All normalized feature scores should preferably remain within:

```text
0 → 100
```

unless explicitly justified otherwise.

Requirements:

- stable scaling
- deterministic transformations
- explainable scoring logic
- reproducible normalization

---

# 19. Feature Explainability Rules

Every feature should remain:

```text
Operationally interpretable.
```

Example:

Correct:

```text
weather_risk_score
inventory_need_score
```

Avoid:

```text
latent_vector_1
hidden_score_x
```

The system must preserve:

```text
Feature-level explainability.
```

---

# 20. Determinism Requirements

This build must remain fully deterministic.

Given identical input datasets:

```text
Feature outputs must remain identical.
```

Requirements:

- no randomness
- stable sorting
- stable transformations
- stable normalization
- stable output schemas

---

# 21. Feature Registry Requirements

The pipeline should maintain a feature registry containing:

| Field | Purpose |
|---|---|
| feature_name | Canonical feature name |
| source_tables | Input dependencies |
| generation_logic | Human-readable logic |
| normalization_strategy | Scaling explanation |
| valid_range | Allowed value range |
| explainability_category | Operational meaning |

---

# 22. Validation Requirements

The pipeline must validate:

- required source columns exist
- no invalid feature ranges
- no NaN feature outputs where prohibited
- stable row counts
- stable entity mapping
- deterministic output generation

Validation failures must remain:

```text
Explicit and operationally understandable.
```

---

# 23. Logging Requirements

The pipeline should log:

- feature generation start/end
- row counts
- missing-value handling
- normalization warnings
- invalid-range warnings
- feature output summaries

Avoid excessive noisy logging.

---

# 24. Error Handling Rules

Preferred:

```text
Explicit operational errors.
```

Example:

```text
ERROR:
Missing humidity_percent in weather_signals.csv
```

Avoid:

- silent feature fallback
- hidden imputation
- silent schema mutation

---

# 25. Configuration Requirements

Thresholds and scaling logic should remain configurable.

Preferred location:

```text
backend/config/
```

Suggested configs:

```text
feature_thresholds.yaml
feature_scaling.yaml
normalization_rules.yaml
```

Avoid scattered hardcoded constants.

---

# 26. Output Schema Stability

Generated feature views should maintain:

- stable column order
- stable naming conventions
- stable feature semantics

Feature schemas become downstream contracts.

---

# 27. Testing Requirements

Tests should validate:

- deterministic feature generation
- normalization correctness
- expected feature ranges
- schema consistency
- stable output generation
- entity mapping correctness

---

# 28. Anti-Drift Rules

This build MUST NOT:

- implement scoring engines
- generate rankings
- infer recommendations
- generate anomaly alerts
- create explainability text
- introduce ML models
- redesign architecture
- silently alter schemas

This build is ONLY responsible for:

```text
Feature engineering infrastructure.
```

---

# 29. Deliverables

Expected outputs:

- feature generation modules
- normalized feature views
- feature registry
- deterministic feature pipelines
- feature validation layer
- processed feature datasets
- feature documentation

---

# 30. Completion Criteria

This build is complete when:

- all required features generate successfully
- feature outputs remain deterministic
- feature schemas remain stable
- outputs are explainable
- feature views are reusable downstream
- validation passes successfully
- architecture boundaries remain preserved

---

# 31. Completion Checklist

## Configuration & Registry

- [x] feature threshold configuration exists
- [x] feature registry metadata exists
- [x] all registry features use `0-100` valid ranges
- [x] source dependencies are documented per feature
- [x] generation logic is human-readable
- [x] normalization strategy is documented
- [x] explainability category is documented
- [x] alias mappings preserve doc wording while using canonical architecture names

## Feature Builders

- [x] agronomic feature builders exist
- [x] sales feature builders exist
- [x] inventory feature builders exist
- [x] relationship feature builders exist
- [x] competitor feature builders exist
- [x] travel feature builders exist
- [x] missing required inputs fail explicitly
- [x] generated feature scores are clamped to `0-100`
- [x] feature outputs are deterministic for identical inputs

## Output Views

- [x] `priority_feature_view` is generated or ready to generate
- [x] `contextual_feature_view` is generated or ready to generate
- [x] `anomaly_feature_view` is generated or ready to generate
- [x] `feature_registry` output is generated or ready to generate
- [x] output column order is stable
- [x] entity mapping is stable
- [x] feature view writer supports deterministic CSV output

## Architecture Compliance

- [x] no priority scoring engine added
- [x] no ranking logic added
- [x] no recommendation logic added
- [x] no anomaly alert logic added
- [x] no explainability text generation added
- [x] no API/frontend changes added
- [x] no private source data mutation
- [x] no generated processed outputs are committed

## Testing

- [x] feature registry tests pass
- [x] agronomic feature tests pass
- [x] sales and inventory feature tests pass
- [x] relationship, competitor, and travel feature tests pass
- [x] feature pipeline tests pass
- [x] Build 01 regression tests pass

## Build 02 Verification

- [x] Build 02 unit tests pass with `python -m unittest tests.test_build02_feature_registry tests.test_build02_agronomic_features tests.test_build02_sales_inventory_features tests.test_build02_relationship_competitor_travel_features tests.test_build02_feature_pipeline`
- [x] Build 01 regression tests pass with `python -m unittest tests.test_build01_csv_loader tests.test_build01_schema_validator tests.test_build01_value_normalizer tests.test_build01_entity_joiner tests.test_build01_pipeline_runner`
- [x] No generated private-derived row outputs are left in `datasets/processed/`

---

# 32. Final One-Line Definition

```text
A deterministic feature engineering pipeline
that transforms validated agricultural operational data
into explainable,
normalized,
and reusable intelligence signals
for downstream decision engines.
```

---

# 33. Task Breakdown & Execution Order

Use `docs/implementation/build_execution_prompt.md` while working through this build.

Each task heading below is intended to be usable as the future commit heading. Work one task at a time: present the heading, short brief, expected file scope, and what will not be touched; then wait for explicit implementation approval.

| Order | Commit Heading | Scope | Primary Files |
|---|---|---|---|
| 1 | Build 02: Define feature thresholds and registry | Establish configurable thresholds and feature metadata without generating final priorities. | `backend/config/feature_thresholds.yaml`, `backend/features/feature_registry.py` |
| 2 | Build 02: Implement agronomic feature builders | Generate weather, pest, crop-stage, and NDVI-style agronomic feature signals from processed inputs. | `backend/features/agronomic_features.py` |
| 3 | Build 02: Implement sales and inventory feature builders | Generate deterministic sales opportunity and inventory urgency feature signals. | `backend/features/sales_features.py`, `backend/features/inventory_features.py` |
| 4 | Build 02: Implement relationship, competitor, and travel feature builders | Generate engagement gap, competitive pressure, and lightweight travel feasibility signals. | `backend/features/relationship_features.py`, `backend/features/competitor_features.py`, `backend/features/travel_features.py` |
| 5 | Build 02: Implement feature pipeline output views | Orchestrate feature builders into stable priority, contextual, anomaly, and registry outputs. | `backend/features/feature_pipeline.py`, `backend/pipelines/`, `datasets/processed/` |
| 6 | Build 02: Add feature generation tests | Validate ranges, schema stability, deterministic generation, and missing-input errors. | `tests/` |
| 7 | Build 02: Verify feature pipeline checklist | Confirm this build generated features only and did not introduce scoring, recommendations, alerts, APIs, or frontend behavior. | `docs/implementation/02_feature_generation_pipeline.md` |

Per-task completion rule: after the human commits and says done, verify the committed scope, confirm the matching checklist items, and propose the next task.
