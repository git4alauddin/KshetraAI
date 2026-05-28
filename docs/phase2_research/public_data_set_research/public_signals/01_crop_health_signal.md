# Crop Health Signal

## Quick Brief

The Crop Health Signal estimates geography-level crop condition by combining vegetation, moisture, thermal, weather, crop-stage, and trend features.

This signal should help answer:

```text
Is the crop behaving as expected for this crop, stage, geography, and time period?
```

It should not rely on one index such as NDVI alone. Instead, it compares current observations against expected historical behavior for the same crop-stage and geography.

---

## Features Used

| Feature | Source Type | What It Represents | Why It Matters |
|---|---|---|---|
| NDVI | Satellite | Vegetation greenness / crop vigor | Shows whether crop vegetation appears healthy, weak, rising, or declining. |
| NDWI | Satellite | Crop/canopy water condition | Helps identify moisture stress or drying tendency. |
| LST | Satellite / thermal remote sensing | Land surface temperature / thermal condition | Helps identify heat or surface-temperature stress. |
| Rainfall | Weather | Recent water availability | Explains whether vegetation or moisture stress may be linked to rainfall deficit. |
| Crop stage | Crop calendar | Expected biological stage for crop and date | Determines whether observed behavior is normal or abnormal for the current stage. |
| Trend analysis | Time series | Direction of recent change | Shows whether crop condition is improving, stable, or worsening. |
| Historical baseline | Derived public-data baseline | Expected range for crop, stage, geography, and time | Provides crop/stage/geography-specific thresholds instead of fixed universal cutoffs. |
| Tehsil/district boundary | Administrative geography | Spatial aggregation unit | Allows satellite and weather signals to be aggregated into operational geography. |

---

## Signal Purpose

The Crop Health Signal should identify whether a crop geography is behaving normally or showing signs of stress.

It should support:

- geography-level crop monitoring
- field-force visit prioritization
- early warning for stressed territories
- explanation-backed agronomic context
- downstream moisture, heat, and pest-risk interpretation

This signal is intentionally geography-level for now.

Recommended operating grain:

```text
Tehsil -> District fallback
```

Avoid farm-level or retailer-level claims unless reliable field boundaries or coordinates are available.

---

## Core Question

The signal should answer:

```text
Is current crop condition normal for this crop, stage, geography, and time period?
```

This means the signal is not asking:

```text
Is NDVI below one fixed threshold?
```

It is asking:

```text
Are NDVI, NDWI, LST, rainfall, and recent trends aligned with what is expected here right now?
```

---

## Recommended Input Grain

| Input | Recommended Grain | Notes |
|---|---|---|
| NDVI | Tehsil / district / crop / date | Aggregated from satellite observations |
| NDWI | Tehsil / district / crop / date | Aggregated from satellite observations |
| LST | Tehsil / district / crop / date | Thermal aggregation, source-dependent |
| Rainfall | Tehsil / district / date window | Recent 7-day and 14-day windows are useful |
| Crop stage | Crop / geography / date | Derived from crop calendar |
| Historical baseline | Geography / crop / stage / week or season | Used for dynamic interpretation |
| Trend | Geography / crop / feature / recent observations | Usually last 3 valid observations |
| Boundary confidence | Geography | Controls confidence and precision of the signal |

---

## Baseline Comparison Logic

Each measurable feature should first be compared against its historical baseline.

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season + feature_name
```

Example:

```text
Wardha_T002 + cotton + flowering_reproductive + week_31 + NDVI
```

Recommended statistical labels:

| Label | Meaning |
|---|---|
| `very_low` | Below expected lower range |
| `low_normal` | Lower side of expected range |
| `normal` | Around expected median |
| `high_normal` | Upper side of expected range |
| `very_high` | Above expected upper range |
| `unknown` | Baseline or observation not reliable enough |

These labels describe statistical position, not final health status.

---

## Stage-Aware Interpretation

Crop stage decides whether a statistical label is good, normal, or concerning.

Example:

| Crop Stage | Expected NDVI Behavior | Falling NDVI Means |
|---|---|---|
| Sowing / establishment | Low or rising from low base | May be normal |
| Vegetative / tillering | Rising or high | Concerning if falling |
| Flowering / reproductive | Stable-high | Concerning if falling sharply |
| Maturity | Declining | Often normal |
| Harvest | Low or declining | Often normal |

This prevents false alarms.

Example:

```text
NDVI falling during harvest
= expected behavior
```

but:

```text
NDVI falling during vegetative growth
= possible crop-health concern
```

---

## Component Flags

Before producing the final signal, create interpretable component flags.

| Flag | Trigger Logic |
|---|---|
| `ndvi_health_flag` | NDVI label is below what is expected for crop stage |
| `ndwi_moisture_flag` | NDWI label indicates lower-than-expected crop/canopy water condition |
| `lst_heat_flag` | LST or heat context is above expected range for crop stage |
| `rainfall_deficit_flag` | Recent rainfall is below baseline or dry spell is active |
| `trend_worsening_flag` | Recent NDVI/NDWI trend contradicts expected stage behavior |
| `boundary_low_confidence_flag` | Geography match or boundary quality is weak |
| `baseline_low_confidence_flag` | Historical baseline has limited observations or broad fallback |

These flags should be kept in the output so the signal remains explainable.

---

## Scoring Logic

For MVP design, use a transparent additive score.

| Component | Score |
|---|---:|
| NDVI health flag active | +2 |
| NDWI moisture flag active | +2 |
| LST heat flag active | +2 |
| Rainfall deficit flag active | +1 |
| Worsening trend flag active | +1 |

Rationale:

- NDVI, NDWI, and LST are primary crop-condition indicators.
- Rainfall is an environmental driver and explanation layer.
- Trend confirms whether the condition is worsening or improving.

Do not include geography or baseline confidence as stress points. Use them to lower confidence, not to increase risk.

---

## Final Signal Labels

Recommended output labels:

| Score | Crop Health Signal |
|---:|---|
| 0-1 | Healthy |
| 2-3 | Watchlist |
| 4-5 | Moderate Stress |
| 6-8 | High Stress |

If too many inputs are missing:

```text
Insufficient Evidence
```

should be allowed as a safe output.

---

## Confidence Logic

Signal confidence should be separate from stress level.

Recommended confidence inputs:

| Confidence Factor | Impact |
|---|---|
| Recent valid satellite observations available | Raises confidence |
| Historical baseline available at tehsil + crop + stage level | Raises confidence |
| Crop stage known clearly | Raises confidence |
| Boundary match is exact or high confidence | Raises confidence |
| Cloud cover or missing observations are high | Lowers confidence |
| Baseline uses broad fallback | Lowers confidence |
| Crop stage unknown | Lowers confidence |

Recommended confidence labels:

```text
high
medium
low
```

Example:

```text
High Stress + Low Confidence
```

is possible and should be displayed cautiously.

---

## Recommended Output Fields

| Field | Meaning |
|---|---|
| `signal_id` | Internal signal record ID |
| `signal_date` | Date of signal generation |
| `geography_id` | Operating geography |
| `geography_level` | Tehsil, district, etc. |
| `crop_id` | Crop being evaluated |
| `crop_stage` | Current crop stage |
| `crop_health_score` | Additive stress score |
| `crop_health_label` | Healthy, Watchlist, Moderate Stress, High Stress, or Insufficient Evidence |
| `signal_confidence` | High, medium, or low |
| `ndvi_label` | Baseline-relative NDVI label |
| `ndwi_label` | Baseline-relative NDWI label |
| `lst_label` | Baseline-relative LST label |
| `rainfall_label` | Baseline-relative rainfall label |
| `ndvi_health_flag` | Whether NDVI is concerning |
| `ndwi_moisture_flag` | Whether NDWI is concerning |
| `lst_heat_flag` | Whether LST is concerning |
| `rainfall_deficit_flag` | Whether rainfall deficit is active |
| `trend_worsening_flag` | Whether trend is worsening against expected stage behavior |
| `baseline_confidence` | Confidence in historical baseline |
| `boundary_confidence` | Confidence in geography match |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

The explanation should show:

1. What the final label is.
2. Which evidence contributed.
3. Why crop stage matters.
4. Whether the evidence is strong or limited.

Example:

```text
Crop health is marked as Moderate Stress because NDVI and NDWI are below the expected range for cotton at flowering stage, LST is above normal, and the recent trend is worsening. Rainfall deficit also supports moisture-stress interpretation.
```

Lower-confidence example:

```text
Crop health is marked as Watchlist, but confidence is medium because the signal uses district-level fallback geography and limited recent satellite observations.
```

---

## Business Use

This signal can help:

- prioritize field visits to stressed crop geographies
- surface early warnings before sales data reflects the issue
- support explainable agronomic conversations
- provide context for next best action recommendations
- improve anomaly interpretation by separating crop stress from normal seasonal behavior

---

## Current Caution

Crop Health Signal should not be described as:

```text
confirmed crop damage
```

or:

```text
farm-level crop failure
```

Preferred wording:

```text
geography-level crop-health stress signal
```

or:

```text
public-data-backed crop condition risk
```

The signal should guide prioritization and investigation, not replace field verification.
