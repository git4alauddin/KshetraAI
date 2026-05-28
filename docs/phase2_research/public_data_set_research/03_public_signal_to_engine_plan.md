# Public Signal To Engine Plan

## Quick Brief

This document defines how Phase 2 public-data signals should connect to the existing KshetraAI decision workflow.

The public signal layer should not replace the current engines. It should enrich them with geography-level agronomic context.

Flow:

```text
public datasets
-> public features
-> public signals
-> existing backend engines
-> API / UI / outcome workflow
```

---

## Public Signals In Scope

The first public-data signal pass has two levels.

### Core Public Signals

These are generated from public features:

| Signal | Role |
|---|---|
| Crop Health Signal | Overall crop condition risk |
| Moisture Stress Signal | Water/moisture stress risk |
| Heat Stress Signal | Thermal pressure risk |
| Pest / Disease Risk Signal | Advisory-backed pest/disease monitoring risk |

### Decision-Layer Public Signals

These are generated after the core public signals are available:

| Signal | Role |
|---|---|
| Campaign Timing Signal | Determines whether a crop/risk action window is too early, right, late, or urgent |
| Territory Priority Signal | Summarizes public agronomic risk into a geography-level priority context |

These signals are geography-level signals.

Recommended grain:

```text
Tehsil -> District fallback
```

---

## Existing Backend Components To Enrich

The public signal layer should connect to these existing backend areas:

| Backend Area | Current Role | Public Signal Use |
|---|---|---|
| Priority Engine | Scores and ranks visit priority | Add agronomic risk/context boosts |
| Recommendation Engine | Produces next best actions | Add public-signal-backed action context |
| Contextual Decision Engine | Selects action based on context | Use public signal state as decision context |
| Anomaly Engine / Alert Generator | Detects and exposes alerts | Convert high-risk public signals into alerts |
| Explainability Engine | Builds reasoning and evidence | Show public evidence and confidence |
| Planning Service / Routes | Serves daily plan workflow | Surface public-risk context in plan items |
| Outcome Service | Captures field outcome | Later validate or correct public signals |

---

## Public Signal Role By Engine

### 1. Priority Engine

Public signals should affect priority as additional context, not as the only ranking source.

Suggested priority impact:

| Public Signal | Priority Impact |
|---|---|
| High Crop Health Stress | Increase territory/retailer visit priority |
| Severe Moisture Stress | Increase priority when crop/stage is sensitive |
| Severe Heat Stress | Increase priority where heat-sensitive crop stage is active |
| Possible Pest/Disease Risk | Strong priority boost if advisory is active and crop/geography match |

Priority changes should preserve explainability.

Example:

```text
Priority increased because public crop-health signal shows Moderate Stress at tehsil level.
```

---

### 2. Recommendation Engine

Public signals should guide the type of next best action.

Suggested mapping:

| Public Signal State | Recommendation Context |
|---|---|
| Crop Health: Watchlist / Moderate / High Stress | Visit or monitor stressed geography |
| Moisture Stress: Emerging / Severe | Discuss water-stress-sensitive advisory or crop support |
| Heat Stress: Heat Risk / Severe | Suggest heat-aware advisory timing |
| Pest Risk: Pest Watch / Possible Risk | Recommend field verification or crop-protection follow-up |

The recommendation should not claim exact product need unless private/internal evidence also supports it.

---

### 3. Contextual Decision Engine

The contextual decision engine can use public signals as environmental/agronomic context.

Example decision context fields:

| Field | Meaning |
|---|---|
| `crop_health_label` | Healthy, Watchlist, Moderate Stress, High Stress |
| `moisture_stress_label` | Normal, Emerging, Severe |
| `heat_stress_label` | Normal, Heat Risk, Severe |
| `pest_disease_risk_label` | Normal, Pest Watch, Possible Risk |
| `public_signal_confidence` | Combined confidence from public evidence |
| `public_signal_evidence_summary` | Short human-readable evidence |

This helps the action selector decide whether the right action is:

- visit
- monitor
- verify in field
- follow up on advisory
- defer if evidence is weak

---

### 4. Anomaly / Alert Engine

Public signals can become alerts when severity and confidence are high enough.

Suggested alert creation rules:

| Public Signal | Alert Trigger |
|---|---|
| Crop Health Signal | Moderate/High Stress with medium/high confidence |
| Moisture Stress Signal | Severe Moisture Stress with medium/high confidence |
| Heat Stress Signal | Severe Heat Stress with medium/high confidence |
| Pest / Disease Risk Signal | Possible Pest/Disease Risk with active advisory and crop/geography match |

Alert wording should remain careful.

Use:

```text
Possible pest/disease risk detected from active public advisory.
```

Avoid:

```text
Pest outbreak confirmed.
```

---

### 5. Explainability Engine

Every public signal consumed by an engine should carry evidence.

Minimum explainability fields:

| Field | Meaning |
|---|---|
| `signal_name` | Public signal name |
| `signal_label` | Final signal label |
| `signal_score` | Transparent score, if available |
| `signal_confidence` | High, medium, or low |
| `geography_level` | Tehsil, district, etc. |
| `feature_evidence` | NDVI, NDWI, LST, rainfall, advisory, etc. |
| `caution_note` | Limits of interpretation |

Example explanation:

```text
Priority was increased because the tehsil has Moderate Crop Health Stress. NDVI and NDWI are below expected range for the current crop stage, and rainfall deficit supports the stress interpretation.
```

---

### 6. Planning Service / Daily Plan

The daily plan should surface public signals as context on ranked plan items.

Potential UI/API additions:

| Field | Meaning |
|---|---|
| `public_risk_summary` | Short summary of relevant public signals |
| `active_public_signals` | List of active public signal labels |
| `public_signal_confidence` | Overall confidence |
| `public_signal_evidence` | Short evidence list |

Example:

```text
Public context: Moderate crop stress and emerging moisture stress in the retailer's operating tehsil.
```

---

### 7. Outcome Feedback

Outcome capture can later validate public signals.

Potential feedback examples:

| Field Outcome | Future Use |
|---|---|
| Rep confirms crop stress | Strengthen confidence in similar future signal patterns |
| Rep says no visible stress | Mark signal as false positive candidate |
| Retailer reports pest issue | Validate advisory-backed risk |
| Visit outcome shows no relevance | Lower future action confidence |

For now, this should be treated as a future learning loop, not a fully implemented model.

---

## Suggested Public Signal Bundle

Each operating geography should eventually have one public signal bundle.

Example:

```text
geography_id
crop_id
signal_date
crop_health_label
moisture_stress_label
heat_stress_label
pest_disease_risk_label
combined_public_risk_label
combined_public_risk_confidence
evidence_summary
```

This bundle can be joined into the current processed backend outputs before scoring/ranking.

---

## Combined Public Risk Label

The engine layer may use a combined label for simpler consumption.

Suggested logic:

| Condition | Combined Public Risk |
|---|---|
| Any severe/high public signal with medium/high confidence | High |
| Any moderate/watchlist/emerging signal with medium/high confidence | Medium |
| Only normal signals | Low |
| Evidence missing or low confidence | Unknown / Low Confidence |

This combined label is for engine consumption only.

Detailed signal evidence should still be preserved.

---

## Implementation Direction

Do not implement this by hard-coding public logic inside every engine.

Preferred approach:

```text
public signal generation
-> public signal bundle table
-> engine consumes bundle fields
```

This keeps the design modular.

Future implementation can introduce:

- public feature generation module
- public signal generation module
- public signal bundle output
- joins into priority/recommendation/anomaly pipelines
- explainability evidence mapping

---

## Current Caution

Public signals should improve context and prioritization, but they should not overclaim precision.

Avoid:

```text
farm-level diagnosis
confirmed pest outbreak
confirmed irrigation failure
exact retailer demand from public data
```

Prefer:

```text
tehsil-level crop stress context
advisory-backed pest risk
weather-supported moisture stress
public-data-backed priority context
```
