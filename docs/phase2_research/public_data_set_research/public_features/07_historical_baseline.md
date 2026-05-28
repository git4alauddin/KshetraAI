# Historical Baseline Feature

## Quick Brief

Historical baseline defines the expected behavior of a public-data feature for a given crop, geography, crop stage, and time period.

For KshetraAI, historical baseline is the foundation for dynamic thresholds.

It helps avoid fixed rules like:

```text
NDVI < 0.4 = bad
```

Instead, the system should compare:

```text
current observation
vs
expected behavior for the same crop + stage + geography + season/week
```

---

## Why Historical Baseline Matters

Public features vary naturally by:

- crop
- crop stage
- geography
- season
- rainfall zone
- satellite source
- observation quality

So a single universal threshold is risky.

Example:

```text
NDVI = 0.45
```

may be:

- normal during sowing
- concerning during vegetative growth
- normal during harvest
- weak for one crop but acceptable for another

Historical baseline makes interpretation contextual and explainable.

---

## Features That Use Historical Baseline

Historical baseline should support:

- NDVI
- NDWI
- LST
- rainfall
- trend thresholds

It may later support other repeated public features.

---

## Preferred Baseline Key

Most specific preferred key:

```text
geography + crop + crop_stage + week_or_season + feature_name
```

Example:

```text
Ludhiana_T004 + wheat + vegetative_tillering + week_08 + NDVI
```

This lets the system ask:

```text
What is normal NDVI here, for this crop, at this stage, around this time?
```

---

## Baseline Key Fallback Hierarchy

Use the most specific reliable baseline available.

| Priority | Baseline Key | Use |
|---:|---|---|
| 1 | geography + crop + crop_stage + week + feature | Best option |
| 2 | geography + crop + crop_stage + season + feature | Good option |
| 3 | district + crop + crop_stage + week/season + feature | Geography fallback |
| 4 | crop + crop_stage + week/season + feature | Crop-stage fallback |
| 5 | geography + week/season + feature | Geography-only fallback |
| 6 | feature-level global fallback | MVP fallback only |

Fallbacks should lower baseline confidence.

---

## Recommended Baseline Statistics

Use robust statistics instead of mean/std when possible.

| Statistic | Meaning |
|---|---|
| `median` | Typical expected value |
| `p20` | Lower expected range |
| `p80` | Upper expected range |
| `sample_count` | Number of observations used |
| `valid_year_count` | Number of seasons/years represented |
| `baseline_source_window` | Historical period used |

Why median and percentiles:

- satellite and weather data can be noisy
- outliers are common
- crop conditions vary across years
- median/p20/p80 are easier to explain

---

## Statistical Labeling From Baseline

Each current observation can be labeled by comparing it to baseline.

| Label | Logic |
|---|---|
| `Very Low` | current value below p20 |
| `Low-Normal` | current value between p20 and median |
| `Normal` | current value close to median |
| `High-Normal` | current value between median and p80 |
| `Very High` | current value above p80 |

Important:

```text
These are statistical-position labels.
```

They are not automatically health/stress labels.

---

## Anomaly Calculation

Recommended anomaly fields:

| Field | Logic |
|---|---|
| `value_anomaly` | current value minus baseline median |
| `value_ratio` | current value divided by baseline median, when meaningful |
| `baseline_label` | Very Low, Low-Normal, Normal, High-Normal, Very High |
| `outside_expected_range_flag` | true when current value is outside allowed labels for crop stage |

Example:

```text
current_ndvi = 0.48
baseline_median_ndvi = 0.62
ndvi_anomaly = -0.14
```

---

## Trend Threshold Derivation

Historical baseline should also help set trend thresholds.

For each:

```text
geography + crop + crop_stage + feature
```

calculate historical observation-to-observation changes.

Example:

```text
delta = value_t - value_t-1
delta_pct = (value_t - value_t-1) / value_t-1
```

Then derive:

| Field | Meaning |
|---|---|
| `typical_abs_change` | Median absolute change |
| `p80_abs_change` | Upper normal movement threshold |
| `positive_trend_threshold` | Threshold for meaningful rise |
| `negative_trend_threshold` | Threshold for meaningful fall |

This avoids using the same trend threshold for every crop/geography/stage.

---

## Minimum Data Requirements

Baseline reliability depends on data volume.

Recommended checks:

| Check | Meaning |
|---|---|
| `sample_count` | Enough observations for the baseline |
| `valid_year_count` | Enough years/seasons represented |
| `valid_scene_count` | Enough satellite scenes after quality filtering |
| `missing_rate` | Missing data not too high |
| `quality_pass_rate` | Enough observations pass quality checks |

Exact minimums can be finalized during implementation after reviewing available data coverage.

---

## Baseline Confidence

Each baseline should produce a confidence level.

| Confidence | Meaning |
|---|---|
| `high` | Specific key available with enough clean observations |
| `medium` | Some fallback used or moderate data coverage |
| `low` | Broad fallback or limited observations |
| `unknown` | Baseline not reliable enough |

Signals should lower confidence when baseline confidence is low.

---

## Baseline Output Fields

Recommended baseline fields:

| Field | Meaning |
|---|---|
| `baseline_id` | Unique baseline record identifier |
| `feature_name` | NDVI, NDWI, LST, rainfall, etc. |
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop context |
| `crop_stage` | Crop stage context |
| `week_or_season` | Time context |
| `median_value` | Typical expected value |
| `p20_value` | Lower expected range |
| `p80_value` | Upper expected range |
| `sample_count` | Number of observations used |
| `valid_year_count` | Number of years/seasons represented |
| `baseline_confidence_level` | High, medium, low, or unknown |
| `baseline_fallback_level` | Which fallback key was used |
| `baseline_source_window` | Historical period used |

---

## How Signals Use Historical Baseline

### Crop Health Signal

Uses baseline to decide whether NDVI, NDWI, LST, and rainfall are behaving as expected for crop/stage/geography.

### Moisture Stress Signal

Uses baseline to identify whether NDWI and rainfall are below expected levels and whether LST is above expected levels.

### Heat Stress Signal

Uses baseline to identify whether LST is high for the current crop/stage/geography.

### Pest / Disease Risk Signal

May use baseline to identify unexplained vegetation anomalies that support pest/disease risk evidence.

---

## Explainability Example

```text
NDVI was labeled Very Low because the current value is below the historical p20
for this crop, stage, geography, and week. The baseline confidence is high
because enough valid historical observations were available.
```

---

## Current Caution

Historical baseline improves threshold quality, but it is only as reliable as the data behind it.

If baseline coverage is weak, the system should:

- lower confidence
- use broader fallback carefully
- avoid strong claims
- show that fallback logic was used
