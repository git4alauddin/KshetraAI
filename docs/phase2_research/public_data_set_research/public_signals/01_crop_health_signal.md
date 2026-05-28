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
