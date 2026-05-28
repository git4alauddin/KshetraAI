# Private Signals

This folder documents finalized Phase 2 private/internal signals.

These signals are derived from private datasets and should be used to strengthen prioritization, recommendations, alerts, and explanations.

---

## Core Private Signals

| No. | Signal | Role |
|---:|---|---|
| 1 | [Retailer Demand Signal](01_retailer_demand_signal.md) | POS-backed retailer/SKU demand movement |
| 2 | [Inventory Pressure Signal](02_inventory_pressure_signal.md) | Stock-out, low-stock, and inventory-sales pressure |
| 3 | [Visit Coverage Gap Signal](03_visit_coverage_gap_signal.md) | Territory/tehsil visit recency and coverage gaps |
| 4 | [Grower Crop Context Signal](04_grower_crop_context_signal.md) | Crop calendar, crop stage, and crop concentration context |

---

## Decision-Layer Private Signal

| No. | Signal | Role |
|---:|---|---|
| 5 | [Retailer Opportunity Signal](05_retailer_opportunity_signal.md) | Combined opportunity signal for prioritization and next best action |

---

## Design Principle

Private signals should stay grounded in the available private datasets.

Do not infer retailer-level meaning from datasets that do not support retailer-level joins.

When a signal is only territory-level, tehsil-level, campaign-level, or grower-level, preserve that grain clearly.
