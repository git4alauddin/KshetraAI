# Satellite Crop Stress Design

This note defines the Phase 2 design for a satellite-backed crop stress risk signal.

The goal is to combine vegetation, water/moisture, thermal, weather, and crop-stage context into an explainable risk indicator.

This signal should be treated as crop stress risk, not confirmed crop damage.

---

## Core Idea

Use multiple indicators together instead of relying on NDVI alone.

```text
NDVI falling
+ NDWI low
+ LST high
+ rainfall deficit
+ sensitive crop stage
= high crop stress risk
```

This logic is more reliable because each indicator explains a different part of crop stress:

| Indicator | Meaning |
|---|---|
| NDVI | Vegetation greenness / crop vigor |
| NDWI | Vegetation or canopy water condition |
| LST | Thermal stress / land surface heating |
| Rainfall deficit | Recent water availability context |
| Crop stage | Sensitivity of the crop at that point in its lifecycle |

---

## Why Not Use NDVI Alone

NDVI alone can be misleading because it changes naturally across crop stage and season.

Low or falling NDVI may happen because of:

- crop stress
- early crop establishment
- crop maturity or harvest
- bare soil
- cloud or scene quality issues
- crop type differences
- normal seasonal pattern

Therefore, NDVI should be interpreted with water, thermal, weather, and crop-stage context.

---

## Desired Public/Satellite Inputs

### Satellite Inputs

| Input | Required Fields |
|---|---|
| NDVI | geography, date, NDVI value, quality/cloud flag if available |
| NDWI | geography, date, NDWI value, quality/cloud flag if available |
| LST | geography, date, land surface temperature value, quality flag if available |

### Weather Inputs

| Input | Required Fields |
|---|---|
| Rainfall | geography, date, recent rainfall total |
| Temperature | geography, date, maximum/mean temperature |
| Humidity | geography, date, humidity if available |

### Crop Calendar Inputs

| Input | Required Fields |
|---|---|
| Crop stage | crop, geography, season, sowing window, stage windows, harvest window |

---

## Baseline-Based Threshold Design

Thresholds should be relative wherever possible.

Avoid:

```text
NDVI < 0.4 means stress
```

Prefer:

```text
current NDVI is below expected NDVI for this crop/stage/geography
```

### Recommended Anomaly Features

| Feature | Logic |
|---|---|
| `ndvi_anomaly` | current NDVI minus NDVI baseline |
| `ndwi_anomaly` | current NDWI minus NDWI baseline |
| `lst_anomaly` | current LST minus LST baseline |
| `rainfall_anomaly` | recent rainfall minus rainfall baseline |

### Baseline Options

| Baseline Type | Use |
|---|---|
| same geography recent historical baseline | Best when enough past observations exist |
| same crop-stage baseline | Best when crop calendar is reliable |
| rolling recent median | Useful for early implementation |
| district/tehsil seasonal baseline | Useful when field-level history is unavailable |

---

## Evidence Flags

Each indicator should produce an explainable evidence flag.

| Evidence Flag | Example Logic |
|---|---|
| `ndvi_decline_flag` | NDVI anomaly is below threshold or NDVI has fallen over recent scenes |
| `ndwi_low_flag` | NDWI anomaly is below threshold |
| `lst_high_flag` | LST anomaly is above threshold |
| `rainfall_deficit_flag` | recent rainfall is below expected rainfall |

Exact numeric thresholds should be finalized after reviewing available data coverage, date frequency, and baseline stability.

---

## Base Stress Level

The first version can use an evidence-count rule.

```text
evidence_count =
    ndvi_decline_flag
  + ndwi_low_flag
  + lst_high_flag
  + rainfall_deficit_flag
```

Recommended classification:

| Evidence Count | Base Stress Level |
|---:|---|
| 0-1 | Low |
| 2 | Moderate |
| 3-4 | High |

This makes the logic transparent and easy to explain.

---

## Crop Stage Sensitivity Modifier

Crop stage should adjust the impact of the stress signal.

The same satellite/weather stress pattern should not always produce the same operational urgency.

### Recommended Stage Sensitivity

| Crop Stage | Sensitivity | Modifier |
|---|---|---|
| sowing / establishment | Medium-high | Upgrade if moisture stress is present |
| vegetative / tillering | Medium | Keep base level |
| flowering / reproductive / grain filling / pod formation | High | Upgrade one level |
| maturity / harvest | Low | Downgrade one level |
| unknown | Neutral | Keep base level |

### Example

```text
Base stress level: Moderate
Crop stage: Flowering
Final stress level: High
```

```text
Base stress level: Moderate
Crop stage: Harvest
Final stress level: Low
```

---

## Final Stress Risk Logic

```text
satellite_weather_stress =
    classify evidence_count into low/moderate/high

final_crop_stress_level =
    adjust satellite_weather_stress by crop_stage_sensitivity
```

Recommended final levels:

- Low
- Moderate
- High

Optional numeric score:

```text
crop_stress_score = 0 to 100
```

The score should remain explainable through component evidence.

---

## Example Explainability Output

```text
High crop stress risk because vegetation greenness declined, water index is low,
surface temperature is above normal, rainfall was below expected levels,
and the crop is in a flowering/yield-formation stage.
```

If crop stage lowers the impact:

```text
Moderate satellite/weather stress was detected, but final crop stress risk
was reduced because the crop is near maturity/harvest stage.
```

---

## Engine Usage

### Priority Engine

Use crop stress level as a priority boost for affected territories, tehsils, or retailers in the same geography.

### Contextual Decision Engine

Use stress type to guide next best action:

- moisture stress context
- heat stress context
- crop-stage-sensitive advisory
- product or advisory discussion if aligned with crop and issue

### Anomaly Detection Engine

Trigger crop stress alerts when stress level rises sharply or remains high across multiple observations.

### Explainability Engine

Show component evidence:

- NDVI evidence
- NDWI evidence
- LST evidence
- rainfall evidence
- crop-stage sensitivity

---

## Reliability Notes

This signal is strongest when:

- satellite scenes are recent
- cloud/quality issues are controlled
- crop stage is known
- rainfall baseline is available
- geography alignment is stable

This signal is weaker when:

- field boundaries are unavailable
- satellite scene quality is poor
- crop stage is unknown
- only one index is available
- geography is too coarse

---

## Current Caution

This signal should be described as:

```text
crop stress risk
```

Not:

```text
confirmed crop damage
```

Field validation or local agronomist review would be needed before treating it as confirmed damage.

---

## Research Support

The design is aligned with established remote-sensing practice where vegetation indices, water/moisture indices, thermal indicators, precipitation, and crop-stage context are used together for agricultural drought or crop water-stress monitoring.

Research-backed concepts:

- vegetation condition can be represented through NDVI
- vegetation/canopy water condition can be represented through NDWI or related moisture indices
- land surface temperature can support thermal or water-stress interpretation
- rainfall deficit adds weather context
- crop stage changes the operational impact of water or heat stress

The implementation should cite the final selected references when this design moves from planning to build.
