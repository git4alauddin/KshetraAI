# Build 05 — Anomaly & Opportunity Detection Engine

---

# 1. Build Objective

The purpose of this build is to implement the deterministic anomaly and opportunity detection layer that identifies unusual operational, agricultural, commercial, inventory, and competitive events requiring field attention.

This build converts:

```text
Historical baselines + current operational signals
```

into:

```text
Explainable anomaly alerts and opportunity signals.
```

The engine should determine:

- what changed unexpectedly
- whether the change is operationally meaningful
- how severe the anomaly/opportunity is
- which field action should be escalated downstream

This build does not implement:

- final priority scoring
- contextual next-best-action generation
- human-readable explanation text
- API routes
- frontend workflows
- autonomous ML anomaly models
- outcome learning recalibration

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/03_anomaly_and_opportunity_detection.md`
- `docs/architecture/05_explainability_and_trust_layer.md`
- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/05_anomaly_detection_engine_contract.md`
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

- Read feature views and historical baseline inputs
- Implement deterministic baseline comparison
- Detect meaningful deviations
- Detect stock-out risks
- Detect demand spikes/drops
- Detect crop-stress escalation
- Detect competitive pressure signals
- Detect operational coverage gaps
- Generate severity scores and classifications
- Generate structured alert outputs
- Preserve anomaly traceability metadata

---

## Out of Scope

- Final priority ranking
- Next-best-action recommendation generation
- Human-readable explanation formatting
- API implementation
- Frontend implementation
- ML-based anomaly modeling
- Autonomous prediction systems
- Outcome learning recalibration

---

# 4. Core Philosophy

The Anomaly & Opportunity Detection Engine should behave as:

```text
A proactive operational monitoring engine.
```

The engine should remain:

- deterministic
- evidence-driven
- threshold-aware
- baseline-aware
- explainable
- operationally interpretable

The engine should NOT:

- behave like an opaque black-box detector
- trigger unexplained alerts
- make guaranteed future claims
- replace human field judgment

Its responsibility is ONLY:

```text
Detect unusual or important deviations
that may require field attention.
```

---

# 5. Input Data Sources

This build consumes outputs from Build 02 and selected historical views.

Expected inputs:

| Input View | Purpose |
|---|---|
| `priority_feature_view.csv` | Current feature signals |
| `contextual_feature_view.csv` | Contextual signal support |
| `anomaly_feature_view.csv` | Current + baseline anomaly features |
| `sales_signals.csv` | POS/demand patterns |
| `inventory_signals.csv` | Stock and stock movement |
| `ndvi_signals.csv` | Crop stress indicators |
| `weather_signals.csv` | Weather risk context |
| `pest_signals.csv` | Pest/disease alert context |
| `visit_history.csv` | Coverage and engagement history |
| `competitor_signals.csv` | Market-pressure context |

---

# 6. Expected Outputs

The engine should generate:

| Output | Purpose |
|---|---|
| `anomaly_alerts.csv` | Structured active alerts |
| `anomaly_trace_log.csv` | Traceability metadata |
| `anomaly_severity_score` | Numerical severity score |
| `severity_level` | Low / Moderate / High / Critical |
| `alert_type` | Type of detected anomaly |
| `supporting_evidence` | Triggering signal evidence |

Outputs should be written to:

```text
datasets/processed/
```

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
backend/anomaly/
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
backend/anomaly/

├── anomaly_engine.py
├── baseline_engine.py
├── deviation_detector.py
├── alert_generator.py
├── severity_classifier.py
└── trend_analyzer.py
```

---

# 10. Detection Philosophy

The engine should primarily compare:

```text
Current signal
        vs
Historical baseline / expected behavior
```

The engine should detect:

```text
Meaningful operational deviation.
```

NOT:

```text
Random numerical fluctuation.
```

---

# 11. Anomaly Categories

Suggested anomaly categories:

| Category | Purpose |
|---|---|
| Agronomic Anomaly | Crop stress, pest, weather abnormality |
| Sales Opportunity | Demand spike or unusual sales growth |
| Sales Risk | Demand drop or regional decline |
| Inventory Risk | Stock depletion / stock-out risk |
| Competitive Event | Competitor pressure escalation |
| Operational Gap | Missed visits / coverage gap |

---

# 12. Agronomic Anomaly Detection

## Purpose

Detect abnormal crop or weather-driven risk.

---

## Example Signals

```text
NDVI drop
High rainfall deviation
High humidity
Pest alert active
Crop stage vulnerability
```

---

## Example Output

```text
Possible crop stress escalation
Severity: High
```

---

# 13. Sales Opportunity Detection

## Purpose

Detect unusual demand growth or commercial opportunity.

---

## Example Signals

```text
sales_last_30d = 48
sales_baseline_30d = 28
sales_growth_percent = 71.4
```

---

## Example Output

```text
Demand spike opportunity
Severity: High
```

---

# 14. Inventory Risk Detection

## Purpose

Detect potential stock-out or inventory imbalance.

---

## Example Signals

```text
current_stock_units = 12
normal_stock_units = 50
sales_velocity_score = 88
```

---

## Example Output

```text
Stock-out risk alert
Severity: Critical
```

---

# 15. Competitive Event Detection

## Purpose

Detect market-defense situations.

---

## Example Signals

```text
competitor_promotion_active = true
regional_sales_drop_score = 72
competitor_availability_score = 80
```

---

## Example Output

```text
Competitive pressure escalation
Severity: High
```

---

# 16. Operational Gap Detection

## Purpose

Detect field execution inefficiencies.

---

## Example Signals

```text
days_since_last_visit = 24
account_importance = high
pending_issue_active = true
```

---

## Example Output

```text
Coverage gap alert
Severity: Moderate
```

---

# 17. Severity Classification Rules

Suggested levels:

| Severity Level | Score Range |
|---|---|
| Critical | 80–100 |
| High | 60–79 |
| Moderate | 40–59 |
| Low | 0–39 |

Thresholds should remain configurable.

---

# 18. Alert Output Structure

Each alert should include:

| Field | Purpose |
|---|---|
| `alert_id` | Unique alert identifier |
| `entity_id` | Related entity |
| `territory_id` | Territory context |
| `alert_type` | Anomaly/opportunity category |
| `severity_score` | Numerical severity |
| `severity_level` | Classification |
| `confidence_level` | Evidence confidence |
| `supporting_evidence` | Signals that triggered alert |
| `detected_at` | Detection timestamp/date |

---

# 19. Example Alert Output

```json
{
  "alert_id": "ALERT001",
  "entity_id": "ENT001",
  "territory_id": "TERR_WARDHA_01",
  "alert_type": "Stock-Out Risk",
  "severity_score": 91,
  "severity_level": "Critical",
  "confidence_level": "High",
  "supporting_evidence": [
    "Current stock is significantly below normal stock",
    "Sales velocity is high",
    "Regional demand is increasing"
  ]
}
```

---

# 20. Anomaly Trace Logging

The engine should preserve trace metadata including:

| Field | Purpose |
|---|---|
| `entity_id` | Entity reference |
| `alert_type` | Detected alert category |
| `current_value` | Current signal value |
| `baseline_value` | Expected/historical value |
| `deviation_value` | Magnitude of deviation |
| `threshold_used` | Configured threshold |
| `triggered_rule` | Rule or detector identifier |
| `severity_score` | Final severity |

---

# 21. Determinism Requirements

This build must remain fully deterministic.

Given identical input datasets and thresholds:

```text
Anomaly outputs must remain identical.
```

Requirements:

- no randomness
- stable threshold use
- stable alert ordering
- stable severity classification
- stable output schemas

---

# 22. Configuration Requirements

Thresholds and severity rules should remain configurable.

Preferred location:

```text
backend/config/
```

Suggested configs:

```text
anomaly_thresholds.yaml
baseline_rules.yaml
severity_rules.yaml
```

Avoid scattered hardcoded constants.

---

# 23. Validation Requirements

The engine must validate:

- required columns exist
- baseline fields exist where required
- no invalid severity scores
- no missing alert identifiers
- anomaly categories are valid
- supporting evidence is non-empty for triggered alerts

Validation failures must remain:

```text
Explicit and operationally understandable.
```

---

# 24. Logging Requirements

The engine should log:

- anomaly detection start/end
- detected alert counts
- severity distribution
- missing baseline warnings
- threshold trigger summaries

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
Missing sales_baseline_30d for ENT004; sales anomaly check skipped.
```

Avoid:

- silent alert suppression
- hidden fallback logic
- silent schema mutation

---

# 26. Output Schema Stability

Generated anomaly outputs should maintain:

- stable column order
- stable naming conventions
- stable severity labels
- stable alert semantics

Anomaly schemas become downstream contracts.

---

# 27. Testing Requirements

Tests should validate:

- deterministic anomaly detection
- baseline comparison correctness
- threshold behavior
- severity classification correctness
- alert schema consistency
- trace metadata preservation
- no alerts generated without evidence

---

# 28. Anti-Drift Rules

This build MUST NOT:

- generate final priority rankings
- generate contextual recommendations
- generate human explanation text
- implement APIs
- introduce ML anomaly models
- redesign architecture
- silently alter schemas

This build is ONLY responsible for:

```text
Deterministic anomaly and opportunity detection infrastructure.
```

---

# 29. Deliverables

Expected outputs:

- anomaly engine modules
- baseline comparison engine
- deviation detector
- severity classifier
- alert generator
- anomaly trace metadata
- configurable threshold files
- deterministic anomaly pipeline
- anomaly validation layer

---

# 30. Completion Criteria

This build is complete when:

- anomaly alerts generate successfully
- severity classification works deterministically
- alert evidence is preserved
- trace logs are generated
- schemas remain stable
- thresholds are configurable
- validation passes successfully
- architecture boundaries remain preserved

---

# 31. Final One-Line Definition

```text
A deterministic anomaly and opportunity detection engine
that compares current operational signals against historical baselines
to generate explainable,
evidence-backed,
and severity-ranked field alerts.
```
