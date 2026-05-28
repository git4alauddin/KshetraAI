# Crop Stage Feature

## Quick Brief

Crop stage represents the estimated biological stage of a crop on a given date and geography.

For KshetraAI, crop stage is used to interpret whether satellite and weather behavior is expected or concerning.

The same NDVI, NDWI, LST, or rainfall condition can mean different things depending on crop stage.

---

## Why Crop Stage Matters

Crop stage gives biological context.

Example:

```text
Falling NDVI during harvest may be normal.
Falling NDVI during vegetative growth may be anomalous.
```

So crop stage helps answer:

```text
Is this signal normal for this crop at this point in the season?
```

---

## Required Inputs

| Input | Requirement |
|---|---|
| Crop name | Required to identify the crop calendar |
| Season | Required where crop calendars differ by season |
| Geography | Required because stage timing can vary by region |
| Observation date | Required to map date into stage window |
| Crop calendar | Required source for sowing, stage, and harvest windows |
| Actual sowing date | Optional but improves accuracy when available |

---

## Crop Calendar Inputs

Crop calendar should provide:

- crop
- geography
- season
- sowing window
- stage windows
- harvest window
- stage names

Preferred calendar grain:

```text
crop + state/district/tehsil + season
```

If tehsil-level calendar is unavailable, use district or state-level calendar with a lower confidence label.

---

## Standard Stage Categories

For the public signal layer, use a small standard set of stages.

| Stage | Meaning |
|---|---|
| `sowing_establishment` | Sowing, germination, early establishment |
| `vegetative_tillering` | Vegetative growth, tillering, canopy development |
| `flowering_reproductive` | Flowering, reproductive stage, pod/grain formation |
| `maturity` | Crop maturing and senescence beginning |
| `harvest` | Harvest window or post-maturity condition |
| `unknown` | Stage cannot be confidently estimated |

Crop-specific calendars can map their local stage names into these standard categories.

---

## Stage Derivation Logic

Basic logic:

```text
crop
+ geography
+ season
+ observation_date
-> crop_stage
```

If actual sowing date is available:

```text
actual_sowing_date
+ crop growth duration
+ observation_date
-> more accurate crop_stage
```

If actual sowing date is not available:

```text
regional crop calendar window
+ observation_date
-> estimated crop_stage
```

---

## Stage Confidence

Crop stage should include a confidence level.

| Confidence | Meaning |
|---|---|
| `high` | Actual sowing date or highly local calendar available |
| `medium` | District/tehsil crop calendar available |
| `low` | Broad state/regional calendar only |
| `unknown` | Crop stage cannot be estimated reliably |

This prevents overclaiming when crop-stage data is approximate.

---

## Stage Sensitivity

Crop stage modifies how strongly stress evidence should matter.

| Stage | Sensitivity | Interpretation |
|---|---|---|
| `sowing_establishment` | Medium-high | Moisture deficit or heat can affect establishment. |
| `vegetative_tillering` | Medium | Stress can affect growth and canopy development. |
| `flowering_reproductive` | High | Stress can be high-impact and should raise concern. |
| `maturity` | Low-medium | Some decline may be normal, depending on crop. |
| `harvest` | Low for crop-health stress | Declining vegetation may be normal; rainfall may matter for operations. |
| `unknown` | Neutral | Do not upgrade/downgrade signal aggressively. |

---

## Expected Signal Behavior By Stage

| Stage | NDVI Expectation | NDWI Expectation | LST Sensitivity | Rainfall Sensitivity |
|---|---|---|---|---|
| `sowing_establishment` | Low but should begin rising | Moisture important | Medium | High |
| `vegetative_tillering` | Rising / high | Normal to high | Medium-high | Medium-high |
| `flowering_reproductive` | Stable-high | Normal to high | High | High |
| `maturity` | Declining | Declining may be normal | Medium | Medium-low |
| `harvest` | Low / declining | Low / declining may be normal | Low for crop health | Excess rainfall may affect operations |
| `unknown` | Unknown | Unknown | Neutral | Neutral |

---

## How Crop Stage Modifies Signal Interpretation

Crop stage should not directly create crop stress by itself.

It should modify interpretation of other features.

Example:

```text
NDVI = Very Low
Stage = Sowing
Interpretation = may be normal
```

```text
NDVI = Very Low
Stage = Vegetative
Interpretation = anomaly risk
```

```text
LST = Very High
Stage = Flowering
Interpretation = high heat-stress concern
```

```text
LST = Very High
Stage = Harvest
Interpretation = lower crop-health concern, but possible field-operation concern
```

---

## Stage Modifier Logic

Recommended modifier:

| Stage Sensitivity | Modifier |
|---|---|
| High | Upgrade stress concern by one level if supporting evidence exists |
| Medium-high | Upgrade only if moisture/thermal evidence is strong |
| Medium | Keep base level |
| Low-medium | Keep or downgrade depending on expected senescence |
| Low | Downgrade crop-health stress concern |
| Unknown | Keep base level but lower confidence |

Important:

```text
Crop stage should modify evidence. It should not override all evidence.
```

---

## Feature Output

Recommended crop stage feature fields:

| Field | Meaning |
|---|---|
| `geography_id` | Tehsil or district identifier |
| `geography_level` | Tehsil or district |
| `crop` | Crop name |
| `season` | Crop season |
| `observation_date` | Date being evaluated |
| `crop_stage` | Standardized crop stage |
| `stage_start_date` | Estimated start date of stage |
| `stage_end_date` | Estimated end date of stage |
| `stage_sensitivity` | Low, medium, medium-high, or high |
| `stage_confidence_level` | High, medium, low, or unknown |
| `stage_source` | Crop calendar source or derivation source |
| `actual_sowing_date_available` | Whether exact sowing date was available |

---

## Signals That Use Crop Stage

Crop stage is used by:

- Crop Health Signal
- Heat Stress Signal
- Pest / Disease Risk Signal

It may also support:

- Moisture Stress Signal
- Campaign Timing Signal
- spray suitability context
- explainability outputs

---

## Explainability Example

```text
The crop is estimated to be in flowering/reproductive stage.
This is a high-sensitivity stage, so low NDWI and high LST are treated
as stronger crop stress evidence than they would be near harvest.
```

---

## Current Caution

Crop stage is an estimated feature unless actual sowing date or field-level crop calendar data is available.

It should be used to guide interpretation, not as a perfect biological truth.
