# Territory Priority Signal

## Quick Brief

The Territory Priority Signal converts core public signals and campaign timing into a higher-level public-context priority label for a geography.

This is a decision-layer public signal.

It does not replace the existing KshetraAI priority engine. It provides a public-data-backed priority context that can later be joined with private demand, inventory, visit, and retailer signals.

This signal should help answer:

```text
Which territory or geography deserves higher attention based on public agronomic risk?
```

---

## Signal Type

```text
Decision-layer public signal
```

This signal should be generated after the core public signals and campaign timing signal are available.

Core public signals it consumes:

- Crop Health Signal
- Moisture Stress Signal
- Heat Stress Signal
- Pest / Disease Risk Signal
- Campaign Timing Signal

---

## Inputs Used

| Input | Type | What It Represents | Why It Matters |
|---|---|---|---|
| Crop Health Signal | Core public signal | Overall crop condition risk | Strong public risk context for prioritization. |
| Moisture Stress Signal | Core public signal | Water/moisture stress risk | Helps prioritize drying or deficit geographies. |
| Heat Stress Signal | Core public signal | Thermal stress risk | Helps prioritize heat-sensitive geographies. |
| Pest / Disease Risk Signal | Core public signal | Advisory-backed pest/disease risk | Strong reason for monitoring or follow-up. |
| Campaign Timing Signal | Decision-layer public signal | Whether action timing is relevant | Helps separate urgent windows from low-action periods. |
| Signal confidence | Public signal metadata | Reliability of evidence | Prevents weak evidence from over-driving priority. |
| Geography boundaries | Public feature | Tehsil/district mapping | Controls operating grain and explainability. |

---

## Signal Purpose

The Territory Priority Signal should summarize public agronomic risk into one priority context label that downstream engines can consume.

It should support:

- territory prioritization
- daily planning context
- alert grouping
- explanation-backed public risk summary
- joining public risk with private retailer opportunity signals

Recommended operating grain:

```text
Tehsil -> District -> Territory mapping
```

If territory boundaries are not exact, the signal should preserve the geography level and confidence.

---

## Core Question

The signal should answer:

```text
How important is this geography right now based on public risk signals?
```

This means the signal is not asking:

```text
Which retailer should be visited?
```

It is asking:

```text
Which geography has public-risk context that should influence downstream prioritization?
```

Retailer-level priority should come later after joining private signals.

---

## Priority Scoring Logic

Recommended transparent scoring:

| Component | Score |
|---|---:|
| Crop Health Signal = High Stress | +3 |
| Crop Health Signal = Moderate Stress | +2 |
| Moisture Stress Signal = Severe Moisture Stress | +2 |
| Heat Stress Signal = Severe Heat Stress | +2 |
| Pest / Disease Risk Signal = Possible Pest/Disease Risk | +3 |
| Pest / Disease Risk Signal = Pest Watch | +1 |
| Campaign Timing Signal = Urgent Window | +2 |
| Campaign Timing Signal = Right Window | +1 |
| Recovery/improving trend present | -1 |

Only medium/high confidence signals should strongly affect scoring.

Low-confidence signals may be included in evidence, but should not create urgent priority by themselves.

---

## Final Signal Labels

Recommended output labels:

| Score | Territory Priority Signal |
|---:|---|
| 0-2 | Low Priority |
| 3-5 | Medium Priority |
| 6-8 | High Priority |
| 9+ | Urgent Priority |

If evidence is weak or unavailable:

```text
Unknown / Low Confidence
```

should be allowed.

---

## Confidence Logic

Priority confidence should combine the confidence of contributing public signals.

Recommended confidence factors:

| Confidence Factor | Impact |
|---|---|
| Multiple public signals agree | Raises confidence |
| Core public signals are medium/high confidence | Raises confidence |
| Geography match is tehsil or district-level reliable | Raises confidence |
| Pest advisory has crop/geography match | Raises confidence |
| Only one weak signal is active | Lowers confidence |
| Most signals use broad fallback geography | Lowers confidence |
| Crop stage unknown | Lowers confidence |

Recommended confidence labels:

```text
high
medium
low
```

---

## Component Flags

Create interpretable flags before final label.

| Flag | Trigger Logic |
|---|---|
| `crop_stress_priority_flag` | Crop Health Signal is Moderate/High Stress |
| `moisture_priority_flag` | Moisture Stress Signal is Severe |
| `heat_priority_flag` | Heat Stress Signal is Severe |
| `pest_priority_flag` | Pest / Disease Risk Signal is Pest Watch or Possible Risk |
| `urgent_timing_flag` | Campaign Timing Signal is Urgent Window |
| `recovery_trend_flag` | Trend indicates recovery/improvement |
| `low_confidence_public_context_flag` | Public evidence is weak or broad |

---

## Recommended Output Fields

| Field | Meaning |
|---|---|
| `signal_id` | Internal signal record ID |
| `signal_date` | Date of signal generation |
| `geography_id` | Operating geography |
| `geography_level` | Tehsil, district, territory mapping, etc. |
| `crop_id` | Crop being evaluated, if crop-specific |
| `territory_public_priority_score` | Additive public priority score |
| `territory_public_priority_label` | Low, Medium, High, Urgent, or Unknown / Low Confidence |
| `signal_confidence` | High, medium, or low |
| `crop_health_label` | Contributing crop health signal |
| `moisture_stress_label` | Contributing moisture signal |
| `heat_stress_label` | Contributing heat signal |
| `pest_disease_risk_label` | Contributing pest/disease signal |
| `campaign_timing_label` | Contributing timing signal |
| `active_public_signals` | List of active public signals |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

Example:

```text
Territory public priority is High because crop health is Moderate Stress, moisture stress is Severe, and the campaign timing window is urgent for the current crop stage.
```

Pest-driven example:

```text
Territory public priority is Urgent because an advisory-backed pest risk is active, the crop/geography match is strong, and weather context supports monitoring.
```

Low-confidence example:

```text
Territory public priority is Medium, but confidence is low because the public signals are available only at district-level fallback.
```

---

## Business Use

This signal can help:

- prioritize geographies before retailer-level joining
- summarize public risk for daily planning
- guide alert grouping by district/tehsil
- support field-force planning with agronomic context
- prepare a clean join into private opportunity signals

---

## Current Caution

Territory Priority Signal should not be described as final retailer priority.

Avoid:

```text
this retailer must be visited because public priority is high
```

Prefer:

```text
this geography has high public-risk priority and should influence downstream visit planning
```

Final visit priority should combine this with private signals such as POS, inventory, visit recency, retailer assignment, and outcome history.
