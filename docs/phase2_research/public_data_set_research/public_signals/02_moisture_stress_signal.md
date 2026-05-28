# Moisture Stress Signal

## Quick Brief

The Moisture Stress Signal estimates whether a crop geography is showing signs of water-related stress.

It combines satellite-derived crop water condition with rainfall, thermal context, crop stage, trend behavior, and historical baseline.

This signal should help answer:

```text
Is the crop likely experiencing moisture stress relative to what is expected for this crop, stage, geography, and time period?
```

It should not rely on rainfall alone or NDWI alone.

---

## Features Used

| Feature | Source Type | What It Represents | Why It Matters |
|---|---|---|---|
| NDWI | Satellite | Crop/canopy water condition | Primary indicator for vegetation/canopy drying tendency. |
| Rainfall | Weather | Recent water availability | Explains whether moisture stress is supported by rainfall deficit or dry spell. |
| LST | Satellite / thermal remote sensing | Land surface temperature / heat condition | High LST can strengthen moisture-stress interpretation. |
| Crop stage | Crop calendar | Current biological stage | Determines whether the crop is sensitive to water deficit right now. |
| Trend analysis | Time series | Recent worsening or recovery | Shows whether moisture condition is declining, stable, or improving. |
| Historical baseline | Derived public-data baseline | Expected range for crop, stage, geography, and time | Avoids fixed universal thresholds. |
| Weather context | Weather | Recent heat, wetness, dryness, humidity | Adds supporting context for water stress interpretation. |
| Geography boundaries | Administrative geography | Spatial aggregation and matching | Keeps the signal tied to tehsil/district-level operating geography. |

---

## Signal Purpose

The Moisture Stress Signal should identify geographies where crop water condition is weaker than expected and recent weather supports a drying or deficit interpretation.

It should support:

- early warning for possible crop water stress
- better prioritization of field visits
- stage-aware advisory timing
- explanation-backed agronomic context
- downstream crop health and territory priority signals

Recommended operating grain:

```text
Tehsil -> District fallback
```

This should remain a geography-level risk signal unless reliable field boundaries or coordinates are available.

---

## Core Question

The signal should answer:

```text
Is crop water condition worse than expected, and is there supporting weather evidence?
```

This means the signal is not asking only:

```text
Was rainfall low?
```

or:

```text
Is NDWI low?
```

It is asking:

```text
Are NDWI, rainfall, LST, crop stage, and trend aligned with a moisture-stress pattern?
```

---

## Recommended Input Grain

| Input | Recommended Grain | Notes |
|---|---|---|
| NDWI | Tehsil / district / crop / date | Primary crop moisture observation |
| Rainfall | Tehsil / district / date window | 7-day and 14-day windows are useful |
| LST | Tehsil / district / crop / date | Used as thermal support, not standalone moisture proof |
| Crop stage | Crop / geography / date | Determines sensitivity to water deficit |
| Historical baseline | Geography / crop / stage / week or season | Used for NDWI, rainfall, and LST interpretation |
| Trend | Geography / crop / feature / recent observations | Usually last 3 valid observations |
| Weather context | Geography / date window | Adds dry spell, heat, and short-term context |
| Boundary confidence | Geography | Controls precision and confidence |

---

## Moisture Pattern Logic

Moisture stress should be treated as a pattern, not a single metric.

Strong moisture-stress evidence:

```text
NDWI below expected range
+ rainfall deficit or dry spell
+ LST high or rising
+ crop is in water-sensitive stage
+ NDWI trend worsening
= strong moisture stress signal
```

Weak moisture-stress evidence:

```text
NDWI slightly low
+ rainfall normal
+ LST normal
+ crop stage not highly sensitive
= watchlist or low confidence
```

This prevents the system from overreacting to a single noisy satellite observation.

---

## Baseline Comparison Logic

Each measurable feature should be compared with historical expectation.

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season + feature_name
```

Example:

```text
Wardha_T002 + cotton + flowering_reproductive + week_31 + NDWI
```

Recommended labels:

| Label | Meaning |
|---|---|
| `very_low` | Below expected lower range |
| `low_normal` | Lower side of expected range |
| `normal` | Around expected median |
| `high_normal` | Upper side of expected range |
| `very_high` | Above expected upper range |
| `unknown` | Baseline or observation not reliable enough |

For moisture stress:

- low NDWI can be concerning
- low rainfall can support water deficit reasoning
- high LST can support drying/heat pressure reasoning

---

## Crop-Stage Interpretation

Crop stage should change the seriousness of moisture stress.

Example:

| Crop Stage | Moisture Sensitivity | Interpretation |
|---|---|---|
| Sowing / establishment | Medium to high | Moisture deficit can affect establishment |
| Vegetative / tillering | High | Moisture deficit may reduce growth |
| Flowering / reproductive | High | Moisture deficit can be more damaging |
| Maturity | Medium to low | Some drying may be normal |
| Harvest | Low | Drying may be expected |

Example:

```text
Low NDWI during flowering
= more concerning
```

but:

```text
Low NDWI near harvest
= may be normal or lower severity
```

---

## Component Flags

Create interpretable flags before final scoring.

| Flag | Trigger Logic |
|---|---|
| `ndwi_low_flag` | NDWI is below expected range for crop-stage context |
| `rainfall_deficit_flag` | Recent rainfall is below expected baseline or dry spell is active |
| `lst_drying_support_flag` | LST is high/rising and supports drying interpretation |
| `water_sensitive_stage_flag` | Crop is in a stage where water deficit matters more |
| `moisture_trend_worsening_flag` | NDWI or related moisture trend is worsening |
| `baseline_low_confidence_flag` | Historical baseline is weak or broad fallback |
| `boundary_low_confidence_flag` | Geography match or boundary quality is weak |

These flags should remain visible for explainability.

---

## Scoring Logic

For MVP design, use transparent additive scoring.

| Component | Score |
|---|---:|
| NDWI low flag active | +2 |
| Rainfall deficit flag active | +1 |
| LST drying support flag active | +1 |
| Water-sensitive crop stage active | +1 |
| Moisture trend worsening flag active | +1 |

Rationale:

- NDWI is the primary crop/canopy moisture indicator.
- Rainfall explains recent water availability.
- LST strengthens drying/heat-pressure interpretation.
- Crop stage modifies severity.
- Trend helps distinguish isolated low observations from worsening conditions.

Do not add score for poor boundary or baseline confidence. Use those to lower confidence.

---

## Final Signal Labels

Recommended output labels:

| Score | Moisture Stress Signal |
|---:|---|
| 0-1 | Normal |
| 2-3 | Emerging Moisture Stress |
| 4-6 | Severe Moisture Stress |

If too many inputs are missing:

```text
Insufficient Evidence
```

should be allowed as a safe output.

---

## Confidence Logic

Signal confidence should be separate from stress level.

Recommended confidence factors:

| Confidence Factor | Impact |
|---|---|
| Recent valid NDWI observation available | Raises confidence |
| Rainfall data available for recent windows | Raises confidence |
| LST or temperature context available | Raises confidence |
| Crop stage known clearly | Raises confidence |
| Historical baseline available at tehsil + crop + stage level | Raises confidence |
| Satellite cloud cover is high | Lowers confidence |
| Rainfall source is broad or low resolution | Lowers confidence |
| Baseline uses broad fallback | Lowers confidence |
| Boundary match is weak | Lowers confidence |

Recommended labels:

```text
high
medium
low
```

Example:

```text
Severe Moisture Stress + Medium Confidence
```

can happen when the pattern is strong but geography or baseline precision is limited.

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
| `moisture_stress_score` | Additive moisture stress score |
| `moisture_stress_label` | Normal, Emerging Moisture Stress, Severe Moisture Stress, or Insufficient Evidence |
| `signal_confidence` | High, medium, or low |
| `ndwi_label` | Baseline-relative NDWI label |
| `rainfall_label` | Baseline-relative rainfall label |
| `lst_label` | Baseline-relative LST label |
| `ndwi_low_flag` | Whether NDWI is concerning |
| `rainfall_deficit_flag` | Whether rainfall deficit is active |
| `lst_drying_support_flag` | Whether LST supports drying interpretation |
| `water_sensitive_stage_flag` | Whether crop is currently water-sensitive |
| `moisture_trend_worsening_flag` | Whether moisture trend is worsening |
| `baseline_confidence` | Confidence in historical baseline |
| `boundary_confidence` | Confidence in geography match |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

The explanation should show:

1. Whether the signal is normal, emerging, or severe.
2. Which evidence contributed.
3. Whether crop stage increases sensitivity.
4. Whether confidence is strong or limited.

Example:

```text
Moisture stress is marked as Severe because NDWI is below the expected range, recent rainfall is deficient, LST is elevated, and the crop is in a water-sensitive flowering stage.
```

Lower-confidence example:

```text
Moisture stress is marked as Emerging, but confidence is medium because recent NDWI is valid while rainfall is available only at district-level fallback.
```

---

## Business Use

This signal can help:

- identify drought-sensitive or drying territories
- prioritize visits where water stress may affect crop outcomes
- support irrigation, nutrient, or crop-protection advisory timing
- explain why a crop health signal is worsening
- improve field-force focus before stress becomes visible in sales or inventory signals

---

## Current Caution

Moisture Stress Signal should not be described as:

```text
confirmed drought
```

or:

```text
confirmed irrigation failure
```

Preferred wording:

```text
geography-level moisture stress risk
```

or:

```text
public-data-backed drying or water-deficit signal
```

The signal should guide prioritization and field verification, not replace ground observation.
