# Retailer Demand Signal

## Quick Brief

The Retailer Demand Signal estimates recent product demand movement for a retailer and SKU using POS transaction data.

This is a core private signal.

It is grounded directly in `retailer_pos.csv`, which records retailer-level transaction line items with SKU, quantity, price, and transaction date.

This signal should help answer:

```text
Which retailer-SKU combinations are showing recent sales movement, demand velocity, or demand change?
```

---

## Signal Type

```text
Core private signal
```

This signal is generated from private POS data before higher-level opportunity or prioritization logic.

---

## Primary Dataset

| Dataset | Grain | Role |
|---|---|---|
| `retailer_pos.csv` | One row per retailer transaction line item | Main source for retailer/SKU demand movement |

---

## Direct Table Fields Used

These fields come directly from `retailer_pos.csv`.

| Field | Use |
|---|---|
| `retailer_id` | Retailer-level demand grouping and join key |
| `transaction_id` | Sale line identifier and duplicate-check support |
| `sku_id` | Product/SKU-level demand grouping |
| `sku_name` | Human-readable product name |
| `sku_qty` | Quantity sold |
| `sku_price` | Transaction-line price |
| `transaction_date` | Sales timing and recency |

---

## Derived Features From POS

These are generated from `retailer_pos.csv` after grouping by retailer, SKU, and time window.

| Derived Feature | How It Is Derived | Meaning |
|---|---|---|
| `recent_sales_qty` | Sum `sku_qty` over recent window | Recent product movement |
| `recent_sales_value` | Sum `sku_qty * sku_price` over recent window | Revenue-weighted sales movement |
| `sales_velocity_qty` | `recent_sales_qty / number_of_days_or_weeks` | Speed of product movement |
| `sales_recency_days` | Target date minus latest `transaction_date` | How recent the latest sale is |
| `prior_sales_qty` | Sum `sku_qty` over comparison window | Baseline/comparison demand |
| `demand_trend_delta` | Recent sales minus prior sales | Direction of demand change |
| `demand_trend_ratio` | Recent sales divided by prior sales, where valid | Relative demand change |
| `product_mix_share` | SKU sales divided by retailer total sales | Product focus within retailer sales |

---

## Joined Features Used

This signal can be enriched by joins, but the core demand score should remain POS-backed.

| Joined Dataset | Join Key | Feature Added | Use |
|---|---|---|---|
| `retailers.csv` | `retailer_id` | `territory_id`, `state`, `district`, `tehsil` | Adds geography and territory context |
| `reps_territory.csv` | `territory_id` after retailer join | `rep_id`, territory ownership | Enables rep/territory filtering |

Do not require inventory or visit-log joins for this core signal.

Inventory and visit context should be used later by:

- Inventory Pressure Signal
- Visit Coverage Gap Signal
- Retailer Opportunity Signal

---

## Signal Purpose

The Retailer Demand Signal should identify retailer-SKU combinations with meaningful sales movement.

It should support:

- retailer-level demand context
- product/SKU movement tracking
- priority scoring inputs
- recommendation context
- opportunity detection when later joined with inventory and visit signals

---

## Core Question

The signal should answer:

```text
Is this retailer-SKU showing recent, active, or increasing sales movement?
```

It should not answer:

```text
Is there unmet demand?
```

Unmet demand requires inventory, visit, and context joins.

---

## Recommended Grain

Primary grain:

```text
retailer_id + sku_id + time_window
```

Optional aggregations:

```text
retailer_id
territory_id + sku_id
tehsil + sku_id
district + sku_id
```

Retailer-SKU should remain the core grain because POS supports it directly.

---

## Time Window Logic

The signal should compare recent sales against a prior window.

Recommended first-pass windows:

| Window | Use |
|---|---|
| Recent 14 days | Short-term product movement |
| Recent 30 days | More stable recent demand |
| Prior 30 days | Comparison baseline |
| Season-to-date | Longer commercial context |

Window choice should be configurable later.

For documentation and first implementation, use:

```text
recent_window = 30 days
prior_window = previous 30 days
```

---

## Demand Activity Labels

Recommended demand activity labels:

| Label | Meaning |
|---|---|
| `no_recent_sales` | No POS sales in recent window |
| `low_activity` | Some sales, but low quantity/value |
| `active_demand` | Meaningful recent sales movement |
| `high_demand` | Strong recent sales movement |
| `unknown` | Missing or invalid POS evidence |

Thresholds should not be hardcoded permanently.

First implementation can use quantiles or configurable thresholds by SKU/category.

---

## Demand Trend Labels

Recommended trend labels:

| Label | Meaning |
|---|---|
| `rising` | Recent sales are meaningfully above prior window |
| `stable` | Recent and prior sales are broadly similar |
| `falling` | Recent sales are meaningfully below prior window |
| `new_activity` | Recent sales exist but prior window had none |
| `inactive` | No recent sales |
| `unknown` | Not enough data |

Trend should be derived from a recent-vs-prior comparison, not from a single transaction.

---

## Component Flags

Create interpretable flags before final label.

| Flag | Trigger Logic |
|---|---|
| `recent_sales_active_flag` | Recent window has non-zero sales quantity |
| `high_sales_velocity_flag` | Sales velocity is above configured/relative threshold |
| `sales_recent_flag` | Latest sale is within recent recency window |
| `demand_rising_flag` | Recent sales are above prior comparison window |
| `new_activity_flag` | Recent sales exist and prior sales were zero |
| `low_evidence_flag` | Too few transactions or weak POS evidence |

---

## Scoring Logic

For first-pass design, use transparent additive scoring.

| Component | Score |
|---|---:|
| Recent sales active | +1 |
| Sales recency is strong | +1 |
| High sales velocity | +2 |
| Demand trend rising | +1 |
| New activity after no prior sales | +1 |

Recommended label mapping:

| Score | Retailer Demand Signal |
|---:|---|
| 0 | No Recent Sales |
| 1-2 | Low / Active Demand |
| 3-4 | Strong Demand |
| 5-6 | High Demand Momentum |

The exact labels can be simplified during implementation if needed.

---

## Confidence Logic

Signal confidence should be separate from demand strength.

Recommended confidence factors:

| Confidence Factor | Impact |
|---|---|
| Multiple transactions in recent window | Raises confidence |
| Recent and prior comparison windows both have data | Raises confidence |
| SKU and retailer IDs are valid | Raises confidence |
| Only one transaction supports demand | Lowers confidence |
| Price or quantity values are missing/invalid | Lowers confidence |
| Product/SKU naming is inconsistent | Lowers confidence |

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
| `retailer_id` | Retailer being evaluated |
| `sku_id` | SKU being evaluated |
| `sku_name` | Product name |
| `recent_window_days` | Recent sales window length |
| `recent_sales_qty` | Quantity sold in recent window |
| `recent_sales_value` | Sales value in recent window |
| `sales_velocity_qty` | Quantity per day/week |
| `sales_recency_days` | Days since latest sale |
| `prior_sales_qty` | Quantity sold in comparison window |
| `demand_trend_label` | Rising, stable, falling, new activity, inactive, or unknown |
| `retailer_demand_score` | Additive demand score |
| `retailer_demand_label` | No Recent Sales, Low/Active Demand, Strong Demand, or High Demand Momentum |
| `signal_confidence` | High, medium, or low |
| `territory_id` | Added after retailer join, if available |
| `district` | Added after retailer join, if available |
| `tehsil` | Added after retailer join, if available |
| `evidence_summary` | Short explanation-ready evidence |

---

## Explainability Pattern

Example:

```text
Retailer demand is marked as Strong Demand because this retailer sold 84 units of Score 250 EC in the recent window, the latest sale is recent, and sales velocity is above the comparison baseline.
```

Low-confidence example:

```text
Retailer demand is marked as Active Demand, but confidence is low because it is supported by only one recent transaction.
```

---

## Business Use

This signal can help:

- identify active retailer-SKU demand
- support product-specific visit reasoning
- provide input into retailer opportunity scoring
- explain why a retailer is commercially relevant
- combine later with inventory to identify replenishment pressure

---

## Current Caution

Retailer Demand Signal shows recorded sales movement.

It does not prove:

- unmet demand
- stock constraint
- competitor impact
- future demand certainty
- recommendation effectiveness

Preferred wording:

```text
recorded recent POS demand
```

or:

```text
retailer-SKU sales movement
```

Use inventory, visit, outcome, and context signals before converting demand into opportunity or action.
