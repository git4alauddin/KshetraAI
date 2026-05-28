# Public Feature Reference

This folder documents the public-data features planned for Phase 2 signal design.

Each feature is documented separately so it can be reasoned about, processed, validated, and reused across multiple public signals.

---

## Feature List

| No. | Feature | Primary Role | Main Signals Supported |
|---:|---|---|---|
| 1 | [NDVI](01_ndvi.md) | Vegetation vigor and greenness | Crop health, pest/disease risk support |
| 2 | [NDWI](02_ndwi.md) | Crop/canopy water condition | Crop health, moisture stress |
| 3 | [LST](03_lst.md) | Thermal and surface heat condition | Crop health, heat stress, moisture stress support |
| 4 | [Rainfall](04_rainfall.md) | Recent and seasonal water availability | Moisture stress, crop health, pest/disease risk support |
| 5 | [Crop Stage](05_crop_stage.md) | Stage-aware interpretation layer | Crop health, heat stress, pest/disease risk, campaign timing |
| 6 | [Trend Analysis](06_trend_analysis.md) | Direction and worsening/improving behavior | Crop health, moisture stress, heat stress |
| 7 | [Historical Baseline](07_historical_baseline.md) | Localized dynamic thresholds | All crop/weather/satellite signals |
| 8 | [Pest Advisory](08_pest_advisory.md) | Public pest/disease advisory evidence | Pest/disease risk |
| 9 | [Weather Context](09_weather_context.md) | Supporting weather conditions | Moisture stress, heat stress, pest/disease risk |
| 10 | [Geography Boundaries](10_geography_boundaries.md) | Spatial matching and aggregation | All public-private geography joins |

---

## Design Principle

These features should not be interpreted through universal fixed thresholds.

Preferred interpretation:

```text
current observation
vs
historical baseline
for the same geography + crop + crop stage + season/week
```

This keeps the signal layer crop-aware, stage-aware, geography-aware, and explainable.

---

## Current Phase 2 Scope

The first pure public-data signal pass focuses on:

1. Crop health signal
2. Moisture stress signal
3. Heat stress signal
4. Pest/disease risk signal

Campaign timing and territory priority can later consume these signals as downstream decision-layer inputs.
