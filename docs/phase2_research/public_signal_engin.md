````markdown id="u8y7pf"
# AI-Guided Agricultural Signal Intelligence Layer — Final MVP Architecture

# 1. System Objective

Build an AI-driven agricultural signal intelligence layer that converts:

- satellite imagery
- weather data
- crop calendars
- pest advisories
- historical crop behavior

into:

```text
contextual agricultural intelligence signals
```

These signals are then consumed by downstream systems for:

- field-force prioritization
- next best action recommendation
- campaign timing
- territory ranking
- anomaly detection
- agronomic advisory

---

# 2. Core Philosophy

The system should NOT rely on fixed thresholds like:

```text
NDVI < 0.4 = bad
```

Instead:

```text
Observed behavior
vs
Expected behavior for that crop and stage
```

This creates:
- crop-awareness
- stage-awareness
- regional awareness
- temporal awareness

---

# 3. Public Data Sources

| Signal | Source |
|---|---|
| NDVI | Sentinel-2 |
| NDWI | Sentinel-2 |
| LST | MODIS LST |
| Rainfall | IMD / CHIRPS / GPM |
| Crop Calendar | Public agronomic calendars |
| Pest Advisories | Government pest surveillance bulletins |
| Administrative Boundaries | Tehsil/District shapefiles |

---

# 4. Spatial Aggregation Layer

Tehsil boundaries are used to:

- clip satellite imagery
- aggregate observations
- generate territory-level intelligence

Flow:

```text
Raw imagery
    ↓
Clip by tehsil polygon
    ↓
Aggregate statistics
    ↓
Tehsil-level observations
```

---

# 5. Core Satellite Signal Roles

## NDVI

Represents:
- vegetation vigor
- greenness
- biomass development

---

## NDWI

Represents:
- crop moisture condition
- drying tendency
- water stress

---

## LST

Represents:
- thermal condition
- heat stress
- abnormal surface heating

---

## Rainfall

Represents:
- environmental water availability
- rainfall anomaly
- drought context

---

# 6. Crop-Type Awareness

Signals are crop-relative.

Example:

```text
NDVI = 0.55
```

may mean:
- healthy for wheat
- weak for rice
- acceptable for cotton

Therefore:

```text
Crop type determines interpretation logic.
```

Initial MVP crops:

- Rice
- Wheat
- Cotton

---

# 7. Crop-Stage Awareness

Crop stage determines:

```text
What biological behavior should be expected right now.
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
| Sowing | Low |
| Vegetative | Rising/High |
| Flowering | Stable-High |
| Maturity | Declining |
| Harvest | Low/Declining |

Important:

```text
Same signal value can mean different things at different stages.
```

---

# 8. Crop Calendar Logic

The system determines stage using:

```text
crop
+
season
+
current week/date
```

Example:

```text
Rice + Kharif + Week 32
→ Vegetative stage
```

---

# 9. Crop Expectation Tables

For each crop-stage combination, define:

- NDVI expected behavior
- NDWI expected behavior
- LST sensitivity
- Rainfall sensitivity

Example — Rice Vegetative Stage:

| Signal | Expected Behavior |
|---|---|
| NDVI | Rising / High |
| NDWI | High |
| LST Sensitivity | High |
| Rainfall Sensitivity | High |

These are:

```text
Biological expectation descriptors
```

NOT statistical thresholds.

---

# 10. Historical Baseline Layer

Purpose:

```text
Convert biological expectations into localized statistical ranges.
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

because agricultural satellite data is noisy.

---

# 11. Statistical Labeling Layer

Current values are converted into statistical labels.

## Final Labels

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
Statistical position labels
```

NOT:
- health labels
- stress labels

---

# 12. Internal Mapping Logic

Crop-stage expectations are internally mapped to:

```text
Allowed statistical labels
```

Example:

## Rice + Vegetative Stage

Expected:

```text
NDVI should be Rising / High
```

Internal mapping:

```text
Allowed NDVI labels:
[Normal, High-Normal, Very High]
```

---

## Rice + Harvest Stage

Expected:

```text
NDVI should be Low / Declining
```

Internal mapping:

```text
Allowed NDVI labels:
[Very Low, Low-Normal]
```

---

# 13. Core Inference Logic

## Baseline Layer Produces

```text
Current statistical labels
```

Example:

```text
NDVI = Very Low
```

---

## Crop Tables Provide

```text
Allowed labels
```

Example:

```text
[Normal, High-Normal, Very High]
```

---

## Engine Checks

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

---

# 14. Trend / Time-Series Layer

Purpose:

```text
Detect worsening or improving behavior over time.
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

# 15. Trend Interpretation Logic

Trend must be interpreted with crop stage.

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

# 16. Signal-Level Anomaly Flags

The system creates anomaly flags for each signal.

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

## Trend anomaly

```text
Observed trend contradicts expected stage behavior
```

Example:

```text
Vegetative stage expects NDVI rising
but NDVI trend = Falling
```

---

# 17. Scoring Engine

The inference engine aggregates anomaly flags into a stress score.

## Final Scoring Logic

| Component | Score |
|---|---:|
| NDVI anomaly | +2 |
| NDWI anomaly | +2 |
| LST anomaly | +2 |
| Rainfall anomaly | +1 |
| Worsening trend | +1 |

Rationale:

- NDVI / NDWI / LST are primary crop-condition signals
- Rainfall is contextual driver signal
- Trend acts as confirmation signal

---

# 18. Final Stress Levels

| Total Score | Stress Level |
|---:|---|
| 0–1 | Healthy |
| 2–3 | Watchlist |
| 4–5 | Moderate Stress |
| 6–8 | High Stress |

---

# 19. Example End-to-End Inference

## Context

```text
Crop = Rice
Stage = Vegetative
```

Expected:

```text
NDVI → Rising/High
NDWI → High
LST → Not High
Rainfall → Adequate
```

---

## Current Statistical Labels

| Signal | Label |
|---|---|
| NDVI | Very Low |
| NDWI | Very Low |
| LST | Very High |
| Rainfall | Very Low |

---

## Trend

| Signal | Trend |
|---|---|
| NDVI | Falling |
| NDWI | Falling |
| LST | Rising |
| Rainfall | Deficient |

---

## Scoring

| Component | Score |
|---|---:|
| NDVI anomaly | +2 |
| NDWI anomaly | +2 |
| LST anomaly | +2 |
| Rainfall anomaly | +1 |
| Worsening trend | +1 |

Total:

```text
8
```

---

## Final Inference

```text
High Stress
```

Reason:

```text
Possible moisture + heat stress
during active vegetative growth stage.
```

---

# 20. Final MVP Intelligence Signals

## A. Crop Health Signal

### Built From
- NDVI
- NDWI
- LST
- Rainfall
- Crop stage
- Trend analysis

### Output
- Healthy
- Watchlist
- Moderate Stress
- High Stress

### Business Value
- prioritize stressed territories
- improve field-force targeting
- improve agronomic recommendation relevance

---

## B. Moisture Stress Signal

### Built From
- NDWI
- Rainfall
- LST

### Scoring Logic

| Condition | Score |
|---|---:|
| NDWI anomaly | +2 |
| Rainfall deficit | +1 |
| LST rising/high | +1 |

### Output

| Score | Signal |
|---:|---|
| 0–1 | Normal |
| 2–3 | Emerging Moisture Stress |
| 4+ | Severe Moisture Stress |

### Business Value
- support irrigation/nutrient campaigns
- identify drought-sensitive territories
- improve farmer advisory quality

---

## C. Heat Stress Signal

### Built From
- LST
- Crop stage

### Scoring Logic

| Condition | Score |
|---|---:|
| LST anomaly | +2 |
| Heat-sensitive stage | +1 |
| Rising LST trend | +1 |

### Output

| Score | Signal |
|---:|---|
| 0–1 | Normal |
| 2–3 | Heat Risk |
| 4+ | Severe Heat Stress |

### Business Value
- prioritize heat-sensitive territories
- support stage-sensitive interventions

---

## D. Pest / Disease Risk Signal

### Built From
- government pest bulletins
- crop stage
- weather conditions
- unexplained vegetation anomalies

### Scoring Logic

| Condition | Score |
|---|---:|
| Pest bulletin active | +2 |
| NDVI anomaly without drought explanation | +2 |
| Sensitive crop stage | +1 |
| Humidity/rainfall favorable | +1 |

### Output

| Score | Signal |
|---:|---|
| 0–1 | Normal |
| 2–3 | Pest Watch |
| 4+ | Possible Pest/Disease Risk |

### Business Value
- prioritize fungicide/insecticide campaigns
- identify regions requiring field verification
- improve outbreak responsiveness

Important:

```text
This is a risk signal, not confirmed pest detection.
```

---

## E. Campaign Timing Signal

### Built From
- crop stage
- weather context
- pest advisories

### Logic

| Condition | Output |
|---|---|
| Crop too early | Too Early |
| Crop at ideal stage | Right Window |
| Crop past effective stage | Late Window |
| Pest/weather urgency active | Urgent Window |

### Business Value
- avoid premature campaigns
- improve campaign conversion
- improve recommendation timing

---

## F. Territory Priority Signal

### Built From
- crop health score
- moisture stress
- heat stress
- pest risk
- campaign timing

### Priority Scoring

| Component | Score |
|---|---:|
| High crop stress | +3 |
| Pest risk active | +3 |
| Moisture stress | +2 |
| Heat stress | +2 |
| Urgent campaign window | +2 |
| Recovery trend | -1 |

### Output

| Score | Priority |
|---:|---|
| 0–2 | Low Priority |
| 3–5 | Medium Priority |
| 6–8 | High Priority |
| 9+ | Urgent Priority |

### Business Value
- optimize field-force movement
- improve revenue per field day
- improve coverage efficiency
- focus effort where intervention probability is highest

---

# 21. Final System Positioning

This system is NOT:

```text
an NDVI dashboard
```

It is:

```text
An AI-driven Agricultural Signal Intelligence Layer
for downstream field-force decision optimization.
```

The downstream decision engine can consume these signals for:

- dynamic visit prioritization
- next best action recommendation
- campaign planning
- anomaly response
- explainable field intelligence
````
