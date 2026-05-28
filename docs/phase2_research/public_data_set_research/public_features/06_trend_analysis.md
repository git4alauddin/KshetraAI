# Trend Analysis Feature

## Quick Brief

Trend analysis identifies whether a public-data feature is improving, stable, or worsening over recent observations.

For KshetraAI, trend analysis helps separate one-time abnormal values from meaningful directional change.

Trend should be interpreted with crop stage. A falling value may be normal in one stage and anomalous in another.

---

## Core Idea

Trend analysis has two steps:

```text
1. Is the change meaningful?
2. Is that meaningful change expected for the current crop stage?
```

Example:

```text
NDVI falling during vegetative stage = possible anomaly
NDVI falling during harvest stage = possibly normal
```

---

## Features That Use Trend

Trend can be calculated for:

- NDVI
- NDWI
- LST
- rainfall

Future features may also use trend if they have repeated observations over time.

---

## Required Inputs

| Input | Requirement |
|---|---|
| Feature values | At least 2-3 valid observations over time |
| Observation dates | Required to order observations |
| Geography | Required for geography-level trend |
| Crop | Required for crop-aware trend interpretation |
| Crop stage | Required for stage-aware trend interpretation |
| Historical variability | Preferred for setting trend thresholds |
| Quality flags | Required to ignore low-confidence observations |

---

## Recommended Trend Window

Recommended MVP trend window:

```text
last 3 valid observations
```

Why:

- one observation is not enough
- two observations can be noisy
- three observations can show direction without becoming too slow

The exact window can later vary by source frequency.

Example:

| Source Type | Possible Trend Window |
|---|---|
| Sentinel-style satellite observation | last 3 valid scenes |
| Weekly aggregated satellite feature | last 3 weeks |
| Daily rainfall | last 7-14 days |
| LST product | last 3 valid observations |

---

## Meaningful Change Threshold

Trend needs a threshold to avoid treating noise as movement.

Avoid universal fixed rules like:

```text
NDVI changed by 5%, so it is rising/falling.
```

Preferred threshold source:

```text
historical variability for geography + crop + crop_stage + feature
```

Example:

```text
normal NDVI week-to-week movement for wheat vegetative stage in a tehsil
```

Then:

```text
if current change is larger than normal variability -> meaningful trend
else -> stable/no meaningful change
```

---

## Trend Threshold Hierarchy

Use the most specific reliable threshold available.

| Priority | Threshold Basis | Use |
|---:|---|---|
| 1 | geography + crop + crop_stage + feature | Best option |
| 2 | crop + crop_stage + feature | Good fallback |
| 3 | crop + feature | Coarser fallback |
| 4 | feature-level global threshold | MVP fallback only |

Fixed thresholds should be treated as fallback values, not final scientific rules.

---

## Trend Classification Logic

For a feature value:

```text
change = latest_value - earlier_value
```

or:

```text
change_pct = (latest_value - earlier_value) / earlier_value
```

Then:

```text
if change > positive_threshold:
    trend = Rising
elif change < negative_threshold:
    trend = Falling
else:
    trend = Stable
```

For rainfall, trend labels may be more context-specific:

```text
Improving
Stable
Deficient
Excessive
```

---

## Crop-Stage-Aware Interpretation

Trend becomes meaningful only after crop-stage interpretation.

Example expectations:

| Crop Stage | NDVI Trend Expectation | NDWI Trend Expectation | LST Trend Concern |
|---|---|---|---|
| Sowing / establishment | Rising over time | Stable or improving | Rising heat may be concerning |
| Vegetative / tillering | Rising / high | Stable or high | Rising heat can add stress concern |
| Flowering / reproductive | Stable-high | Stable or high | Rising heat is more concerning |
| Maturity | Falling may be normal | Falling may be normal | Depends on crop/weather |
| Harvest | Falling is often normal | Falling is often normal | More relevant for operations than crop health |

---

## Trend Anomaly Logic

Trend anomaly occurs when observed trend contradicts expected crop-stage behavior.

Example:

```text
Feature: NDVI
Crop stage: Vegetative
Expected trend: Rising
Observed trend: Falling
Result: trend anomaly
```

Non-anomaly example:

```text
Feature: NDVI
Crop stage: Harvest
Expected trend: Falling
Observed trend: Falling
Result: expected behavior
```

Thermal example:

```text
Feature: LST
Crop stage: Flowering
Observed trend: Rising
Current label: Very High
Result: heat stress evidence strengthens
```

---

## Direction vs Severity

Trend direction and current severity should be kept separate.

Example:

```text
NDVI label = Normal
NDVI trend = Falling
```

This means:

```text
current condition is still normal, but direction is worsening
```

Another example:

```text
NDVI label = Very Low
NDVI trend = Stable
```

This means:

```text
condition is already weak, but not currently worsening
```

Both cases matter differently.

---

## Quality Checks

Trend should be ignored or downgraded when:

- fewer than required valid observations exist
- observations are too far apart
- observations come from mixed sources without normalization
- cloud/quality flags are poor
- crop stage is unknown
- geography changed or boundary mapping is unreliable
- historical threshold is unavailable and fallback threshold is weak

Recommended output should include:

```text
trend_quality_level = high / medium / low
```

---

## Feature Output

Recommended trend feature fields:

| Field | Meaning |
|---|---|
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop context |
| `crop_stage` | Current estimated crop stage |
| `feature_name` | NDVI, NDWI, LST, or rainfall |
| `trend_window` | Number of observations or days/weeks used |
| `latest_value` | Most recent valid feature value |
| `earlier_value` | Earlier value used for comparison |
| `change_value` | Absolute change |
| `change_pct` | Percentage change where applicable |
| `positive_threshold` | Threshold for rising/improving |
| `negative_threshold` | Threshold for falling/declining |
| `trend_label` | Rising, stable, falling, improving, deficient, or excessive |
| `expected_trend_for_stage` | Expected behavior from crop-stage logic |
| `trend_anomaly_flag` | Whether observed trend contradicts crop-stage expectation |
| `trend_quality_level` | High, medium, or low |

---

## Signals That Use Trend Analysis

Trend analysis is used by:

- Crop Health Signal
- Moisture Stress Signal
- Heat Stress Signal

It may also support:

- Pest / Disease Risk Signal
- territory priority context
- explainability outputs

---

## Explainability Example

```text
NDVI is currently within the normal range, but the recent trend is Falling.
Because the crop is in vegetative stage, where NDVI is expected to rise,
this trend is treated as early warning evidence.
```

---

## Current Caution

Trend analysis should not use a universal threshold unless no historical baseline is available.

The preferred design is:

```text
trend threshold from historical variability
+ crop-stage-aware interpretation
```

This avoids overreacting to normal noise or seasonal behavior.
