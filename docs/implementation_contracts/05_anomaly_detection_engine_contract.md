# KshetraAI — Anomaly Detection Engine Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the Anomaly Detection Engine.

The Anomaly Detection Engine is responsible for:

```text
Detecting unusual, emerging,
or operationally important deviations
in agricultural and commercial signals.
```

This engine determines:

```text
What unusual event requires immediate attention.
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | Anomaly Detection Engine |
| Layer | Core Intelligence Layer |
| Primary Responsibility | Detect anomalies and opportunities |
| Upstream Dependencies | Feature Builder, Historical Signals |
| Downstream Consumers | Dashboard, Explainability Layer, Priority Engine |
| Architecture Criticality | High |

---

# 3. Core Philosophy

The Anomaly Detection Engine should remain:

- deterministic
- explainable
- evidence-driven
- threshold-oriented
- operationally interpretable

The engine should NOT:

- generate final explanations
- perform recommendation ranking
- redesign scoring systems
- recalibrate learning weights
- generate uncontrolled predictions

Its responsibility is ONLY:

```text
Detect and classify unusual operational events.
```

---

# 4. Responsibilities

The Anomaly Detection Engine IS responsible for:

- baseline comparison
- deviation detection
- anomaly severity scoring
- opportunity detection
- alert generation
- operational escalation classification

---

# 5. Non-Responsibilities

The Anomaly Detection Engine is NOT responsible for:

- final prioritization ranking
- next best action generation
- frontend rendering
- API handling
- explanation formatting
- learning recalibration
- weight optimization

These belong to downstream modules.

---

# 6. Core Detection Philosophy

The engine operates using:

```text
Historical baseline
        vs
Current signals
```

The goal is to identify:

```text
Meaningful operational deviation.
```

NOT random statistical noise.

---

# 7. Primary Detection Categories

| Category | Purpose |
|---|---|
| Agronomic Anomalies | Crop/pest/weather abnormalities |
| Sales Anomalies | Demand spikes or drops |
| Inventory Anomalies | Stock-out or depletion risks |
| Competitive Anomalies | Market pressure events |
| Operational Anomalies | Coverage or visit irregularities |

---

# 8. Expected Inputs

Inputs originate from:

- feature builder outputs
- historical baseline tables
- current operational signals
- contextual datasets

---

# Example Input

```json
{
  "entity_id": "ENT001",

  "sales_last_30d": 48,
  "sales_baseline_30d": 28,

  "inventory_current": 12,
  "inventory_normal": 50,

  "ndvi_current": 0.48,
  "ndvi_baseline": 0.62,

  "humidity_percent": 87,
  "rainfall_7d_mm": 112
}
```

---

# 9. Expected Outputs

The engine outputs:

- anomaly type
- anomaly severity
- anomaly score
- operational alert
- supporting evidence

---

# Example Output

```json
{
  "entity_id": "ENT001",

  "anomaly_type": "Stock-Out Risk",

  "severity_level": "Critical",

  "anomaly_score": 91,

  "evidence": [
    "Inventory significantly below baseline",
    "Sales velocity increasing"
  ]
}
```

---

# 10. Baseline Comparison Philosophy

The engine should compare:

```text
Current State
        vs
Expected Normal State
```

NOT isolated raw values.

---

# Examples

Good anomaly logic:

```text
Current sales much higher than normal baseline
→ possible demand spike
```

Bad anomaly logic:

```text
Sales > 40
→ anomaly
```

without context.

---

# 11. Agronomic Anomaly Logic

# Purpose

Detect unusual crop-health-related events.

---

# Example Inputs

- NDVI drop
- rainfall deviation
- humidity spike
- pest alert emergence

---

# Example Outputs

```text
Possible crop stress increase
Possible pest emergence risk
```

---

# 12. Sales Anomaly Logic

# Purpose

Detect unusual commercial changes.

---

# Example Inputs

- sudden sales spike
- unusual demand growth
- regional sales decline

---

# Example Outputs

```text
Demand spike opportunity
Regional sales decline warning
```

---

# 13. Inventory Anomaly Logic

# Purpose

Detect abnormal inventory risk.

---

# Example Inputs

- low inventory
- high sales velocity
- abnormal depletion

---

# Example Outputs

```text
Stock-out risk alert
```

---

# 14. Competitive Anomaly Logic

# Purpose

Detect unusual competitive pressure.

---

# Example Inputs

- competitor promotion
- rapid market share loss
- competitor availability increase

---

# Example Outputs

```text
Competitive pressure escalation
```

---

# 15. Operational Anomaly Logic

# Purpose

Detect operational inefficiencies.

---

# Example Inputs

- missed strategic visits
- coverage gaps
- long engagement gaps

---

# Example Outputs

```text
Coverage gap alert
```

---

# 16. Severity Classification Rules

Suggested V1 classification:

| Score Range | Severity |
|---|---|
| 0–30 | Low |
| 31–60 | Moderate |
| 61–80 | High |
| 81–100 | Critical |

---

# 17. Detection Methods

The engine may use:

- threshold comparison
- percentage deviation
- moving baselines
- rolling averages
- trend analysis

The engine should initially avoid:

- black-box anomaly models
- opaque ML systems
- uncontrolled statistical complexity

---

# 18. Allowed File Ownership

The AI MAY modify:

```text
backend/anomaly/
backend/config/anomaly_thresholds.yaml
backend/config/baselines.yaml
```

---

# 19. Forbidden File Ownership

The AI MUST NOT modify:

```text
backend/engines/priority_engine.py
backend/explainability/
frontend/
contracts/
architecture_docs/
```

unless explicitly instructed.

---

# 20. Recommended Folder Structure

```text
backend/anomaly/

├── anomaly_engine.py
├── baseline_engine.py
├── deviation_detector.py
├── alert_generator.py
├── severity_classifier.py
└── trend_analyzer.py
```

---

# 21. Threshold Configuration Rule

Thresholds should remain configurable.

Preferred:

```text
backend/config/anomaly_thresholds.yaml
```

Avoid:

```text
hardcoded scattered thresholds
```

---

# 22. Deterministic Detection Rule

The engine MUST remain:

```text
Fully deterministic.
```

Given identical inputs:

```text
anomaly outputs must remain identical.
```

Avoid:

- randomness
- hidden state
- unstable thresholds

---

# 23. Explainability Preservation Rule

Every anomaly MUST preserve:

- triggering signals
- baseline comparison
- severity reasoning
- supporting evidence

Avoid:

```text
opaque anomaly detection
```

---

# 24. Important Safety Rule

The engine should infer:

```text
Possible operational risk/opportunity.
```

NOT:

```text
Guaranteed real-world event certainty.
```

Correct:

```text
Possible stock-out risk detected.
```

Incorrect:

```text
Retailer will definitely run out of stock tomorrow.
```

---

# 25. Logging Requirements

The engine should log:

- detected anomalies
- severity levels
- baseline deviations
- triggered thresholds

Example:

```text
INFO:
Stock-out anomaly triggered for ENT001
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
Missing historical baseline for ENT007
```

Avoid silent anomaly suppression.

---

# 27. Schema Stability Rule

The engine MUST preserve:

- anomaly output schemas
- severity labels
- anomaly naming conventions

The AI MUST NOT:

- silently alter alert structures
- rename severity categories
- invent undocumented outputs

---

# 28. API Independence Rule

The engine should remain:

```text
Pure anomaly intelligence logic.
```

The engine MUST NOT contain:

- HTTP handling
- frontend formatting
- dashboard rendering
- API route logic

---

# 29. Allowed Dependencies

Allowed:

```text
pandas
numpy
typing
yaml
statistics
```

---

# 30. Forbidden Dependencies

Avoid:

```text
heavy ML anomaly frameworks
distributed stream engines
uncontrolled predictive systems
```

unless explicitly requested later.

---

# 31. Testing Requirements

The engine should be testable for:

- threshold correctness
- baseline comparison
- deterministic outputs
- severity classification
- anomaly schema consistency
- evidence generation

---

# 32. Anti-Drift Rules

The AI MUST NOT:

- generate recommendations
- generate explanations
- redesign scoring logic
- recalibrate weights
- merge responsibilities with other engines

The engine should remain:

```text
Pure anomaly and opportunity intelligence.
```

---

# 33. Example Processing Flow

```text
Historical Baseline
        +
Current Signals
        ↓
Deviation Detection
        ↓
Anomaly Scoring
        ↓
Severity Classification
        ↓
Alert Generation
```

---

# 34. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Are outputs deterministic? | Yes/No |
| Are anomalies evidence-driven? | Yes/No |
| Are thresholds configurable? | Yes/No |
| Are severity levels interpretable? | Yes/No |
| Is explainability preserved? | Yes/No |
| Is scope respected? | Yes/No |

---

# 35. Final One-Line Definition

```text
A deterministic explainable deviation-detection engine
that identifies unusual agricultural,
commercial, inventory,
and operational events requiring field attention.
```