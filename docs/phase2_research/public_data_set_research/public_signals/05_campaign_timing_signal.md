# Campaign Timing Signal

## Quick Brief

The Campaign Timing Signal estimates whether a campaign, advisory, or product-focused field action is timely for a crop geography.

This is a decision-layer public signal.

It does not come directly from one raw public feature. It consumes crop stage, weather context, pest advisories, and the core public signals to decide whether the current window is too early, right, late, or urgent.

This signal should help answer:

```text
Is this the right time to act for this crop, geography, and risk context?
```

---

## Signal Type

```text
Decision-layer public signal
```

This signal should be generated after the core public signals are available.

Core public signals it may consume:

- Crop Health Signal
- Moisture Stress Signal
- Heat Stress Signal
- Pest / Disease Risk Signal

---

## Features And Signals Used

| Input | Type | What It Represents | Why It Matters |
|---|---|---|---|
| Crop stage | Public feature | Current biological stage | Determines whether campaign/advisory timing is appropriate. |
| Weather context | Public feature | Recent or forecast weather | Helps avoid poor timing or identify urgent windows. |
| Pest advisory | Public feature | Active pest/disease warning | Can create urgent campaign or field verification window. |
| Crop Health Signal | Core public signal | Crop condition risk | Helps determine whether intervention is timely. |
| Moisture Stress Signal | Core public signal | Moisture stress risk | Supports water-stress-aware advisory timing. |
| Heat Stress Signal | Core public signal | Thermal pressure risk | Supports heat-aware advisory timing. |
| Pest / Disease Risk Signal | Core public signal | Advisory-backed pest/disease risk | Supports crop-protection campaign timing. |

---

## Signal Purpose

The Campaign Timing Signal should prevent action from being recommended at the wrong crop or risk window.

It should support:

- timely field-force action
- better campaign conversion
- stage-aware recommendations
- advisory-backed urgency
- fewer premature or stale campaign pushes

This signal is not a replacement for the recommendation engine. It is timing context consumed by recommendation and prioritization logic.

---

## Core Question

The signal should answer:

```text
Given crop stage and public risk context, is action timely now?
```

This means the signal is not asking:

```text
Is there a campaign available?
```

It is asking:

```text
Is the crop/risk/weather window appropriate for action?
```

---

## Recommended Input Grain

| Input | Recommended Grain | Notes |
|---|---|---|
| Crop stage | Crop / geography / date | Primary timing anchor |
| Pest advisory | District / tehsil / crop / date | Can make timing urgent |
| Weather context | District / tehsil / date window | Helps support or suppress timing |
| Crop health signal | Geography / crop / date | Context for stress-related timing |
| Moisture stress signal | Geography / crop / date | Context for water-stress timing |
| Heat stress signal | Geography / crop / date | Context for heat-aware timing |
| Pest/disease risk signal | Geography / crop / date | Context for crop-protection timing |

Recommended operating grain:

```text
Tehsil -> District fallback
```

---

## Timing Logic

Campaign timing should be interpreted from crop stage plus active risk context.

Basic timing labels:

| Label | Meaning |
|---|---|
| `too_early` | Crop is before the useful action window |
| `right_window` | Crop is in the expected useful action window |
| `late_window` | Crop has passed the ideal action window |
| `urgent_window` | Active risk/advisory/weather context makes timely action important |
| `insufficient_evidence` | Timing cannot be confidently determined |

---

## Example Interpretation

Example:

```text
Crop stage = flowering_reproductive
Pest / Disease Risk = Possible Pest/Disease Risk
Weather = wet/humid support
= Urgent Window
```

Example:

```text
Crop stage = sowing_establishment
Campaign designed for flowering stage
= Too Early
```

Example:

```text
Crop stage = harvest
Pest advisory stale
= Late Window or No Timely Action
```

---

## Component Flags

Create interpretable flags before final label.

| Flag | Trigger Logic |
|---|---|
| `crop_stage_right_window_flag` | Crop stage matches useful action window |
| `crop_stage_too_early_flag` | Crop is before useful action window |
| `crop_stage_late_flag` | Crop is past useful action window |
| `active_advisory_flag` | Pest/weather advisory is active and relevant |
| `public_risk_urgent_flag` | Pest, crop health, moisture, or heat risk is high enough to require attention |
| `weather_timing_support_flag` | Weather supports action timing |
| `weather_timing_blocker_flag` | Weather makes action timing unsuitable |
| `timing_low_confidence_flag` | Crop stage, weather, or advisory evidence is weak |

---

## Label Logic

Recommended first-pass logic:

| Condition | Campaign Timing Label |
|---|---|
| Crop stage before action window | Too Early |
| Crop stage in action window and no urgent risk | Right Window |
| Crop stage past action window | Late Window |
| Active advisory or high public risk during relevant crop stage | Urgent Window |
| Crop stage or risk evidence missing | Insufficient Evidence |

If multiple conditions apply, urgent risk should override normal `right_window`.

Example:

```text
right_window + active pest advisory
= urgent_window
```

---

## Confidence Logic

Signal confidence should be separate from timing label.

Recommended confidence factors:

| Confidence Factor | Impact |
|---|---|
| Crop stage known clearly | Raises confidence |
| Public risk signal has medium/high confidence | Raises confidence |
| Advisory is recent and crop/geography matched | Raises confidence |
| Weather context is available and relevant | Raises confidence |
| Crop stage estimated from broad calendar only | Lowers confidence |
| Advisory stale or broad geography only | Lowers confidence |
| Weather forecast/source is missing | Lowers confidence |

Recommended confidence labels:

```text
high
medium
low
```

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
| `campaign_timing_label` | Too Early, Right Window, Late Window, Urgent Window, or Insufficient Evidence |
| `signal_confidence` | High, medium, or low |
| `crop_stage_right_window_flag` | Whether crop stage is suitable |
| `active_advisory_flag` | Whether relevant advisory is active |
| `public_risk_urgent_flag` | Whether public risk makes action urgent |
| `weather_timing_support_flag` | Whether weather supports timing |
| `weather_timing_blocker_flag` | Whether weather blocks timing |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

Example:

```text
Campaign timing is marked as Urgent Window because the crop is in a relevant stage, pest risk is active, and recent weather supports monitoring.
```

Example:

```text
Campaign timing is marked as Too Early because the crop has not yet reached the target stage for this action.
```

---

## Business Use

This signal can help:

- avoid premature campaigns
- identify urgent advisory windows
- improve next best action timing
- increase campaign relevance
- support public-signal-backed field-force planning

---

## Current Caution

Campaign Timing Signal should not claim:

```text
this campaign will convert
```

or:

```text
product need is confirmed
```

Preferred wording:

```text
timing appears relevant based on crop stage and public risk context
```

or:

```text
public context suggests an urgent action window
```
