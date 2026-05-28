# LST Feature

## Quick Brief

LST means Land Surface Temperature.

For KshetraAI, LST is used as a thermal-condition feature. It helps identify whether land/crop surfaces are hotter than expected for a geography, crop stage, and season.

LST should be used as heat or thermal stress context, not as standalone proof of crop damage.

---

## Source / Measurement Concept

LST is usually derived from thermal remote sensing data.

Common public sources may include:

- MODIS LST products
- Landsat thermal products
- other public thermal satellite products

Unlike NDVI/NDWI, LST is not calculated from Sentinel-2 optical bands in the same direct way, because Sentinel-2 does not provide a thermal band.

---

## Required Inputs

| Input | Requirement |
|---|---|
| Thermal satellite product | Required for land surface temperature |
| LST value | Temperature value, usually in Kelvin or Celsius depending on source |
| Acquisition date | Required for time-series and crop-stage matching |
| Geography | Required for tehsil/district aggregation |
| Quality flag | Required to avoid invalid thermal observations |
| Unit metadata | Required to handle Kelvin/Celsius conversion correctly |

---

## What LST Represents

LST can help describe:

- land surface heating
- thermal stress context
- heat pressure
- dry/hot surface conditions
- surface temperature anomaly
- worsening heat trend over time

---

## What LST Does Not Prove Alone

LST alone does not prove:

- confirmed crop heat damage
- exact canopy temperature
- exact air temperature
- irrigation failure
- pest or disease pressure
- exact field-level stress

LST must be interpreted with:

- crop stage
- NDWI
- NDVI
- rainfall
- air temperature/weather context
- historical baseline
- trend
- scene quality

---

## Spatial Grain

For Phase 2, LST should be aggregated at geography level.

Preferred practical levels:

```text
Tehsil -> District
```

Do not claim farm-level heat stress unless field boundaries, farm polygons, or reliable GPS coordinates are available.

---

## Aggregation Logic

For each observation date and geography:

```text
thermal pixels
  -> clip/filter by tehsil or district boundary
  -> remove invalid pixels
  -> convert units if needed
  -> aggregate to geography-level LST
```

Recommended aggregate statistics:

| Statistic | Use |
|---|---|
| `median_lst` | Main robust LST value |
| `p20_lst` | Lower distribution context |
| `p80_lst` | Upper distribution context |
| `valid_pixel_count` | Quality/reliability check |
| `quality_flag_summary` | Observation quality check |

Prefer median over mean because thermal observations can be noisy and spatially mixed.

---

## Historical Baseline Logic

LST should be interpreted relative to expected thermal behavior.

Avoid fixed rules like:

```text
LST > 40 C = heat stress
```

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season
```

Baseline values:

| Baseline Feature | Meaning |
|---|---|
| `baseline_median_lst` | Expected LST for similar context |
| `baseline_p20_lst` | Lower expected range |
| `baseline_p80_lst` | Upper expected range |
| `lst_anomaly` | Current LST minus baseline median |

This makes LST interpretation:

- crop-aware
- stage-aware
- geography-aware
- season-aware

---

## Statistical Labeling

Current LST should be converted into a statistical position label.

| Label | Logic |
|---|---|
| `Very Low` | current LST below baseline p20 |
| `Low-Normal` | current LST between p20 and median |
| `Normal` | current LST close to median |
| `High-Normal` | current LST between median and p80 |
| `Very High` | current LST above baseline p80 |

Important:

```text
These are statistical labels, not automatic heat-damage labels.
```

Example:

```text
LST = Very High
```

means:

```text
LST is high compared with expected local crop-stage thermal behavior.
```

It does not automatically mean:

```text
confirmed heat damage.
```

---

## Crop-Stage Interpretation

LST impact changes by crop stage.

Example stage expectations:

| Crop Stage | LST Sensitivity |
|---|---|
| Sowing / establishment | Medium; high surface temperature can affect establishment |
| Vegetative / tillering | Medium to high; heat can increase water demand |
| Flowering / reproductive | High; heat stress can be operationally important |
| Maturity | Medium to low depending on crop |
| Harvest | Low for crop-health stress, but may affect field operations |

Therefore:

```text
Very High LST during flowering is more concerning.
Very High LST near harvest may be less concerning for crop health.
Very High LST with low NDWI and rainfall deficit is stronger stress evidence.
```

---

## Trend Logic

LST trend should be calculated from recent valid observations.

Recommended trend window:

```text
last 3 valid observations
```

Trend classes:

| Trend | Meaning |
|---|---|
| `Rising` | LST increased meaningfully |
| `Stable` | LST change is within normal variability |
| `Falling` | LST decreased meaningfully |

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

## LST Anomaly Logic

LST anomaly should be detected when current thermal behavior is higher than expected for the crop-stage/geography context.

Example:

```text
Crop stage: Flowering
Expected LST labels: Normal, Low-Normal, High-Normal
Current LST label: Very High
Result: LST anomaly
```

Trend example:

```text
Crop stage: Flowering
Observed trend: Rising
Current label: Very High
Result: thermal stress evidence strengthens
```

---

## Quality Checks

LST should be ignored or downgraded when:

- quality flag indicates invalid thermal observation
- valid pixel count is too low
- scene date is too old
- unit metadata is unclear
- geography boundary is unreliable
- crop-stage context is unknown
- thermal observation is missing

Recommended output should include:

```text
lst_quality_level = high / medium / low
```

---

## Feature Output

Recommended LST feature fields:

| Field | Meaning |
|---|---|
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop context |
| `crop_stage` | Current estimated crop stage |
| `observation_date` | Thermal observation date |
| `median_lst` | Aggregated current LST |
| `lst_unit` | Celsius or Kelvin |
| `baseline_median_lst` | Expected LST baseline |
| `baseline_p20_lst` | Lower expected range |
| `baseline_p80_lst` | Upper expected range |
| `lst_label` | Statistical position label |
| `lst_anomaly_flag` | Whether current LST is outside expected thermal behavior |
| `lst_trend` | Rising, stable, or falling |
| `lst_trend_anomaly_flag` | Whether trend strengthens thermal-stress concern |
| `valid_pixel_count` | Number of valid pixels used |
| `quality_flag_summary` | Thermal product quality summary |
| `lst_quality_level` | High, medium, or low |

---

## Signals That Use LST

LST is used by:

- Crop Health Signal
- Moisture Stress Signal
- Heat Stress Signal

It may also support future:

- pest/disease risk interpretation
- territory priority context
- crop stress explanations

---

## Explainability Example

```text
LST is higher than expected for this crop stage and geography.
The crop is in flowering stage, where thermal stress can be high-impact,
and the latest LST label is Very High with a Rising trend.
```

---

## Current Caution

LST is a thermal-condition feature.

It should be used as evidence inside a broader signal, not as a standalone crop damage diagnosis.
