# NDVI Feature

## Quick Brief

NDVI means Normalized Difference Vegetation Index.

It is a satellite-derived vegetation index used to estimate vegetation greenness, crop vigor, and biomass development.

For KshetraAI, NDVI should be used as a crop-health context feature, not as a standalone proof of crop damage.

---

## Formula

```text
NDVI = (NIR - Red) / (NIR + Red)
```

Where:

| Term | Meaning |
|---|---|
| `NIR` | Near-infrared reflectance. For Sentinel-2, use Band 8 (`B08`). |
| `Red` | Red band reflectance. For Sentinel-2, use Band 4 (`B04`). |

Healthy vegetation usually reflects more near-infrared light and absorbs more red light, which results in higher NDVI.

---

## Required Inputs

| Input | Requirement |
|---|---|
| Satellite imagery | Multispectral imagery with Red and NIR bands |
| Red band | Required for formula |
| NIR band | Required for formula |
| Acquisition date | Required for time-series and crop-stage matching |
| Geography | Required for tehsil/district aggregation |
| Cloud/quality flag | Required to avoid using bad observations |

---

## What NDVI Represents

NDVI can help describe:

- vegetation greenness
- crop vigor
- biomass development
- crop growth pattern
- vegetation decline over time
- deviation from expected crop behavior

---

## What NDVI Does Not Prove Alone

NDVI alone does not prove:

- confirmed crop disease
- confirmed pest infestation
- exact farm-level crop damage
- exact reason for vegetation decline
- retailer demand
- product need

NDVI must be interpreted with:

- crop stage
- historical baseline
- trend
- NDWI
- LST
- rainfall
- pest advisory context, when relevant

---

## Spatial Grain

For Phase 2, NDVI should be aggregated at geography level.

Preferred practical levels:

```text
Tehsil -> District
```

Do not claim farm-level NDVI unless field boundaries, farm polygons, or reliable GPS coordinates are available.

---

## Aggregation Logic

For each observation date and geography:

```text
satellite pixels
  -> clip/filter by tehsil or district boundary
  -> remove cloudy/invalid pixels
  -> calculate NDVI per valid pixel
  -> aggregate to geography-level NDVI
```

Recommended aggregate statistics:

| Statistic | Use |
|---|---|
| `median_ndvi` | Main robust NDVI value |
| `p20_ndvi` | Lower distribution context |
| `p80_ndvi` | Upper distribution context |
| `valid_pixel_count` | Quality/reliability check |
| `cloud_coverage_pct` | Observation quality check |

Prefer median over mean because satellite observations can be noisy.

---

## Historical Baseline Logic

NDVI should be interpreted relative to expected behavior.

Avoid fixed rules like:

```text
NDVI < 0.4 = unhealthy
```

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season
```

Baseline values:

| Baseline Feature | Meaning |
|---|---|
| `baseline_median_ndvi` | Expected NDVI for similar context |
| `baseline_p20_ndvi` | Lower expected range |
| `baseline_p80_ndvi` | Upper expected range |
| `ndvi_anomaly` | Current NDVI minus baseline median |

This makes NDVI interpretation:

- crop-aware
- stage-aware
- geography-aware
- season-aware

---

## Statistical Labeling

Current NDVI should be converted into a statistical position label.

| Label | Logic |
|---|---|
| `Very Low` | current NDVI below baseline p20 |
| `Low-Normal` | current NDVI between p20 and median |
| `Normal` | current NDVI close to median |
| `High-Normal` | current NDVI between median and p80 |
| `Very High` | current NDVI above baseline p80 |

Important:

```text
These are statistical labels, not automatic health labels.
```

Example:

```text
NDVI = Very Low
```

means:

```text
NDVI is low compared with expected local crop-stage behavior.
```

It does not automatically mean:

```text
confirmed crop failure.
```

---

## Crop-Stage Interpretation

NDVI meaning changes by crop stage.

Example stage expectations:

| Crop Stage | Expected NDVI Behavior |
|---|---|
| Sowing / establishment | Low but rising |
| Vegetative / tillering | Rising / high |
| Flowering / reproductive | Stable-high |
| Maturity | Declining |
| Harvest | Low / declining |

Therefore:

```text
Low NDVI during sowing may be normal.
Low NDVI during active vegetative growth may be concerning.
Falling NDVI during harvest may be normal.
Falling NDVI during vegetative growth may be anomalous.
```

---

## Trend Logic

NDVI trend should be calculated from recent observations.

Recommended trend window:

```text
last 3 valid observations
```

Trend classes:

| Trend | Meaning |
|---|---|
| `Rising` | NDVI increased meaningfully |
| `Stable` | NDVI change is within normal variability |
| `Falling` | NDVI decreased meaningfully |

Trend thresholds should come from historical variability where possible.

Preferred trend threshold key:

```text
geography + crop + crop_stage + signal
```

Fallback only if history is insufficient:

```text
fixed signal-specific threshold
```

Fixed thresholds should be treated as MVP fallbacks, not final scientific rules.

---

## NDVI Anomaly Logic

NDVI anomaly should be detected when current NDVI behavior does not match expected crop-stage behavior.

Example:

```text
Crop stage: Vegetative
Expected NDVI labels: Normal, High-Normal, Very High
Current NDVI label: Very Low
Result: NDVI anomaly
```

Trend example:

```text
Crop stage: Vegetative
Expected trend: Rising
Observed trend: Falling
Result: NDVI trend anomaly
```

---

## Quality Checks

NDVI should be ignored or downgraded when:

- cloud coverage is high
- valid pixel count is too low
- scene date is too old
- geography boundary is unreliable
- crop-stage context is unknown
- satellite observation is missing

Recommended output should include:

```text
ndvi_quality_level = high / medium / low
```

---

## Feature Output

Recommended NDVI feature fields:

| Field | Meaning |
|---|---|
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop context |
| `crop_stage` | Current estimated crop stage |
| `observation_date` | Satellite observation date |
| `median_ndvi` | Aggregated current NDVI |
| `baseline_median_ndvi` | Expected NDVI baseline |
| `baseline_p20_ndvi` | Lower expected range |
| `baseline_p80_ndvi` | Upper expected range |
| `ndvi_label` | Statistical position label |
| `ndvi_anomaly_flag` | Whether current NDVI is outside expected stage behavior |
| `ndvi_trend` | Rising, stable, or falling |
| `ndvi_trend_anomaly_flag` | Whether trend contradicts crop-stage expectation |
| `valid_pixel_count` | Number of valid pixels used |
| `cloud_coverage_pct` | Scene/cloud quality indicator |
| `ndvi_quality_level` | High, medium, or low |

---

## Signals That Use NDVI

NDVI is used by:

- Crop Health Signal
- Pest / Disease Risk Signal

It may also support future:

- territory priority context
- crop stress explanations
- campaign timing context

---

## Explainability Example

```text
NDVI is lower than expected for this crop stage and geography.
The crop is in vegetative stage, where NDVI is expected to be rising or high,
but the latest NDVI label is Very Low and the recent trend is Falling.
```

---

## Current Caution

NDVI is a vegetation condition feature.

It should be used as evidence inside a broader signal, not as a standalone diagnosis.
