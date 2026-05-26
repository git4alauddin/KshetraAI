````markdown
# Phase 1 — Finalized Crop Health Engine

# 1. Objective

Build a tehsil-level crop stress intelligence engine that combines:

- satellite indices
- weather context
- crop biology
- crop stage awareness
- historical baselines
- temporal behavior

to infer crop condition.

The engine should NOT rely on raw thresholds alone.

Core philosophy:

```text
Observed behavior
vs
Expected behavior for that crop and stage
```

---

# 2. Finalized Signals

| Signal | Purpose |
|---|---|
| Tehsil Boundary | Spatial analysis unit |
| NDVI | Vegetation vigor / greenness |
| NDWI | Moisture / water condition |
| LST | Heat stress / thermal condition |
| Rainfall | Environmental water context |
| Crop Type | Crop-specific interpretation |
| Crop Stage | Stage-aware interpretation |
| Time-Series Trend | Direction of signal movement |

---

# 3. Tehsil Boundary Layer

Purpose:

- clip satellite imagery
- aggregate statistics
- produce tehsil-level intelligence

Flow:

```text
Raw satellite imagery
    ↓
Clip using tehsil polygon
    ↓
Aggregate mean statistics
    ↓
Tehsil-wise NDVI / NDWI / LST / Rainfall
```

---

# 4. Satellite Signal Roles

## NDVI

Measures:
- crop vigor
- greenness
- biomass development

Meaning:

```text
Higher NDVI generally → healthier vegetation
```

---

## NDWI

Measures:
- moisture condition
- water stress tendency

Meaning:

```text
Lower NDWI → drying/moisture stress
```

---

## LST

Measures:
- surface heat
- thermal stress

Meaning:

```text
Higher LST → higher heat stress risk
```

---

## Rainfall

Provides:
- drought context
- water availability context

Meaning:

```text
Low rainfall + drying signals
→ stronger drought confidence
```

---

# 5. Crop Type Layer

Purpose:

```text
Signals are crop-relative, not universal.
```

Example:

```text
NDVI = 0.55
```

may mean:
- normal for wheat
- weak for rice
- acceptable for cotton

So crop type decides:

```text
Which interpretation rules should be used.
```

Initial crops:

- Rice
- Wheat
- Cotton

---

# 6. Crop Stage Layer

Purpose:

```text
Tell the system what behavior should be expected RIGHT NOW.
```

Stages:

- Sowing
- Vegetative
- Flowering/Reproductive
- Maturity
- Harvest

Example:

| Stage | Expected NDVI |
|---|---|
| Sowing | low |
| Vegetative | rising/high |
| Flowering | high/stable |
| Maturity | declining |
| Harvest | low/declining |

Important:

```text
Same NDVI value can mean different things at different stages.
```

---

# 7. Crop Calendar Logic

Crop calendar determines:

```text
crop + season + current week
→ current crop stage
```

Example:

```text
Rice + Kharif + Week 32
→ Vegetative stage
```

---

# 8. Crop Expectation Tables

These are manually curated agronomic expectation tables.

Purpose:

```text
Describe expected biological behavior.
```

Example — Rice:

| Stage | NDVI | NDWI | LST Sensitivity | Rainfall Sensitivity |
|---|---|---|---|---|
| Sowing | Low/Rising | Medium-High | Medium | High |
| Vegetative | Rising/High | High | High | High |
| Flowering | Stable-High | High | Very High | High |
| Maturity | Declining | Declining | Medium-Low | Medium |
| Harvest | Low/Declining | Low | Low | Low |

Important:

These are NOT statistical thresholds.

They are:

```text
Biological expectation descriptors.
```

---

# 9. Historical Baseline Layer

Purpose:

```text
Convert expectations into localized statistical ranges.
```

For each:

```text
tehsil + crop + stage + week
```

calculate:

- median
- p20
- p80

for:
- NDVI
- NDWI
- LST
- Rainfall

Example:

| Metric | Value |
|---|---|
| median_ndvi | 0.64 |
| p20_ndvi | 0.58 |
| p80_ndvi | 0.70 |

Important:

Use:
- median instead of mean
- percentile spread instead of standard deviation

because satellite/agri data is noisy.

---

# 10. Statistical Labeling Layer

Current values are converted into percentile-relative labels.

## Final labels

| Label | Logic |
|---|---|
| Very Low | below p20 |
| Low-Normal | p20 → median |
| Normal | around median |
| High-Normal | median → p80 |
| Very High | above p80 |

Example:

```text
Current NDVI = 0.44
p20 = 0.58
→ Very Low
```

Important:

These are:

```text
Statistical positioning labels
```

NOT:
- health labels
- stress labels

---

# 11. Internal Mapping Logic

This was the key abstraction finalized.

Crop expectation tables are internally converted into:

```text
Allowed baseline labels
```

Example:

## Rice + Vegetative

Expectation:

```text
NDVI should be Rising/High
```

Internal mapping:

```text
Allowed NDVI labels:
[Normal, High-Normal, Very High]
```

---

## Rice + Harvest

Expectation:

```text
NDVI should be Low/Declining
```

Internal mapping:

```text
Allowed NDVI labels:
[Very Low, Low-Normal]
```

---

# 12. Core Mapping Logic

## Baseline layer gives:

```text
Current statistical label
```

Example:

```text
NDVI = Very Low
```

---

## Crop-stage table provides:

```text
Allowed labels
```

Example:

```text
[Normal, High-Normal, Very High]
```

---

## Inference engine checks:

```text
current_label ∈ allowed_labels ?
```

If YES:

```text
Expected behavior
```

If NO:

```text
Anomaly detected
```

This is the core health-engine abstraction.

---

# 13. Time-Series / Trend Layer

Purpose:

```text
Detect improving or worsening behavior over time.
```

Trend window:

```text
Last 3 observations/weeks
```

Trend labels:

- Rising
- Stable
- Falling

For rainfall:
- Improving
- Stable
- Deficient

---

## Signal-wise trend meaning

| Signal | Worsening Trend |
|---|---|
| NDVI | Falling |
| NDWI | Falling |
| LST | Rising |
| Rainfall | Deficient/decreasing |

---

# 14. Trend Awareness Logic

Trend must be interpreted with stage.

Example:

## Rice Vegetative Stage

Expected:

```text
NDVI rising
```

Observed:

```text
NDVI falling
```

Inference:

```text
Trend anomaly
```

---

## Rice Maturity Stage

Expected:

```text
NDVI declining
```

Observed:

```text
NDVI falling
```

Inference:

```text
Possibly normal
```

---

# 15. Stress Inference Engine

Purpose:

```text
Combine all anomalies into crop-condition intelligence.
```

Inputs:

- NDVI
- NDWI
- LST
- Rainfall
- Crop Type
- Crop Stage
- Historical Baseline
- Trends

---

# 16. Signal-Level Anomalies

## NDVI anomaly

```text
Current NDVI label not allowed
for this crop-stage
```

---

## NDWI anomaly

```text
Current NDWI label not allowed
for this crop-stage
```

---

## LST anomaly

```text
Current LST label not allowed
for this crop-stage
```

---

## Rainfall anomaly

```text
Rainfall below expected range
```

---

# 17. Stress Scoring System

| Component | Score |
|---|---:|
| NDVI anomaly | +2 |
| NDWI anomaly | +2 |
| LST anomaly | +2 |
| Rainfall anomaly | +1 |
| Worsening trend | +1 |

---

# 18. Final Stress Levels

| Total Score | Stress Level |
|---|---|
| 0–1 | Healthy |
| 2–3 | Watchlist |
| 4–5 | Moderate Stress |
| 6–8 | High Stress |

---

# 19. Final Inference Example

Rice + Vegetative Stage

Observed:

- NDVI = Very Low
- NDWI = Very Low
- LST = Very High
- Rainfall = Very Low
- NDVI trend = Falling
- NDWI trend = Falling
- LST trend = Rising

Score:

```text
2 + 2 + 2 + 1 + 1 = 8
```

Final inference:

```text
High Stress
```

Reason:

```text
Possible moisture + heat stress
during active vegetative growth stage.
```

---

# 20. Final System Philosophy

The engine does NOT ask:

```text
Is NDVI low?
```

It asks:

```text
Is the observed behavior
compatible with what this crop
should biologically be doing
at this stage
in this region
during this time?
```

That is the finalized health-engine logic.
````
