# NDWI Feature

## Quick Brief

NDWI means Normalized Difference Water Index.

For KshetraAI, NDWI is used as a satellite-derived moisture/water-condition feature. It helps indicate whether vegetation or canopy conditions are becoming drier than expected.

NDWI should be used as crop moisture context, not as standalone proof of drought or irrigation failure.

---

## Formula

For vegetation/canopy water condition, use the Gao-style NDWI:

```text
NDWI = (NIR - SWIR) / (NIR + SWIR)
```

Where:

| Term | Meaning |
|---|---|
| `NIR` | Near-infrared reflectance. For Sentinel-2, use Band 8 (`B08`). |
| `SWIR` | Short-wave infrared reflectance. For Sentinel-2, use Band 11 (`B11`) for canopy water stress context. |

Important:

```text
Some sources use Green and NIR for open-water NDWI.
For crop moisture stress, KshetraAI should use NIR and SWIR.
```

---

## Required Inputs

| Input | Requirement |
|---|---|
| Satellite imagery | Multispectral imagery with NIR and SWIR bands |
| NIR band | Required for formula |
| SWIR band | Required for formula |
| Acquisition date | Required for time-series and crop-stage matching |
| Geography | Required for tehsil/district aggregation |
| Cloud/quality flag | Required to avoid using bad observations |

---

## What NDWI Represents

NDWI can help describe:

- vegetation/canopy water condition
- drying tendency
- moisture stress context
- water-related vegetation decline
- crop moisture anomaly
- change in crop water status over time

---

## What NDWI Does Not Prove Alone

NDWI alone does not prove:

- confirmed drought
- confirmed irrigation failure
- exact soil moisture
- exact crop damage
- exact field-level water stress
- product need

NDWI must be interpreted with:

- rainfall
- LST
- NDVI
- crop stage
- historical baseline
- trend
- geography and quality checks

---

## Spatial Grain

For Phase 2, NDWI should be aggregated at geography level.

Preferred practical levels:

```text
Tehsil -> District
```

Do not claim farm-level moisture stress unless field boundaries, farm polygons, or reliable GPS coordinates are available.

---

## Aggregation Logic

For each observation date and geography:

```text
satellite pixels
  -> clip/filter by tehsil or district boundary
  -> remove cloudy/invalid pixels
  -> calculate NDWI per valid pixel
  -> aggregate to geography-level NDWI
```

Recommended aggregate statistics:

| Statistic | Use |
|---|---|
| `median_ndwi` | Main robust NDWI value |
| `p20_ndwi` | Lower distribution context |
| `p80_ndwi` | Upper distribution context |
| `valid_pixel_count` | Quality/reliability check |
| `cloud_coverage_pct` | Observation quality check |

Prefer median over mean because satellite observations can be noisy.

---

## Historical Baseline Logic

NDWI should be interpreted relative to expected moisture behavior.

Avoid fixed rules like:

```text
NDWI < 0.2 = moisture stress
```

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season
```

Baseline values:

| Baseline Feature | Meaning |
|---|---|
| `baseline_median_ndwi` | Expected NDWI for similar context |
| `baseline_p20_ndwi` | Lower expected range |
| `baseline_p80_ndwi` | Upper expected range |
| `ndwi_anomaly` | Current NDWI minus baseline median |

This makes NDWI interpretation:

- crop-aware
- stage-aware
- geography-aware
- season-aware

---

## Statistical Labeling

Current NDWI should be converted into a statistical position label.

| Label | Logic |
|---|---|
| `Very Low` | current NDWI below baseline p20 |
| `Low-Normal` | current NDWI between p20 and median |
| `Normal` | current NDWI close to median |
| `High-Normal` | current NDWI between median and p80 |
| `Very High` | current NDWI above baseline p80 |

Important:

```text
These are statistical labels, not automatic drought labels.
```

Example:

```text
NDWI = Very Low
```

means:

```text
NDWI is low compared with expected local crop-stage water condition.
```

It does not automatically mean:

```text
confirmed drought.
```

---

## Crop-Stage Interpretation

NDWI meaning changes by crop stage and crop water demand.

Example stage expectations:

| Crop Stage | Expected NDWI Behavior |
|---|---|
| Sowing / establishment | Moisture-sensitive; low NDWI may matter if rainfall is also low |
| Vegetative / tillering | Moderate to high water condition expected |
| Flowering / reproductive | Moisture stress can be high-impact |
| Maturity | Declining NDWI may be normal |
| Harvest | Low / declining NDWI may be normal |

Therefore:

```text
Low NDWI during flowering can be more concerning.
Low NDWI near harvest may be expected.
Low NDWI with high LST and rainfall deficit is stronger evidence of moisture stress.
```

---

## Trend Logic

NDWI trend should be calculated from recent valid observations.

Recommended trend window:

```text
last 3 valid observations
```

Trend classes:

| Trend | Meaning |
|---|---|
| `Rising` | NDWI increased meaningfully |
| `Stable` | NDWI change is within normal variability |
| `Falling` | NDWI decreased meaningfully |

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

## NDWI Anomaly Logic

NDWI anomaly should be detected when current water-condition behavior does not match expected crop-stage behavior.

Example:

```text
Crop stage: Flowering
Expected NDWI labels: Normal, High-Normal, Very High
Current NDWI label: Very Low
Result: NDWI anomaly
```

Trend example:

```text
Crop stage: Vegetative
Expected trend: Stable or Rising
Observed trend: Falling
Result: NDWI trend anomaly
```

---

## Quality Checks

NDWI should be ignored or downgraded when:

- cloud coverage is high
- valid pixel count is too low
- scene date is too old
- SWIR band quality is poor or missing
- geography boundary is unreliable
- crop-stage context is unknown
- satellite observation is missing

Recommended output should include:

```text
ndwi_quality_level = high / medium / low
```

---

## Feature Output

Recommended NDWI feature fields:

| Field | Meaning |
|---|---|
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop context |
| `crop_stage` | Current estimated crop stage |
| `observation_date` | Satellite observation date |
| `median_ndwi` | Aggregated current NDWI |
| `baseline_median_ndwi` | Expected NDWI baseline |
| `baseline_p20_ndwi` | Lower expected range |
| `baseline_p80_ndwi` | Upper expected range |
| `ndwi_label` | Statistical position label |
| `ndwi_anomaly_flag` | Whether current NDWI is outside expected stage behavior |
| `ndwi_trend` | Rising, stable, or falling |
| `ndwi_trend_anomaly_flag` | Whether trend contradicts crop-stage expectation |
| `valid_pixel_count` | Number of valid pixels used |
| `cloud_coverage_pct` | Scene/cloud quality indicator |
| `ndwi_quality_level` | High, medium, or low |

---

## Signals That Use NDWI

NDWI is used by:

- Crop Health Signal
- Moisture Stress Signal

It may also support future:

- pest/disease risk interpretation
- territory priority context
- crop stress explanations

---

## Explainability Example

```text
NDWI is lower than expected for this crop stage and geography.
The crop is in flowering stage, where water stress can be high-impact,
and the latest NDWI label is Very Low with a Falling trend.
```

---

## Current Caution

NDWI is a crop/canopy water-condition feature.

It should be used as evidence inside a broader signal, not as a standalone drought diagnosis.
