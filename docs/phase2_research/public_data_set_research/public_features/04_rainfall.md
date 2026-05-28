# Rainfall Feature

## Quick Brief

Rainfall is a weather-derived water availability feature.

For KshetraAI, rainfall helps explain whether vegetation or moisture stress may be linked to recent rainfall deficit or abnormal rainfall behavior.

Rainfall should be used as environmental context, not as standalone proof of crop stress.

---

## Required Inputs

| Input | Requirement |
|---|---|
| Rainfall amount | Daily or aggregated rainfall value |
| Observation date | Required for time-window and crop-stage matching |
| Geography | Required for district/tehsil aggregation |
| Source metadata | Required to track whether data comes from station, gridded, satellite, or model source |
| Unit metadata | Required to keep rainfall units consistent, usually millimeters |
| Quality flag | Useful when source provides missing/estimated/low-confidence indicators |

---

## What Rainfall Represents

Rainfall can help describe:

- recent water availability
- rainfall deficit
- rainfall surplus
- dry spell context
- wet spell context
- weather support for moisture stress
- disease/pest-favorable wetness context

---

## What Rainfall Does Not Prove Alone

Rainfall alone does not prove:

- actual soil moisture level
- actual irrigation availability
- confirmed drought damage
- confirmed crop recovery
- exact field-level water availability
- exact pest or disease risk

Rainfall must be interpreted with:

- NDWI
- NDVI
- LST
- crop stage
- historical rainfall baseline
- trend/dry-spell context
- irrigation context, if available

---

## Spatial Grain

For Phase 2, rainfall should be aggregated or mapped at geography level.

Preferred practical levels:

```text
Tehsil -> District
```

Rainfall may be available at different grains depending on the source:

- station level
- gridded cell
- district level
- model/forecast grid

The pipeline should normalize it to the operating geography used by the signal layer.

---

## Time Windows

Rainfall should be summarized across recent windows, not only one day.

Recommended windows:

| Window | Use |
|---|---|
| 1-day rainfall | Immediate weather context |
| 3-day rainfall | Short wet/dry spell context |
| 7-day rainfall | Recent crop water availability |
| 14-day rainfall | Medium recent moisture context |
| season-to-date rainfall | Seasonal water context |

The best window may vary by crop stage and signal.

---

## Historical Baseline Logic

Rainfall should be interpreted relative to expected rainfall.

Avoid fixed rules like:

```text
rainfall_7d < 10 mm = deficit
```

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season
```

Baseline values:

| Baseline Feature | Meaning |
|---|---|
| `baseline_median_rainfall_7d` | Expected 7-day rainfall for similar context |
| `baseline_p20_rainfall_7d` | Lower expected rainfall range |
| `baseline_p80_rainfall_7d` | Upper expected rainfall range |
| `rainfall_anomaly_7d` | Current 7-day rainfall minus baseline median |
| `rainfall_ratio_7d` | Current 7-day rainfall divided by baseline median |

This makes rainfall interpretation:

- geography-aware
- season-aware
- stage-aware
- less dependent on arbitrary fixed thresholds

---

## Statistical Labeling

Current rainfall should be converted into a statistical position label.

| Label | Logic |
|---|---|
| `Very Low` | current rainfall below baseline p20 |
| `Low-Normal` | current rainfall between p20 and median |
| `Normal` | current rainfall close to median |
| `High-Normal` | current rainfall between median and p80 |
| `Very High` | current rainfall above baseline p80 |

Important:

```text
These are rainfall-position labels, not automatic crop stress labels.
```

Example:

```text
rainfall_7d = Very Low
```

means:

```text
recent rainfall is low compared with expected local seasonal behavior.
```

It does not automatically mean:

```text
confirmed drought stress.
```

---

## Crop-Stage Interpretation

Rainfall impact changes by crop stage.

Example stage sensitivity:

| Crop Stage | Rainfall Sensitivity |
|---|---|
| Sowing / establishment | High; rainfall deficit can affect establishment |
| Vegetative / tillering | Medium to high; deficit can slow growth |
| Flowering / reproductive | High; water stress can be high-impact |
| Maturity | Medium to low depending on crop |
| Harvest | Excess rainfall may be operationally more important than deficit |

Therefore:

```text
Rainfall deficit during flowering can be more concerning.
Rainfall deficit near harvest may be less concerning for crop growth.
Excess rainfall near harvest may affect field operations or crop quality.
```

---

## Trend / Dry Spell Logic

Rainfall trend should consider recent windows.

Useful derived indicators:

| Indicator | Meaning |
|---|---|
| `rainfall_3d` | Total rainfall in last 3 days |
| `rainfall_7d` | Total rainfall in last 7 days |
| `rainfall_14d` | Total rainfall in last 14 days |
| `dry_spell_days` | Consecutive days below rainfall threshold |
| `wet_spell_days` | Consecutive days with meaningful rainfall |
| `rainfall_trend` | Improving, stable, deficient, or excessive |

Rainfall trend thresholds should come from historical variability where possible.

Fallback thresholds may be used only as MVP defaults.

---

## Rainfall Anomaly Logic

Rainfall anomaly should be detected when recent rainfall is materially below or above expected behavior.

Example:

```text
Crop stage: Flowering
Current 7-day rainfall label: Very Low
NDWI label: Very Low
LST label: Very High
Result: rainfall deficit strengthens crop stress evidence
```

Wetness example:

```text
Recent rainfall: Very High
Humidity: High
Crop stage: Disease-sensitive
Result: rainfall may support pest/disease-favorable condition
```

---

## Quality Checks

Rainfall should be ignored or downgraded when:

- observation is missing
- source quality flag is low
- geography mapping is unclear
- unit metadata is unclear
- forecast and observed rainfall are mixed without labeling
- data is too stale for the target signal

Recommended output should include:

```text
rainfall_quality_level = high / medium / low
```

---

## Feature Output

Recommended rainfall feature fields:

| Field | Meaning |
|---|---|
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop context, when available |
| `crop_stage` | Current estimated crop stage |
| `observation_date` | Rainfall observation date |
| `rainfall_1d` | Rainfall in last 1 day |
| `rainfall_3d` | Rainfall in last 3 days |
| `rainfall_7d` | Rainfall in last 7 days |
| `rainfall_14d` | Rainfall in last 14 days |
| `baseline_median_rainfall_7d` | Expected 7-day rainfall baseline |
| `baseline_p20_rainfall_7d` | Lower expected 7-day rainfall range |
| `baseline_p80_rainfall_7d` | Upper expected 7-day rainfall range |
| `rainfall_label_7d` | Statistical position label |
| `rainfall_deficit_flag` | Whether recent rainfall is below expected range |
| `rainfall_surplus_flag` | Whether recent rainfall is above expected range |
| `dry_spell_days` | Consecutive dry days |
| `wet_spell_days` | Consecutive wet days |
| `rainfall_trend` | Improving, stable, deficient, or excessive |
| `rainfall_quality_level` | High, medium, or low |
| `source_name` | Rainfall data source |

---

## Signals That Use Rainfall

Rainfall is used by:

- Crop Health Signal
- Moisture Stress Signal
- Pest / Disease Risk Signal

It may also support future:

- spray suitability
- campaign timing
- territory priority context
- crop stress explanations

---

## Explainability Example

```text
Recent rainfall is below the expected range for this geography and crop stage.
The 7-day rainfall label is Very Low, and this strengthens the moisture-stress evidence
because NDWI is also low and LST is high.
```

---

## Current Caution

Rainfall is a water-availability context feature.

It should be used with NDWI, LST, NDVI, and crop stage before concluding crop stress or pest/disease risk.
