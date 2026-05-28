# Public Signals

This folder documents finalized Phase 2 public-data signals.

These signals are derived from public datasets and public features, then used to strengthen prioritization, recommendations, alerts, and explanations.

---

## Core Public Signals

| No. | Signal | Role |
|---:|---|---|
| 1 | [Crop Health Signal](01_crop_health_signal.md) | Geography-level crop condition risk |
| 2 | [Moisture Stress Signal](02_moisture_stress_signal.md) | Water/moisture stress risk |
| 3 | [Heat Stress Signal](03_heat_stress_signal.md) | Thermal pressure risk |
| 4 | [Pest / Disease Risk Signal](04_pest_disease_risk_signal.md) | Advisory-backed pest/disease monitoring risk |

---

## Decision-Layer Public Signals

| No. | Signal | Role |
|---:|---|---|
| 5 | [Campaign Timing Signal](05_campaign_timing_signal.md) | Determines whether action timing is too early, right, late, or urgent |
| 6 | [Territory Priority Signal](06_territory_priority_signal.md) | Summarizes public agronomic risk into geography-level priority context |

---

## Design Principle

Public signals should stay geography-aware, stage-aware, and confidence-aware.

They should improve decision context, but they should not overclaim farm-level diagnosis, confirmed pest outbreaks, confirmed irrigation failure, or exact retailer demand.

When a signal is district-level or tehsil-level, preserve that grain clearly in the output and explanation.
