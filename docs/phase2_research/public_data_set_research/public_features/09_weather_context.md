# Weather Context Feature

## Quick Brief

Weather context combines recent and forecast environmental conditions that help interpret public agricultural signals.

For KshetraAI, weather context should not be treated as a standalone diagnosis. It should act as supporting evidence for crop health, moisture stress, heat stress, and pest/disease risk signals.

This feature is especially useful when satellite indicators show stress and we need to understand whether recent weather can explain it.

---

## What Weather Context Represents

Weather context can help describe:

- recent heat condition
- recent rainfall condition
- humidity or wetness condition
- dry-spell context
- wet-spell context
- pest/disease-favorable environment
- short-term weather risk for field action timing

---

## What Weather Context Does Not Prove Alone

Weather context alone does not prove:

- confirmed crop stress
- confirmed pest or disease incidence
- actual field-level soil moisture
- actual irrigation availability
- exact crop loss
- exact retailer-level product demand

It should be interpreted with:

- NDVI
- NDWI
- LST
- rainfall
- crop stage
- pest advisories
- historical baseline
- geography-level aggregation

---

## Expected Source Types

Weather context may come from:

- IMD weather data or advisories
- agromet advisories
- public gridded weather datasets
- rainfall products such as CHIRPS or GPM
- forecast APIs, where allowed
- local station observations, where available

For Phase 2 research, the source should be selected based on availability, coverage, update frequency, and license suitability.

---

## Core Weather Fields

Recommended weather fields:

| Field | Meaning |
|---|---|
| `observation_date` | Date of weather observation or forecast |
| `geography_id` | Target geography, preferably tehsil or district |
| `temperature_max_c` | Maximum temperature in Celsius |
| `temperature_min_c` | Minimum temperature in Celsius |
| `relative_humidity_pct` | Relative humidity percentage, if available |
| `rainfall_mm` | Rainfall amount in millimeters |
| `wind_speed_kmph` | Wind speed, if available |
| `weather_source` | Source dataset or API |
| `weather_quality_flag` | Missing, estimated, observed, forecast, or low confidence |

Not every source will provide every field. Missing fields should remain null instead of being invented.

---

## Derived Weather Features

Weather context should be converted into derived fields that are easier for signals to consume.

| Derived Field | Meaning |
|---|---|
| `recent_rainfall_3d_mm` | Rainfall over the last 3 days |
| `recent_rainfall_7d_mm` | Rainfall over the last 7 days |
| `recent_rainfall_14d_mm` | Rainfall over the last 14 days |
| `rainfall_deficit_flag` | Whether rainfall is below expected baseline |
| `rainfall_surplus_flag` | Whether rainfall is above expected baseline |
| `dry_spell_days` | Consecutive days with very low or no rainfall |
| `wet_spell_days` | Consecutive rainy or high-humidity days |
| `heat_risk_flag` | Whether temperature/LST context suggests heat risk |
| `humidity_favorable_flag` | Whether humidity/wetness may favor pest or disease risk |
| `weather_context_confidence` | High, medium, or low confidence |

---

## Historical Baseline Logic

Weather should be interpreted relative to local seasonal behavior.

Avoid fixed universal rules like:

```text
rainfall_7d < 10 mm = drought
```

Preferred baseline key:

```text
geography + crop + crop_stage + week_or_season + weather_feature
```

Examples:

```text
Ludhiana_T004 + wheat + vegetative_tillering + week_08 + rainfall_7d
Wardha_T002 + cotton + flowering_reproductive + week_31 + temperature_max
```

Baseline comparison helps decide whether current weather is normal, dry, wet, hot, or unusually variable for that crop-stage context.

---

## Crop-Stage Interpretation

The same weather condition can have different meaning depending on crop stage.

Example:

| Condition | Stage | Interpretation |
|---|---|---|
| High heat | Flowering/reproductive | Higher sensitivity |
| High heat | Harvest | May be less concerning |
| Rainfall deficit | Vegetative | Moisture stress support |
| Rainfall deficit | Harvest | May be normal or less harmful |
| High humidity and rainfall | Sensitive disease stage | Pest/disease risk support |

Crop stage should therefore modify the severity of the weather context signal.

---

## Pest/Disease Risk Support

Weather context can strengthen pest or disease risk only when combined with other evidence.

Example stronger pattern:

```text
active pest advisory
+ crop match
+ geography match
+ sensitive crop stage
+ recent wet/humid conditions
= stronger pest/disease risk evidence
```

Example weaker pattern:

```text
active pest advisory
+ no crop match
+ dry weather
+ stale advisory
= weak pest/disease risk evidence
```

Weather should support risk reasoning, not replace advisory or field evidence.

---

## Feature Output

Recommended output fields:

| Field | Meaning |
|---|---|
| `geography_id` | Target geography |
| `crop_id` | Crop, if crop-specific interpretation is used |
| `crop_stage` | Current crop stage |
| `weather_window_start` | Start of weather aggregation window |
| `weather_window_end` | End of weather aggregation window |
| `rainfall_7d_mm` | Seven-day rainfall |
| `rainfall_14d_mm` | Fourteen-day rainfall |
| `rainfall_baseline_label` | Very low, low-normal, normal, high-normal, or very high |
| `temperature_baseline_label` | Very low, low-normal, normal, high-normal, or very high |
| `dry_spell_days` | Consecutive dry days |
| `wet_spell_days` | Consecutive wet days |
| `heat_context_label` | Normal, warm, hot, or extreme |
| `humidity_context_label` | Low, normal, high, or unknown |
| `pest_weather_support_flag` | Whether weather supports pest/disease risk reasoning |
| `weather_context_confidence` | High, medium, or low |
| `weather_source` | Source dataset/API |

---

## Signals That Use Weather Context

Weather context can support:

- crop health signal
- moisture stress signal
- heat stress signal
- pest/disease risk signal
- campaign timing signal
- territory priority signal

For the first pure public-data pass, it is most important for:

- moisture stress
- heat stress
- pest/disease risk

---

## Explainability Example

Example explanation text:

```text
Weather context increased risk confidence because the territory has recent rainfall deficit, elevated heat context, and the crop is currently in a sensitive growth stage.
```

For pest/disease context:

```text
Weather context supports pest-risk monitoring because recent wet conditions align with an active advisory for the crop and geography.
```

---

## Current Caution

Weather context should stay conservative.

Do not say:

```text
weather confirms pest outbreak
```

Prefer:

```text
weather conditions support pest-risk monitoring
```

or:

```text
recent weather may explain part of the observed crop stress signal
```
