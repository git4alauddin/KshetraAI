# Build 03 — Dynamic Prioritization Engine

---

# 1. Build Objective

The purpose of this build is to implement the deterministic multi-signal prioritization engine that ranks retailers, growers, and operational entities for field visits.

This build converts:

```text
Normalized intelligence features
```

into:

```text
Operational visit priorities.
```

The engine should determine:

- who should be visited
- how urgently they should be visited
- why they are prioritized
- which signals contributed most

This build does not implement:

- contextual next-best-action generation
- anomaly detection logic
- explainability text generation
- API routes
- frontend workflows
- outcome learning recalibration

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/01_dynamic_prioritization_engine.md`
- `docs/architecture/05_explainability_and_trust_layer.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/03_priority_engine_contract.md`
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

- Read normalized feature views from Build 02
- Implement weighted multi-signal scoring
- Generate final priority scores
- Generate priority classifications
- Rank entities deterministically
- Build reusable scoring modules
- Preserve feature contribution traceability
- Generate prioritization-ready outputs
- Preserve explainability metadata

---

## Out of Scope

- Contextual recommendation generation
- Product advisory generation
- Anomaly detection logic
- Human-readable explanation generation
- Outcome learning recalibration
- APIs
- Frontend implementation
- ML training
- Route optimization engines
- Autonomous AI reasoning

---

# 4. Core Philosophy

The Dynamic Prioritization Engine should behave as:

```text
An explainable operational urgency engine.
```

The engine should remain:

- deterministic
- modular
- interpretable
- configurable
- evidence-backed

The engine should NOT:

- behave like a black-box AI
- generate unexplained rankings
- infer unsupported operational conclusions

Its responsibility is ONLY:

```text
Generate explainable visit prioritization.
```

---

# 5. Input Data Sources

This build consumes outputs from Build 02.

Expected inputs:

| Input View | Purpose |
|---|---|
| `priority_feature_view.csv` | Primary prioritization features |
| `feature_registry.csv` | Feature metadata |
| `territories.csv` | Territory context |
| `visit_entities.csv` | Entity metadata |

Expected features include:

- weather_risk_score
- pest_risk_score
- ndvi_stress_score
- inventory_need_score
- sales_opportunity_score
- relationship_gap_score
- competitive_pressure_score
- travel_feasibility_score
- account_priority_score
- campaign_engagement_score

---

# 6. Expected Outputs

The engine should generate:

| Output | Purpose |
|---|---|
| `priority_score` | Final urgency score |
| `priority_level` | Operational classification |
| `component_breakdown` | Score contribution visibility |
| `ranked_visit_list.csv` | Ranked entity outputs |
| `priority_trace_log.csv` | Explainability trace metadata |

Outputs should be written to:

```text
datasets/processed/
```

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
backend/engines/
backend/config/
backend/utils/
backend/pipelines/
datasets/processed/
tests/
docs/implementation/
```

---

# 8. Forbidden File Scope

This build must not modify:

```text
private-data/
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

# 9. Recommended Engine Structure

Suggested structure:

```text
backend/engines/

├── priority_engine.py
├── scoring_engine.py
├── ranking_engine.py
├── component_scorers.py
└── priority_classifier.py
```

---

# 10. Priority Scoring Philosophy

The engine should combine:

```text
Multiple operational intelligence dimensions
```

including:

- agronomic urgency
- commercial opportunity
- inventory urgency
- relationship urgency
- competitive pressure
- operational feasibility

The system should prioritize:

```text
Operationally meaningful urgency.
```

NOT:

```text
Pure numerical maximization.
```

---

# 11. Suggested Priority Components

Recommended high-level components:

| Component | Purpose |
|---|---|
| Agronomic Risk | Crop/pest/weather urgency |
| Commercial Opportunity | Sales potential |
| Inventory Urgency | Stock replenishment need |
| Relationship Urgency | Coverage gap |
| Competitive Pressure | Market defense urgency |
| Operational Feasibility | Travel practicality |

---

# 12. Example Component Weighting

Example configuration:

```yaml
agronomic_risk_weight: 0.30
commercial_opportunity_weight: 0.25
inventory_urgency_weight: 0.15
relationship_urgency_weight: 0.10
competitive_pressure_weight: 0.10
operational_feasibility_weight: 0.10
```

Weights must remain configurable.

---

# 13. Example Priority Logic

## Example Inputs

```text
weather_risk_score = 85
pest_risk_score = 90
inventory_need_score = 78
sales_opportunity_score = 82
```

---

## Example Result

```text
priority_score = 84.7
priority_level = Critical
```

---

# 14. Priority Classification Rules

Suggested levels:

| Level | Score Range |
|---|---|
| Critical | 80–100 |
| High | 60–79 |
| Medium | 40–59 |
| Low | 0–39 |

Thresholds should remain configurable.

---

# 15. Ranking Requirements

The engine should generate:

```text
Stable deterministic ranking outputs.
```

Requirements:

- stable sorting
- deterministic tie-breaking
- reproducible rankings
- explainable score ordering

---

# 16. Tie-Breaking Rules

When scores are equal:

Preferred tie-breaking order:

1. Higher agronomic urgency
2. Higher account importance
3. Higher sales opportunity
4. Stable entity ID ordering

Tie-breaking must remain deterministic.

---

# 17. Explainability Preservation Rules

The prioritization engine MUST preserve:

- feature contribution visibility
- component contribution visibility
- rule traceability
- score decomposition

Example:

```json
{
  "agronomic_component": 32.5,
  "commercial_component": 21.0,
  "inventory_component": 14.2
}
```

---

# 18. Priority Trace Logging

The engine should generate trace metadata including:

| Field | Purpose |
|---|---|
| entity_id | Entity reference |
| feature_inputs | Source features |
| component_scores | Component contributions |
| applied_weights | Weight visibility |
| final_priority_score | Final output |
| priority_level | Classification |

---

# 19. Determinism Requirements

This build must remain fully deterministic.

Given identical feature inputs:

```text
Priority outputs must remain identical.
```

Requirements:

- no randomness
- stable ranking order
- stable weighting logic
- stable normalization
- stable output schemas

---

# 20. Configuration Requirements

Weights and thresholds should remain configurable.

Preferred location:

```text
backend/config/
```

Suggested configs:

```text
priority_weights.yaml
priority_thresholds.yaml
ranking_rules.yaml
```

Avoid scattered hardcoded constants.

---

# 21. Validation Requirements

The engine must validate:

- required feature columns exist
- feature ranges remain valid
- weights sum correctly
- no NaN priority scores
- no invalid classifications
- stable ranking generation

Validation failures must remain:

```text
Explicit and operationally understandable.
```

---

# 22. Logging Requirements

The engine should log:

- scoring execution
- weight loading
- ranking generation
- invalid feature warnings
- priority distribution summaries

Avoid excessive noisy logging.

---

# 23. Error Handling Rules

Preferred:

```text
Explicit operational errors.
```

Example:

```text
ERROR:
Missing inventory_need_score for ENT004
```

Avoid:

- silent scoring fallback
- hidden ranking mutation
- silent schema mutation

---

# 24. Output Schema Stability

Generated prioritization outputs should maintain:

- stable column order
- stable naming conventions
- stable ranking semantics

Priority schemas become downstream contracts.

---

# 25. Testing Requirements

Tests should validate:

- deterministic scoring
- deterministic ranking
- weight application correctness
- tie-breaking correctness
- classification correctness
- schema consistency
- explainability metadata preservation

---

# 26. Anti-Drift Rules

This build MUST NOT:

- generate contextual recommendations
- infer anomaly alerts
- generate explanation text
- implement APIs
- introduce ML models
- redesign architecture
- silently alter schemas

This build is ONLY responsible for:

```text
Deterministic prioritization infrastructure.
```

---

# 27. Deliverables

Expected outputs:

- priority engine modules
- scoring engine
- ranking engine
- configurable weighting system
- ranked visit outputs
- priority trace metadata
- deterministic prioritization pipeline
- prioritization validation layer

---

# 28. Completion Criteria

This build is complete when:

- priority scores generate successfully
- rankings remain deterministic
- explainability metadata is preserved
- output schemas remain stable
- tie-breaking remains deterministic
- validation passes successfully
- architecture boundaries remain preserved

---

# 29. Final One-Line Definition

```text
A deterministic multi-signal prioritization engine
that converts normalized agricultural intelligence features
into explainable,
ranked,
and operationally meaningful field visit priorities.
```

---

# 30. Task Breakdown & Execution Order

Use `docs/implementation/build_execution_prompt.md` while working through this build.

Each task heading below is intended to be usable as the future commit heading. Work one task at a time: present the heading, short brief, expected file scope, and what will not be touched; then wait for explicit implementation approval.

| Order | Commit Heading | Scope | Primary Files |
|---|---|---|---|
| 1 | Build 03: Configure priority weights | Define deterministic component weights and priority thresholds. | `backend/config/priority_weights.yaml`, `backend/config/decision_thresholds.yaml` |
| 2 | Build 03: Implement component scorers | Convert feature signals into bounded component scores with trace metadata. | `backend/engines/component_scorers.py` |
| 3 | Build 03: Implement weighted priority scoring | Combine component scores into final priority scores without recommendation logic. | `backend/engines/scoring_engine.py`, `backend/engines/priority_engine.py` |
| 4 | Build 03: Implement deterministic ranking | Rank entities with stable sorting and explicit tie-breaking. | `backend/engines/ranking_engine.py` |
| 5 | Build 03: Implement priority classification | Assign priority bands using configured thresholds and stable labels. | `backend/engines/priority_classifier.py` |
| 6 | Build 03: Add priority engine tests | Validate weighting, tie-breaking, classification, schema stability, and determinism. | `tests/` |
| 7 | Build 03: Verify prioritization checklist | Confirm this build ranks priorities only and does not create recommendations, anomalies, APIs, or frontend behavior. | `docs/implementation/03_dynamic_prioritization_engine.md` |

Per-task completion rule: after the human commits and says done, verify the committed scope, confirm the matching checklist items, and propose the next task.
