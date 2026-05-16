# Build 06 — Explainability & Trust Engine

---

# 1. Build Objective

The purpose of this build is to implement the deterministic explainability layer that converts prioritization scores, contextual recommendations, and anomaly alerts into transparent operational reasoning.

This build converts:

```text
Scores + rules + signals + alerts
```

into:

```text
Evidence-backed explanations and trust metadata.
```

The engine should determine:

- why an entity was prioritized
- why a recommendation was generated
- why an anomaly was triggered
- which signals contributed most
- how confident the system is

This build does not implement:

- priority scoring
- recommendation generation
- anomaly detection
- APIs
- frontend workflows
- autonomous LLM-based reasoning
- outcome learning recalibration

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/05_explainability_and_trust_layer.md`
- `docs/architecture/01_dynamic_prioritization_engine.md`
- `docs/architecture/02_contextual_decision_engine.md`
- `docs/architecture/03_anomaly_and_opportunity_detection.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/06_explainability_engine_contract.md`
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

- Read outputs from prioritization, contextual decision, and anomaly builds
- Map feature contributions to explanation evidence
- Map triggered rules to explanation traces
- Generate structured explanation objects
- Generate confidence metadata
- Generate evidence summaries
- Generate safe operational explanation text using templates
- Preserve traceability metadata
- Validate explanation completeness and safety

---

## Out of Scope

- Priority scoring
- Contextual recommendation generation
- Anomaly detection
- Outcome learning
- API implementation
- Frontend implementation
- Free-form LLM generation
- Autonomous reasoning
- ML model training

---

# 4. Core Philosophy

The Explainability & Trust Engine should behave as:

```text
A deterministic operational reasoning translator.
```

The engine should remain:

- evidence-backed
- deterministic
- template-driven
- traceable
- operationally safe
- human-readable

The engine should NOT:

- invent new intelligence
- hallucinate reasons
- make unsupported claims
- modify recommendations
- modify scores
- modify alerts

Its responsibility is ONLY:

```text
Explain existing intelligence outputs.
```

---

# 5. Input Data Sources

This build consumes outputs from previous builds.

Expected inputs:

| Input View | Purpose |
|---|---|
| `ranked_visit_list.csv` | Priority outputs |
| `priority_trace_log.csv` | Priority feature contribution trace |
| `recommendation_outputs.csv` | Contextual action outputs |
| `recommendation_trace_log.csv` | Rule/action trace metadata |
| `anomaly_alerts.csv` | Structured anomaly alerts |
| `anomaly_trace_log.csv` | Alert evidence trace |
| `feature_registry.csv` | Feature meaning and source metadata |

---

# 6. Expected Outputs

The engine should generate:

| Output | Purpose |
|---|---|
| `explanation_outputs.csv` | Entity-level explanations |
| `explanation_trace_log.csv` | Traceability metadata |
| `evidence_summary` | Human-readable evidence |
| `confidence_reasoning` | Why confidence is high/medium/low |
| `safe_explanation_text` | Rep-facing explanation text |

Outputs should be written to:

```text
datasets/processed/
```

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
backend/explainability/
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
backend/engines/
backend/anomaly/
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
backend/explainability/

├── explanation_engine.py
├── evidence_mapper.py
├── confidence_engine.py
├── template_generator.py
├── reasoning_formatter.py
└── explanation_registry.py
```

---

# 10. Explanation Categories

The engine should support:

| Explanation Type | Purpose |
|---|---|
| Priority Explanation | Why the entity was ranked |
| Recommendation Explanation | Why the next-best action was suggested |
| Anomaly Explanation | Why the alert was triggered |
| Confidence Explanation | Why the confidence level was assigned |
| Evidence Summary | Which signals supported the output |

---

# 11. Priority Explanation Logic

## Purpose

Explain:

```text
Why this entity was prioritized.
```

## Example Inputs

```text
priority_score = 84
agronomic_component = high
inventory_component = high
sales_component = medium
```

## Example Output

```text
This retailer is prioritized because agronomic urgency and inventory need are both high.
```

---

# 12. Recommendation Explanation Logic

## Purpose

Explain:

```text
Why this action was recommended.
```

## Example Inputs

```text
triggered_rule = COTTON_FUNGAL_RISK_01
recommended_action = discuss_fungicide_advisory
supporting_signals = rainfall, humidity, crop_stage, NDVI
```

## Example Output

```text
A fungicide advisory discussion is recommended because cotton is in a vulnerable growth stage and recent rainfall and humidity increase fungal disease risk.
```

---

# 13. Anomaly Explanation Logic

## Purpose

Explain:

```text
Why this alert was triggered.
```

## Example Inputs

```text
alert_type = Stock-Out Risk
current_stock_units = 12
normal_stock_units = 50
sales_velocity_score = 88
```

## Example Output

```text
A stock-out risk alert was triggered because current stock is significantly below normal levels while sales velocity remains high.
```

---

# 14. Confidence Explanation Logic

## Purpose

Explain:

```text
Why confidence is high, medium, or low.
```

Suggested confidence interpretation:

| Confidence | Meaning |
|---|---|
| High | Multiple aligned strong signals |
| Medium | Partial supporting evidence |
| Low | Weak or incomplete evidence |

---

# 15. Evidence Mapping Requirements

Every explanation must preserve:

- source signals
- matched rules
- score contributions
- anomaly trigger evidence
- confidence basis

Explanations must never exist without evidence.

---

# 16. Template-Based Explanation Rules

Explanations should initially be generated using:

```text
Structured templates.
```

Preferred config location:

```text
backend/config/explanation_templates.yaml
```

Avoid:

```text
Uncontrolled free-form LLM generation.
```

---

# 17. Safety Requirements

The engine MUST avoid:

- confirmed disease claims
- unsupported agronomic certainty
- hallucinated explanations
- unsupported product claims
- contradiction between evidence and explanation

Correct:

```text
Possible fungal disease risk detected.
```

Incorrect:

```text
Crop is definitely infected.
```

---

# 18. Explanation Output Structure

Each explanation should include:

| Field | Purpose |
|---|---|
| `entity_id` | Entity reference |
| `explanation_type` | Priority / Recommendation / Anomaly |
| `summary_text` | Human-readable explanation |
| `evidence_items` | Supporting evidence |
| `confidence_level` | Confidence value |
| `confidence_reasoning` | Why confidence was assigned |
| `source_trace_ids` | Links to trace metadata |

---

# 19. Example Explanation Output

```json
{
  "entity_id": "ENT001",
  "explanation_type": "recommendation",
  "summary_text": "A fungicide advisory discussion is recommended because cotton is in a vulnerable flowering stage and recent rainfall and humidity increase fungal disease risk.",
  "evidence_items": [
    "Cotton flowering stage",
    "High rainfall deviation",
    "High humidity",
    "NDVI stress detected"
  ],
  "confidence_level": "High",
  "confidence_reasoning": "Multiple agronomic signals are aligned."
}
```

---

# 20. Explanation Trace Logging

The engine should preserve trace metadata including:

| Field | Purpose |
|---|---|
| `entity_id` | Entity reference |
| `source_output_type` | Priority / Recommendation / Alert |
| `source_output_id` | Linked output ID |
| `evidence_used` | Evidence items |
| `template_used` | Explanation template ID |
| `confidence_rule_used` | Confidence rule ID |
| `safety_validation_status` | Safe / Needs Review |

---

# 21. Determinism Requirements

This build must remain fully deterministic.

Given identical input traces:

```text
Explanation outputs must remain identical.
```

Requirements:

- no randomness
- stable template selection
- stable evidence ordering
- stable confidence rules
- stable output schemas

---

# 22. Configuration Requirements

Templates and confidence rules should remain configurable.

Preferred location:

```text
backend/config/
```

Suggested configs:

```text
explanation_templates.yaml
confidence_rules.yaml
safety_terms.yaml
```

Avoid scattered hardcoded explanation logic.

---

# 23. Validation Requirements

The engine must validate:

- evidence exists for each explanation
- source traces exist
- explanation type is valid
- confidence value is valid
- unsafe certainty language is avoided
- explanation text does not contradict evidence

Validation failures must remain:

```text
Explicit and operationally understandable.
```

---

# 24. Logging Requirements

The engine should log:

- explanation generation start/end
- missing evidence warnings
- template selection
- confidence assignment
- safety validation failures

Avoid excessive noisy logging.

---

# 25. Error Handling Rules

Preferred:

```text
Explicit operational warnings.
```

Example:

```text
WARNING:
No evidence found for recommendation REC004; explanation not generated.
```

Avoid:

- hallucinated fallback explanation
- silent explanation generation
- hidden schema mutation

---

# 26. Output Schema Stability

Generated explanation outputs should maintain:

- stable column order
- stable naming conventions
- stable explanation categories
- stable confidence labels

Explanation schemas become downstream contracts.

---

# 27. Testing Requirements

Tests should validate:

- deterministic explanation generation
- evidence mapping correctness
- template selection correctness
- confidence assignment correctness
- unsafe claim prevention
- schema consistency
- no explanation without evidence

---

# 28. Anti-Drift Rules

This build MUST NOT:

- generate priority scores
- generate recommendations
- detect anomalies
- implement APIs
- introduce uncontrolled LLM generation
- redesign architecture
- silently alter schemas

This build is ONLY responsible for:

```text
Deterministic explainability and trust infrastructure.
```

---

# 29. Deliverables

Expected outputs:

- explanation engine modules
- evidence mapper
- confidence engine
- template generator
- confidence and template safety rules
- explanation output datasets
- explanation trace metadata
- configurable templates
- explanation validation layer

---

# 30. Completion Criteria

This build is complete when:

- explanations generate successfully
- every explanation is evidence-backed
- explanation outputs remain deterministic
- unsafe certainty claims are blocked
- confidence reasoning works correctly
- output schemas remain stable
- validation passes successfully
- architecture boundaries remain preserved

---

# 31. Final One-Line Definition

```text
A deterministic explainability and trust engine
that converts existing operational intelligence outputs
into evidence-backed,
safe,
traceable,
and human-understandable reasoning.
```

---

# 32. Task Breakdown & Execution Order

Use `docs/implementation/build_execution_prompt.md` while working through this build.

Each task heading below is intended to be usable as the future commit heading. Work one task at a time: present the heading, short brief, expected file scope, and what will not be touched; then wait for explicit implementation approval.

| Order | Commit Heading | Scope | Primary Files |
|---|---|---|---|
| 1 | Build 06: Define explanation templates and confidence rules | Configure approved explanation templates, evidence requirements, and confidence-language rules. | `backend/config/explanation_templates.yaml`, `backend/config/confidence_rules.yaml` |
| 2 | Build 06: Implement evidence mapping | Map priority, recommendation, and alert outputs back to supported evidence fields. | `backend/explainability/evidence_mapper.py`, `backend/explainability/explanation_registry.py` |
| 3 | Build 06: Implement confidence reasoning | Convert score traces and evidence completeness into stable confidence signals. | `backend/explainability/confidence_engine.py` |
| 4 | Build 06: Implement explanation generation | Generate deterministic, template-based explanations without uncontrolled LLM output. | `backend/explainability/explanation_engine.py`, `backend/explainability/template_generator.py` |
| 5 | Build 06: Implement reasoning formatting | Format explanations for API/frontend consumption with stable schema and safe wording. | `backend/explainability/reasoning_formatter.py` |
| 6 | Build 06: Add explainability tests | Validate evidence coverage, template output, confidence labels, safety language, and determinism. | `tests/` |
| 7 | Build 06: Verify explainability checklist | Confirm this build explains existing outputs only and does not add scoring, recommendations, anomalies, APIs, or frontend logic. | `docs/implementation/06_explainability_and_trust_engine.md` |

Per-task completion rule: after the human commits and says done, verify the committed scope, confirm the matching checklist items, and propose the next task.
