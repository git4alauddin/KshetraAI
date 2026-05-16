# Build 04 — Contextual Decision Engine

---

# 1. Build Objective

The purpose of this build is to implement the deterministic contextual decision engine that converts prioritized entity context into next-best-action recommendations.

This build converts:

```text
Priority outputs + contextual feature signals
```

into:

```text
Structured operational recommendations.
```

The engine should determine:

- what risk or opportunity exists
- what action the field representative should take
- which product category may be discussed
- which operational follow-up is relevant
- what confidence level applies
- which rules/signals triggered the recommendation

This build does not implement:

- priority scoring
- anomaly detection
- final human-readable explanation text
- outcome learning
- API routes
- frontend workflows
- autonomous LLM reasoning

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/02_contextual_decision_engine.md`
- `docs/architecture/01_dynamic_prioritization_engine.md`
- `docs/architecture/05_explainability_and_trust_layer.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/04_contextual_decision_engine_contract.md`
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

- Read priority outputs from Build 03
- Read contextual feature views from Build 02
- Implement deterministic rule matching
- Generate risk/opportunity labels
- Generate next-best-action recommendations
- Generate product category recommendations
- Generate advisory/follow-up action lists
- Assign confidence levels using controlled rules
- Preserve matched-rule and evidence metadata
- Write structured recommendation outputs

## Out of Scope

- Priority score calculation
- Feature generation
- Anomaly detection
- Explanation text generation
- Outcome logging
- API implementation
- Frontend implementation
- Free-form LLM recommendations
- Unsupported agronomic diagnosis
- Brand-specific claims not grounded in data/rules

---

# 4. Core Philosophy

The Contextual Decision Engine should behave as:

```text
A controlled rule-based operational recommendation engine.
```

The engine should remain:

- deterministic
- rule-driven
- explainable
- evidence-backed
- operationally safe
- confidence-aware

The engine should NOT:

- behave like a chatbot
- invent agronomic diagnoses
- generate unsupported product claims
- hide rule triggers
- modify priority scores
- trigger anomaly escalation

Its responsibility is ONLY:

```text
Convert contextual signals into structured next-best actions.
```

---

# 5. Input Dependencies

This build consumes outputs from previous builds:

| Input | Source Build |
|---|---|
| `priority_rankings.csv` | Build 03 |
| `priority_score_breakdown.csv` | Build 03 |
| `contextual_feature_view.csv` | Build 02 |
| `priority_feature_view.csv` | Build 02 |
| controlled decision rules | Build 04 config/rules |

Inputs must already be validated and deterministic.

---

# 6. Expected Outputs

This build should produce structured outputs such as:

| Output | Purpose |
|---|---|
| `recommendation_outputs.csv` | Next-best-action records |
| `recommendation_trace_log.csv` | Matched rules, evidence, and confidence trace |
| `decision_rule_validation_report.csv` | Rule/config validation results |

Each recommendation record should preserve:

- `entity_id`
- `rep_id`, where available
- `territory_id`
- `priority_score`
- `priority_level`
- `risk_or_opportunity`
- `recommended_actions`
- `recommended_product_category`
- `confidence_level`
- `matched_rule_ids`
- `evidence_signals`

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
backend/engines/contextual_decision_engine.py
backend/engines/recommendation_engine.py
backend/engines/advisory_engine.py
backend/engines/action_selector.py
backend/rules/
backend/config/decision_thresholds.yaml
datasets/processed/
tests/
docs/implementation/
```

---

# 8. Forbidden File Scope

This build must not modify:

```text
private-data/
backend/data/
backend/pipelines/
backend/features/
backend/anomaly/
backend/explainability/
backend/learning/
backend/api/
frontend/
docs/architecture/
docs/implementation_contracts/
```

Architecture and contract docs may only be changed if the human explicitly requests a documentation revision.

---

# 9. Rule Requirements

Rules must be controlled and inspectable.

Recommended rule categories:

- agronomic action rules
- inventory action rules
- sales opportunity rules
- relationship follow-up rules
- competitive response rules

Rules should define:

| Field | Purpose |
|---|---|
| `rule_id` | Stable rule identifier |
| `rule_type` | Agronomic, inventory, sales, relationship, competitive |
| `conditions` | Required feature thresholds or categorical matches |
| `risk_or_opportunity` | Inferred context label |
| `recommended_actions` | Structured action list |
| `recommended_product_category` | Broad product category only |
| `confidence_level` | High, Medium, or Low |
| `evidence_fields` | Input fields supporting the rule |

---

# 10. Safety Rules

The engine must use cautious operational language.

Allowed:

```text
Possible fungal disease risk
Possible stock-out risk
High inventory replenishment need
Competitive pressure detected
```

Forbidden:

```text
Crop is infected
Retailer will definitely stock out tomorrow
This product must be purchased
```

The engine may recommend product categories, not unsupported brand claims.

---

# 11. Determinism Requirements

This build must be fully deterministic.

Given identical inputs:

```text
recommendation outputs must remain identical
```

Requirements:

- stable rule ordering
- stable action ordering
- stable confidence assignment
- stable tie-breaking if multiple rules match
- no randomness
- no hidden mutable state
- no free-form generative reasoning

---

# 12. Traceability Requirements

Every recommendation must preserve:

- matched rule ID
- triggering fields
- input feature values used
- risk/opportunity label
- action list
- confidence level

If no rule matches, the engine must produce an explicit operational warning or a structured no-recommendation record.

Avoid silent fallbacks.

---

# 13. Error Handling Requirements

Preferred errors:

```text
ERROR:
Missing contextual_feature_view column: inventory_need_score
```

```text
WARNING:
No contextual decision rule matched entity_id=ENT004
```

Avoid:

- silent recommendation generation
- hidden default recommendations
- swallowed validation errors
- schema mutation

---

# 14. Expected Tests

Tests should validate:

- rule matching
- deterministic outputs
- confidence assignment
- no unsupported diagnosis language
- missing required input fields
- no-match behavior
- output schema stability
- action ordering stability
- product category constraints
- trace metadata completeness

---

# 15. Definition of Done

Build 04 is complete only when:

- contextual rules are defined and inspectable
- recommendation engine logic is deterministic
- next-best-action outputs are structured
- confidence levels are rule-driven
- matched-rule metadata is preserved
- evidence fields are preserved for explainability
- no human-readable explanation engine is implemented here
- no priority scoring is implemented here
- no anomaly detection is implemented here
- no API/frontend code is modified
- no unsupported agronomic certainty claims exist
- tests validate rule matching and output stability

---

# 16. Completion Checklist

## Inputs

- [ ] priority outputs from Build 03 are available
- [ ] contextual feature view from Build 02 is available
- [ ] required fields are validated
- [ ] missing inputs produce explicit errors

## Rule System

- [ ] agronomic rules exist
- [ ] inventory rules exist
- [ ] sales opportunity rules exist
- [ ] relationship rules exist
- [ ] competitive response rules exist
- [ ] all rules have stable `rule_id`
- [ ] all rules define evidence fields
- [ ] all rules define confidence level

## Recommendation Outputs

- [ ] `recommendation_outputs.csv` is generated or ready to generate
- [ ] `recommendation_trace_log.csv` is generated or ready to generate
- [ ] output schema is stable
- [ ] action order is stable
- [ ] confidence labels are valid
- [ ] product categories are broad and supported

## Architecture Compliance

- [ ] no scoring logic added
- [ ] no anomaly logic added
- [ ] no explanation text engine added
- [ ] no outcome learning added
- [ ] no API/frontend changes added
- [ ] only allowed files were modified

## Testing

- [ ] rule-match tests pass
- [ ] no-match behavior tests pass
- [ ] deterministic output tests pass
- [ ] schema stability tests pass
- [ ] safety language tests pass

---

# 17. Review Checklist

Before accepting Build 04, review:

| Question | Expected Answer |
|---|---|
| Did this build modify only allowed files? | Yes |
| Are recommendations deterministic? | Yes |
| Are matched rules traceable? | Yes |
| Are evidence fields preserved? | Yes |
| Are confidence levels interpretable? | Yes |
| Did the engine avoid diagnosis certainty? | Yes |
| Did it avoid priority scoring? | Yes |
| Did it avoid anomaly detection? | Yes |
| Did it avoid explanation generation? | Yes |

---

# 18. Build 04 Final Statement

Build 04 is successful when KshetraAI can deterministically convert prioritized contextual signals into safe, structured, traceable next-best-action recommendations without introducing scoring, anomaly detection, explanation generation, or frontend/API behavior.
