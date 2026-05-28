# Heat Stress Signal

## Quick Brief

The Heat Stress Signal estimates whether a crop geography is experiencing abnormal heat or thermal pressure.

It combines land surface temperature, weather temperature context, crop stage, trend behavior, and historical baseline.

This signal should help answer:

```text
Is the crop geography hotter than expected, and does the current crop stage make that heat more concerning?
```

It should not rely on LST alone.

---

## Features Used

| Feature | Source Type | What It Represents | Why It Matters |
|---|---|---|---|
| LST | Satellite / thermal remote sensing | Land surface temperature / surface heat | Primary thermal pressure feature. |
| Weather context | Weather | Air temperature, heat condition, recent weather | Supports interpretation of heat exposure. |
| Crop stage | Crop calendar | Current biological stage | Determines whether heat is operationally severe. |
| Trend analysis | Time series | Whether heat is rising, stable, or falling | Identifies worsening heat pressure. |
| Historical baseline | Derived public-data baseline | Expected LST/temperature range for crop, stage, geography, and time | Prevents fixed universal heat thresholds. |
| Rainfall / moisture context | Weather / satellite support | Dryness or water deficit context | Heat stress is more concerning when moisture is also limited. |
| Geography boundaries | Administrative geography | Spatial aggregation and matching | Keeps the signal tied to tehsil/district-level operating geography. |

---

## Signal Purpose

The Heat Stress Signal should identify geographies where thermal conditions are unusually high for the crop, stage, geography, and time period.

It should support:

- heat-sensitive territory prioritization
- crop-stage-aware risk detection
- explanation-backed field advisory context
- support for crop health and moisture stress interpretation
- downstream campaign timing and territory priority decisions

Recommended operating grain:

```text
Tehsil -> District fallback
```

This should remain a geography-level risk signal unless reliable field boundaries or coordinates are available.

---

## Core Question

The signal should answer:

```text
Is current heat exposure abnormal, worsening, and relevant to the crop's current stage?
```

This means the signal is not asking only:

```text
Is LST high?
```

It is asking:

```text
Is LST or temperature high relative to baseline, is the trend worsening, and is the crop currently heat-sensitive?
```

---

## Recommended Input Grain

| Input | Recommended Grain | Notes |
|---|---|---|
| LST | Tehsil / district / crop / date | Primary thermal observation |
| Air temperature / weather context | Tehsil / district / date window | Supports LST interpretation |
| Crop stage | Crop / geography / date | Determines heat sensitivity |
| Historical baseline | Geography / crop / stage / week or season | Used for LST and temperature interpretation |
| Trend | Geography / crop / thermal feature / recent observations | Usually last 3 valid observations |
| Rainfall / moisture context | Tehsil / district / date window | Helps identify compounding heat + dryness |
| Boundary confidence | Geography | Controls precision and confidence |

---

## Heat Pattern Logic

Heat stress should be treated as a contextual pattern.

Strong heat-stress evidence:

```text
LST above expected range
+ air temperature/weather context hot
+ crop is in heat-sensitive stage
+ LST trend rising
+ rainfall or moisture context is weak
= strong heat stress signal
```

Weak heat-stress evidence:

```text
LST slightly high
+ crop stage not highly sensitive
+ rainfall/moisture context normal
+ no rising trend
= watchlist or low severity
```

This prevents overreaction to one hot observation.

---

## Baseline Comparison Logic

LST and weather temperature should be compared with historical expectation.

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season + feature_name
```

Example:

```text
Ludhiana_T004 + wheat + flowering_reproductive + week_10 + LST
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

For heat stress:

- high or very high LST can be concerning
- high air temperature can support heat exposure reasoning
- moisture deficit can amplify concern

---

## Crop-Stage Interpretation

Crop stage should modify heat severity.

Example:

| Crop Stage | Heat Sensitivity | Interpretation |
|---|---|---|
| Sowing / establishment | Medium | Heat can affect establishment |
| Vegetative / tillering | Medium to high | Heat may reduce growth, especially with moisture deficit |
| Flowering / reproductive | High | Heat can be more damaging during reproductive stages |
| Maturity | Medium | Heat may accelerate drying/senescence |
| Harvest | Low to medium | Heat may be less concerning or expected |

Example:

```text
High LST during flowering
= stronger concern
```

but:

```text
High LST near harvest
= may be less severe depending on crop and rainfall context
```

---

## Component Flags

Create interpretable flags before final scoring.

| Flag | Trigger Logic |
|---|---|
| `lst_high_flag` | LST is above expected range for crop-stage context |
| `temperature_high_flag` | Weather temperature context is above expected range |
| `heat_sensitive_stage_flag` | Crop is in a stage where heat matters more |
| `heat_trend_worsening_flag` | LST or temperature trend is rising/worsening |
| `moisture_compounding_flag` | Rainfall or NDWI context suggests dryness may compound heat |
| `baseline_low_confidence_flag` | Historical baseline is weak or broad fallback |
| `boundary_low_confidence_flag` | Geography match or boundary quality is weak |

These flags should remain visible for explainability.

---

## Scoring Logic

For MVP design, use transparent additive scoring.

| Component | Score |
|---|---:|
| LST high flag active | +2 |
| Temperature high flag active | +1 |
| Heat-sensitive crop stage active | +1 |
| Heat trend worsening flag active | +1 |
| Moisture compounding flag active | +1 |

Rationale:

- LST is the primary thermal observation.
- Air temperature/weather context supports thermal interpretation.
- Crop stage determines sensitivity.
- Trend shows whether pressure is worsening.
- Moisture deficit can make heat stress more operationally important.

Do not add score for weak boundary or baseline confidence. Use those to lower confidence.

---

## Final Signal Labels

Recommended output labels:

| Score | Heat Stress Signal |
|---:|---|
| 0-1 | Normal |
| 2-3 | Heat Risk |
| 4-6 | Severe Heat Stress |

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
| Recent valid LST observation available | Raises confidence |
| Weather temperature context available | Raises confidence |
| Crop stage known clearly | Raises confidence |
| Historical baseline available at tehsil + crop + stage level | Raises confidence |
| Rainfall or moisture context available | Raises confidence for compounding interpretation |
| Thermal source quality is low or missing | Lowers confidence |
| LST is available only at coarse resolution | Lowers confidence |
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
Heat Risk + High Confidence
```

or:

```text
Severe Heat Stress + Low Confidence
```

depending on source quality and baseline availability.

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
| `heat_stress_score` | Additive heat stress score |
| `heat_stress_label` | Normal, Heat Risk, Severe Heat Stress, or Insufficient Evidence |
| `signal_confidence` | High, medium, or low |
| `lst_label` | Baseline-relative LST label |
| `temperature_label` | Baseline-relative weather temperature label |
| `rainfall_or_moisture_label` | Supporting moisture/rainfall context |
| `lst_high_flag` | Whether LST is concerning |
| `temperature_high_flag` | Whether weather temperature is concerning |
| `heat_sensitive_stage_flag` | Whether crop is currently heat-sensitive |
| `heat_trend_worsening_flag` | Whether thermal trend is worsening |
| `moisture_compounding_flag` | Whether dryness may compound heat |
| `baseline_confidence` | Confidence in historical baseline |
| `boundary_confidence` | Confidence in geography match |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

The explanation should show:

1. Whether the signal is normal, heat risk, or severe.
2. Which heat evidence contributed.
3. Whether crop stage increases sensitivity.
4. Whether moisture/dryness compounds the concern.
5. Whether confidence is strong or limited.

Example:

```text
Heat stress is marked as Severe because LST is above the expected range, recent weather context is hot, the thermal trend is rising, and the crop is in a heat-sensitive flowering stage.
```

Compounding example:

```text
Heat risk is strengthened because rainfall and moisture context are weak, which may increase crop sensitivity to elevated surface temperature.
```

Lower-confidence example:

```text
Heat stress is marked as Heat Risk, but confidence is medium because LST is available only at district-level aggregation.
```

---

## Business Use

This signal can help:

- prioritize visits to heat-sensitive crop geographies
- support weather-backed field advisory timing
- explain crop-health decline when thermal pressure is high
- identify territories where moisture stress may worsen under heat
- improve campaign timing for stage-sensitive crop protection actions

---

## Current Caution

Heat Stress Signal should not be described as:

```text
confirmed crop heat damage
```

or:

```text
exact field-level heat loss
```

Preferred wording:

```text
geography-level heat stress risk
```

or:

```text
public-data-backed thermal pressure signal
```

The signal should guide prioritization and field verification, not replace ground observation.
