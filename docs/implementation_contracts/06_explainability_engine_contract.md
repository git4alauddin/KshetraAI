# KshetraAI — Explainability Engine Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the Explainability Engine.

The Explainability Engine is responsible for:

```text
Converting intelligence outputs
into transparent, evidence-backed,
human-understandable operational reasoning.
```

This engine determines:

```text
Why the system generated a particular score,
alert, recommendation, or operational action.
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Explainability Engine |
| Layer | Trust & Transparency Layer |
| Primary Responsibility | Generate explainable reasoning |
| Upstream Dependencies | Priority Engine, Contextual Engine, Anomaly Engine |
| Downstream Consumers | Dashboard, APIs, Mobile App |
| Architecture Criticality | High |

---

# 3. Core Philosophy

The Explainability Engine should remain:

- evidence-driven
- deterministic
- interpretable
- traceable
- operationally understandable

The engine should NOT:

- generate new intelligence
- perform anomaly detection
- perform scoring
- infer new business logic
- modify recommendations
- recalibrate learning weights

Its responsibility is ONLY:

```text
Explain existing intelligence outputs.
```

---

# 4. Responsibilities

The Explainability Engine IS responsible for:

- signal attribution
- evidence mapping
- rule traceability
- confidence communication
- operational explanation generation
- structured reasoning generation
- recommendation transparency

---

# 5. Non-Responsibilities

The Explainability Engine is NOT responsible for:

- priority scoring
- recommendation generation
- anomaly detection
- business rule inference
- frontend rendering
- API route handling
- learning optimization

These belong to upstream intelligence modules.

---

# 6. Core Explainability Philosophy

The engine should operate using:

```text
Signals
        ↓
Matched Rules
        ↓
Operational Reasoning
        ↓
Human-Readable Explanation
```

The engine should NOT:

```text
Invent unsupported reasoning.
```

---

# 7. Primary Explainability Categories

| Category | Purpose |
|---|---|
| Priority Explainability | Why an entity was prioritized |
| Recommendation Explainability | Why an action was suggested |
| Anomaly Explainability | Why an alert was triggered |
| Confidence Explainability | Why confidence is high/medium/low |
| Evidence Explainability | Which signals contributed |

---

# 8. Expected Inputs

Inputs originate from:

- priority engine outputs
- contextual engine outputs
- anomaly engine outputs
- matched rules
- feature scores

---

# Example Input

```json
{
  "entity_id": "ENT001",

  "priority_score": 83.7,

  "weather_risk_score": 85,
  "pest_disease_risk_score": 90,
  "crop_stage_risk_score": 80,

  "matched_rule": "COTTON_FUNGAL_RISK_01",

  "recommended_actions": [
    "Inspect crop symptoms",
    "Discuss fungicide advisory"
  ],

  "confidence_level": "High"
}
```

---

# 9. Expected Outputs

The engine outputs:

- structured explanation
- evidence summary
- operational reasoning
- confidence explanation
- recommendation trace

---

# Example Output

```json
{
  "entity_id": "ENT001",

  "explanation": "Cotton crops in this region are currently in a vulnerable flowering stage. Recent rainfall and humidity conditions increase fungal disease risk. NDVI stress signals also indicate possible crop stress. A fungicide advisory discussion is recommended.",

  "evidence": [
    "High rainfall in last 7 days",
    "High humidity",
    "NDVI stress detected",
    "Cotton flowering stage"
  ],

  "confidence_level": "High"
}
```

---

# 10. Explainability Generation Philosophy

The engine should generate:

```text
Grounded operational reasoning.
```

NOT:

```text
Creative or speculative narratives.
```

---

# 11. Priority Explainability Logic

# Purpose

Explain:

```text
Why this entity was ranked highly.
```

---

# Example Inputs

- high agronomic urgency
- high inventory need
- high sales opportunity

---

# Example Output

```text
This retailer was prioritized due to elevated pest-related crop risk,
low fungicide inventory,
and strong seasonal sales opportunity.
```

---

# 12. Recommendation Explainability Logic

# Purpose

Explain:

```text
Why a recommendation was generated.
```

---

# Example Inputs

- matched agronomic rule
- contextual signals
- operational conditions

---

# Example Output

```text
High rainfall and humidity increase fungal disease risk for cotton crops currently in the flowering stage.
```

---

# 13. Anomaly Explainability Logic

# Purpose

Explain:

```text
Why an alert was triggered.
```

---

# Example Inputs

- current vs baseline comparison
- threshold breach
- trend escalation

---

# Example Output

```text
Inventory levels are significantly below the normal baseline while fungicide demand is increasing rapidly.
```

---

# 14. Confidence Explainability Logic

# Purpose

Explain:

```text
Why confidence is high/medium/low.
```

---

# Example Logic

| Confidence | Interpretation |
|---|---|
| High | Multiple aligned strong signals |
| Medium | Partial supporting evidence |
| Low | Weak or incomplete evidence |

---

# Example Output

```text
Confidence is high because multiple agronomic and inventory signals strongly support the recommendation.
```

---

# 15. Evidence Mapping Rules

Every explanation should preserve:

- triggering signals
- matched rules
- contributing features
- contextual evidence

Avoid unsupported claims.

---

# 16. Human-Readable Explanation Rule

Generated explanations should remain:

- concise
- operationally understandable
- field-rep friendly
- evidence-backed

Avoid:

- academic language
- excessive technical jargon
- speculative wording

---

# 17. Important Safety Rule

The engine MUST preserve:

```text
Operational uncertainty.
```

Correct:

```text
Possible fungal disease risk detected.
```

Incorrect:

```text
Crop is definitely infected.
```

---

# 18. Template-Based Generation Rule

The engine should initially use:

```text
Structured explanation templates.
```

NOT:

```text
Uncontrolled generative free-text reasoning.
```

Reason:

- safer demos
- deterministic outputs
- explainability consistency
- operational safety

---

# 19. Allowed File Ownership

The AI MAY modify:

```text
backend/explainability/
backend/config/explanation_templates.yaml
backend/config/confidence_rules.yaml
```

---

# 20. Forbidden File Ownership

The AI MUST NOT modify:

```text
backend/engines/priority_engine.py
backend/anomaly/
frontend/
contracts/
architecture_docs/
```

unless explicitly instructed.

---

# 21. Recommended Folder Structure

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

# 22. Template Configuration Rule

Templates should remain configurable.

Preferred:

```text
backend/config/explanation_templates.yaml
```

Avoid:

```text
hardcoded explanation text scattered across files
```

---

# 23. Deterministic Generation Rule

The engine MUST remain:

```text
Fully deterministic.
```

Given identical inputs:

```text
explanations must remain identical.
```

Avoid:

- randomness
- uncontrolled generative text
- dynamic speculative phrasing

---

# 24. Explainability Preservation Rule

Every explanation MUST preserve:

- traceability
- operational grounding
- evidence alignment
- confidence visibility

Avoid:

```text
hallucinated reasoning
```

---

# 25. Logging Requirements

The engine should log:

- generated explanations
- matched templates
- evidence mappings
- confidence generation

Example:

```text
INFO:
Generated explanation for ENT001 using template AGRI_RISK_TEMPLATE_01
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
No explanation template found for anomaly type STOCKOUT_RISK
```

Avoid silent explanation fallback.

---

# 27. Schema Stability Rule

The engine MUST preserve:

- explanation schema
- confidence labels
- evidence structure

The AI MUST NOT:

- silently alter output formats
- rename confidence categories
- invent undocumented fields

---

# 28. API Independence Rule

The engine should remain:

```text
Pure explainability intelligence.
```

The engine MUST NOT contain:

- HTTP logic
- frontend rendering
- dashboard formatting
- API routing

---

# 29. Allowed Dependencies

Allowed:

```text
pandas
typing
yaml
dataclasses
```

---

# 30. Forbidden Dependencies

Avoid:

```text
uncontrolled LLM generation
heavy generative frameworks
opaque summarization systems
```

unless explicitly requested later.

---

# 31. Testing Requirements

The engine should be testable for:

- deterministic explanations
- evidence mapping
- confidence consistency
- template selection
- schema consistency
- operational safety

---

# 32. Anti-Drift Rules

The AI MUST NOT:

- generate new intelligence
- redesign scoring logic
- create new business rules
- trigger anomalies
- modify recommendations

The engine should remain:

```text
Pure explainability and trust infrastructure.
```

---

# 33. Example Processing Flow

```text
Signals + Rules + Scores
        ↓
Evidence Mapping
        ↓
Template Selection
        ↓
Confidence Mapping
        ↓
Human-Readable Explanation
```

---

# 34. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Are explanations deterministic? | Yes/No |
| Are explanations evidence-backed? | Yes/No |
| Is operational safety preserved? | Yes/No |
| Are confidence levels interpretable? | Yes/No |
| Are templates configurable? | Yes/No |
| Is scope respected? | Yes/No |

---

# 35. Final One-Line Definition

```text
A deterministic evidence-driven explainability engine
that converts agricultural operational intelligence
into transparent, human-understandable,
and trustworthy reasoning outputs.
```