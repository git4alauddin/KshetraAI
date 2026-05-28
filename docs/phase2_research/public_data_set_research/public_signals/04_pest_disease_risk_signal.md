# Pest / Disease Risk Signal

## Quick Brief

The Pest / Disease Risk Signal estimates whether a crop geography has elevated pest or disease risk based on public advisory evidence and supporting environmental context.

It combines pest advisories, crop match, geography match, advisory recency, crop stage, weather context, and unexplained vegetation anomalies.

This signal should help answer:

```text
Is there public-data-backed evidence that this crop geography should be monitored for pest or disease risk?
```

It should not be treated as confirmed pest detection.

---

## Features Used

| Feature | Source Type | What It Represents | Why It Matters |
|---|---|---|---|
| Pest advisory | Public bulletin / advisory | Recent pest or disease warning for crop/geography | Primary evidence source for risk. |
| Crop stage | Crop calendar | Current biological stage | Some pests/diseases are more relevant at specific stages. |
| Weather context | Weather | Humidity, rainfall, heat, wetness, dry spell | Supports whether conditions are favorable for pest/disease pressure. |
| NDVI / NDWI anomaly | Satellite | Vegetation or moisture behavior not explained by drought/heat alone | Can support investigation when advisory and crop context align. |
| Historical baseline | Derived public-data baseline | Expected vegetation/moisture behavior | Helps identify abnormal vegetation behavior. |
| Trend analysis | Time series | Worsening vegetation/moisture pattern | Helps identify whether anomalies are emerging or persistent. |
| Geography boundaries | Administrative geography | Advisory-to-territory matching | Ensures risk is shown at the right district/tehsil grain. |

---

## Signal Purpose

The Pest / Disease Risk Signal should identify geographies where a rep or agronomic team may need to monitor, verify, or respond to pest/disease risk.

It should support:

- pest/disease alerting
- field verification prioritization
- crop-protection campaign timing
- explanation-backed next best action context
- territory prioritization where risk evidence is current and relevant

Recommended operating grain:

```text
District -> Tehsil where available
```

Most pest advisories may be district or block level, so the signal must preserve geography confidence.

---

## Core Question

The signal should answer:

```text
Is there recent, crop-relevant, geography-relevant advisory evidence supported by stage or weather context?
```

This means the signal is not asking only:

```text
Did NDVI fall?
```

or:

```text
Was a pest name mentioned somewhere?
```

It is asking:

```text
Does the advisory match the crop and geography, is it recent, and do crop stage or weather conditions make it relevant?
```

---

## Recommended Input Grain

| Input | Recommended Grain | Notes |
|---|---|---|
| Pest advisory | District / tehsil / crop / date | Primary public evidence |
| Crop stage | Crop / geography / date | Determines sensitivity/relevance |
| Weather context | District / tehsil / date window | Humidity, rainfall, wet spell, heat, dry spell |
| NDVI / NDWI anomaly | Tehsil / district / crop / date | Supporting evidence only |
| Historical baseline | Geography / crop / stage / week or season | Used for vegetation anomaly interpretation |
| Trend | Geography / crop / recent observations | Used to identify worsening unexplained pattern |
| Boundary confidence | Geography | Controls precision and confidence |

---

## Advisory Match Logic

Pest advisory evidence should first be filtered and scored for relevance.

Strong advisory evidence:

```text
advisory active
+ crop match true
+ geography match exact or district/tehsil match
+ pest/disease named
+ advisory severity available or language indicates concern
= strong advisory evidence
```

Weak advisory evidence:

```text
advisory stale
+ crop match unknown
+ broad state-level geography
+ severity unknown
= weak advisory evidence
```

Expired or irrelevant advisories should not create high pest risk.

---

## Recency Logic

Advisory relevance should decay over time.

Example MVP recency labels:

| Days Since Advisory | Recency Label | Use |
|---:|---|---|
| 0-7 | Recent | Strong evidence |
| 8-21 | Active | Usable evidence |
| 22-45 | Stale | Weak evidence |
| 46+ | Expired | Usually not active |

Exact windows can later become configurable by crop, pest, geography, or advisory source.

---

## Crop And Geography Match Logic

The signal should preserve both crop match and geography match.

Crop match:

| Match | Meaning |
|---|---|
| `true` | Advisory crop matches target crop |
| `false` | Advisory crop does not match |
| `unknown` | Crop is broad, missing, or not confidently parsed |

Geography match:

| Match Level | Meaning |
|---|---|
| `exact` | Tehsil/block/local geography match |
| `district` | District-level match |
| `state` | State-level match only |
| `broad` | Broad regional advisory |
| `unknown` | Match cannot be confirmed |

Risk should be strongest when crop and geography both match well.

---

## Weather And Stage Support

Weather and crop stage should support, not replace, advisory evidence.

Stronger pest/disease risk pattern:

```text
active pest advisory
+ crop match
+ district/tehsil geography match
+ sensitive crop stage
+ recent wet/humid weather or pest-favorable conditions
= stronger pest/disease risk
```

Weaker pattern:

```text
active advisory
+ crop match
+ dry/unfavorable weather
+ crop stage not sensitive
= lower risk or watchlist
```

Crop-stage and weather support should raise confidence/severity only when advisory evidence is relevant.

---

## Vegetation Anomaly Support

NDVI or NDWI anomalies can support pest/disease risk only when other explanations are weak or already accounted for.

Example:

```text
NDVI falling
+ no strong rainfall deficit
+ no strong heat/moisture explanation
+ active crop-matched advisory
= possible pest/disease investigation support
```

But vegetation anomaly alone should not create a pest signal.

Do not infer pest pressure from NDVI alone.

---

## Component Flags

Create interpretable flags before final scoring.

| Flag | Trigger Logic |
|---|---|
| `advisory_active_flag` | Advisory is recent or active |
| `crop_match_flag` | Advisory crop matches target crop |
| `geography_match_flag` | Advisory geography matches target geography or fallback geography |
| `advisory_severity_flag` | Advisory severity is moderate/high or wording indicates concern |
| `sensitive_stage_flag` | Crop is in a pest/disease-sensitive stage |
| `weather_favorable_flag` | Weather context supports pest/disease risk |
| `unexplained_vegetation_anomaly_flag` | NDVI/NDWI anomaly exists without clear drought/heat explanation |
| `baseline_low_confidence_flag` | Historical baseline is weak or broad fallback |
| `boundary_low_confidence_flag` | Geography match or boundary quality is weak |

These flags should be kept in output for explainability.

---

## Scoring Logic

For MVP design, use transparent additive scoring.

| Component | Score |
|---|---:|
| Active pest/disease advisory | +2 |
| Crop match is true | +1 |
| Geography match is exact or district/tehsil level | +1 |
| Advisory severity is moderate/high | +1 |
| Sensitive crop stage active | +1 |
| Weather favorable for pest/disease risk | +1 |
| Unexplained vegetation anomaly active | +1 |

Rationale:

- Advisory is the primary evidence.
- Crop/geography match determines relevance.
- Stage and weather determine whether risk is timely.
- Vegetation anomaly is supporting evidence only.

Do not add score for weak boundary or baseline confidence. Use those to lower confidence.

---

## Final Signal Labels

Recommended output labels:

| Score | Pest / Disease Risk Signal |
|---:|---|
| 0-1 | Normal |
| 2-3 | Pest Watch |
| 4+ | Possible Pest/Disease Risk |

If advisory evidence is missing but satellite/weather anomalies exist:

```text
No Advisory-Backed Pest Evidence
```

may be safer than producing pest risk.

If too many inputs are missing:

```text
Insufficient Evidence
```

should be allowed as a safe output.

---

## Confidence Logic

Signal confidence should be separate from risk level.

Recommended confidence factors:

| Confidence Factor | Impact |
|---|---|
| Advisory source is known and recent | Raises confidence |
| Crop match is true | Raises confidence |
| Geography match is exact or district/tehsil-level | Raises confidence |
| Advisory has severity or clear wording | Raises confidence |
| Weather context is available | Raises confidence |
| Crop stage is known clearly | Raises confidence |
| Advisory is stale | Lowers confidence |
| Crop match is unknown | Lowers confidence |
| Geography match is broad/state-only | Lowers confidence |
| Advisory was manually parsed with limited detail | Lowers confidence |

Recommended labels:

```text
high
medium
low
```

Example:

```text
Possible Pest/Disease Risk + Medium Confidence
```

is valid when advisory evidence is active but geography is district-level rather than tehsil-level.

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
| `pest_disease_risk_score` | Additive risk score |
| `pest_disease_risk_label` | Normal, Pest Watch, Possible Pest/Disease Risk, No Advisory-Backed Pest Evidence, or Insufficient Evidence |
| `signal_confidence` | High, medium, or low |
| `advisory_id` | Linked advisory record, if available |
| `pest_or_disease` | Pest/disease named in advisory |
| `advisory_recency_label` | Recent, active, stale, or expired |
| `advisory_active_flag` | Whether advisory is considered active |
| `crop_match_flag` | Whether advisory crop matches |
| `geography_match_flag` | Whether advisory geography matches |
| `geography_match_level` | Exact, district, state, broad, or unknown |
| `advisory_severity_level` | Low, moderate, high, or unknown |
| `sensitive_stage_flag` | Whether crop stage is sensitive/relevant |
| `weather_favorable_flag` | Whether weather supports pest/disease risk |
| `unexplained_vegetation_anomaly_flag` | Whether vegetation anomaly supports investigation |
| `boundary_confidence` | Confidence in geography match |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

The explanation should show:

1. Whether risk is normal, watchlist, or possible pest/disease risk.
2. Which advisory evidence contributed.
3. Whether crop and geography matched.
4. Whether weather/stage strengthened the risk.
5. Whether satellite anomaly is supporting evidence only.

Example:

```text
Pest/disease risk is marked as Possible Risk because a recent cotton advisory is active for the district, the crop matches, the crop is in a sensitive stage, and recent wet weather supports monitoring.
```

Satellite-supported example:

```text
Vegetation anomaly is used only as supporting evidence because NDVI is falling without a strong rainfall or heat explanation, and there is an active crop-matched advisory.
```

Lower-confidence example:

```text
Pest risk is marked as Pest Watch, but confidence is low because the advisory is broad state-level guidance and crop match is not fully confirmed.
```

---

## Business Use

This signal can help:

- prioritize pest/disease monitoring visits
- support insecticide or fungicide campaign timing
- explain why a territory needs attention even before sales signals change
- connect public advisory evidence to field-force planning
- improve next best action relevance with advisory-backed context

---

## Current Caution

Pest / Disease Risk Signal should not be described as:

```text
confirmed pest outbreak
```

or:

```text
confirmed disease incidence at retailer/farm level
```

Preferred wording:

```text
advisory-backed pest/disease risk
```

or:

```text
public-data-backed pest/disease monitoring signal
```

The signal should guide prioritization and field verification, not replace surveillance or agronomic inspection.
