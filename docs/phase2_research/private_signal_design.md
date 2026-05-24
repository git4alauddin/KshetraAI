# Private Signal Design

This note documents Phase 2 signal ideas derived from private/internal datasets.

Signals here are design candidates. They should be implemented only after validating required joins, grain, and reliability.

---

## 1. `reps_territory.csv`

### Dataset Grain

One row per representative-territory assignment.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `rep_id` | Representative-level filtering and ownership. |
| `territory_id` | Territory join key for retailers, visits, and processed outputs. |
| `territory_name` | Human-readable territory label. |
| `state` | State-level grouping. |
| `district` | District-level grouping. |
| `tehsil_list` | Territory coverage footprint. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `territory_ownership_signal` | Territory / rep | Map each `territory_id` to one `rep_id`. | Ensures daily plans and alerts are filtered to the correct representative. |
| `territory_tehsil_count` | Territory | Count tehsils in `tehsil_list`. | Measures territory coverage breadth. |
| `territory_geography_key` | Territory | Use state, district, and tehsil list as a geography mapping layer. | Enables joins to retailers, growers, public weather, NDVI, and pest context. |
| `coverage_complexity_signal` | Territory | Higher tehsil count means broader geographic coverage. | Can support workload/context interpretation, not priority by itself. |

### Strongest Phase 2 Use

Use this dataset as the ownership and geography backbone. It should control which representative sees which territory, and it should help validate that downstream retailer, grower, visit, and public-context signals belong to the correct territory.

### Required Joins

- `retailers.csv` on `territory_id`
- `retailer_visit_log.csv` on `territory_id`
- processed territory outputs on `territory_id`
- public geography signals through district/tehsil/state mapping where available

### Reliability

High for ownership and geography mapping.

Low for direct priority or recommendation strength because it does not contain sales, inventory, visit outcomes, or risk values.

### Caution

Do not use this dataset alone to decide visit priority. It should act as a filtering, joining, validation, and context layer.

---

## 2. `retailers.csv`

### Dataset Grain

One row per retailer.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `retailer_id` | Retailer-level entity key. |
| `territory_id` | Territory ownership and representative filtering. |
| `state` | State-level grouping. |
| `district` | District-level grouping. |
| `tehsil` | Local geography grouping and join key. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `retailer_entity_signal` | Retailer | Treat each `retailer_id` as a visit candidate entity. | Establishes the base universe for retailer visit planning. |
| `retailer_territory_assignment` | Retailer / territory | Map each retailer to `territory_id`. | Filters daily plan candidates by representative territory. |
| `retailer_geography_signal` | Retailer | Use state, district, and tehsil as geography tags. | Supports joins to visits, public context, growers, weather, NDVI, and pest signals. |
| `territory_retailer_density` | Territory | Count retailers per `territory_id`. | Provides workload and market coverage context. |
| `tehsil_retailer_density` | Tehsil | Count retailers per tehsil. | Identifies local retail concentration. |
| `retailer_assignment_validation` | Retailer | Check whether retailer geography fits the assigned territory geography. | Helps detect mapping issues before scoring. |

### Strongest Phase 2 Use

Use this dataset as the retailer master and join base. It should define which retailers exist, where they are located, and which territory they belong to.

### Required Joins

- `reps_territory.csv` on `territory_id`
- `retailer_pos.csv` on `retailer_id`
- `retailer_inventory_weekly.csv` on `retailer_id`
- public or grower geography signals through state, district, or tehsil where appropriate

### Reliability

High for retailer identity, territory assignment, and geography.

Low for direct priority, demand, inventory need, or relationship quality because those require other datasets.

### Caution

This dataset should not create urgency by itself. It is a master-data layer. Visit priority should come from joined signals such as POS, inventory, visit recency, alerts, and contextual risk.

---

## 3. `growers.csv`

### Dataset Grain

One row per grower.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `grower_id` | Grower-level entity key. |
| `state` | State-level grouping. |
| `district` | District-level grouping. |
| `tehsil` | Local geography join key. |
| `language` | Communication and localization context. |
| `device_type` | Digital reachability context. |
| `grower_age` | Demographic context. |
| `gender` | Demographic context. |
| `grower_crop_calendar` | Crop, season, sowing, harvest, and stage context. |
| `product_scan` | Grower product engagement indicator. |
| `product_name` | Product involved in scan activity. |
| `product_scan_datetime` | Timing of product scan activity. |
| `grower_farm_size` | Farm-size opportunity context. |
| `offline_campaign_attended` | Offline engagement indicator. |
| `campaign_attendance_date` | Timing of offline engagement. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `grower_geography_signal` | Grower / tehsil | Use state, district, and tehsil from grower profile. | Joins grower context to territory, weather, NDVI, pest, and retailer geography. |
| `crop_calendar_signal` | Grower / crop | Parse `grower_crop_calendar` for crop, season, sowing, harvest, and stages. | Adds crop-stage context for advisories and risk interpretation. |
| `current_crop_stage_signal` | Grower / crop | Compare target date with crop calendar stage dates. | Supports crop-stage aware recommendations. |
| `grower_digital_readiness_signal` | Grower | Use `device_type` to estimate digital reachability. | Helps choose communication or follow-up channel. |
| `grower_language_signal` | Grower / geography | Use `language` label. | Supports localized advisory or communication planning. |
| `product_scan_engagement_signal` | Grower / product | Use `product_scan`, `product_name`, and scan datetime. | Indicates product-level interest or engagement. |
| `offline_campaign_engagement_signal` | Grower | Use `offline_campaign_attended` and attendance date. | Indicates field campaign engagement. |
| `farm_size_opportunity_signal` | Grower / geography | Use `grower_farm_size`, optionally aggregated by tehsil/district. | Provides opportunity context, especially when combined with crop and demand signals. |
| `crop_concentration_signal` | Tehsil / district | Aggregate growers by crop from crop calendar. | Helps identify geography-level crop focus. |

### Strongest Phase 2 Use

Use this dataset to strengthen crop context, grower engagement, local communication fit, and geography-level opportunity. It is especially useful when joined with public weather/NDVI/pest signals and private campaign or retailer geography signals.

### Required Joins

- `whatsapp_campaign.csv` on `grower_id`
- public weather, NDVI, and pest signals through geography and date
- `retailers.csv` through tehsil/district/state geography where suitable
- `reps_territory.csv` through territory geography where suitable

### Reliability

High for grower profile, geography, crop calendar, farm size, and engagement fields present in the row.

Medium for territory or retailer use because those require geography-based joining rather than a direct retailer key.

### Caution

This dataset should not be used as direct proof of retailer demand. It is best used as crop, grower, and geography context that strengthens recommendations when combined with sales, inventory, visit, campaign, and public-risk signals.

---

## 4. `retailer_pos.csv`

### Dataset Grain

One row per retailer transaction line item.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `retailer_id` | Retailer-level join key. |
| `transaction_id` | Sale line identifier. |
| `sku_id` | Product SKU sold. |
| `sku_name` | Product name sold. |
| `sku_qty` | Quantity sold. |
| `sku_price` | Transaction-line price. |
| `transaction_date` | Sale date. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `recent_sales_quantity_signal` | Retailer / SKU | Sum `sku_qty` over a recent time window. | Measures recent product movement. |
| `recent_sales_value_signal` | Retailer / SKU | Sum `sku_qty * sku_price` over a recent time window. | Provides revenue-weighted sales context. |
| `sales_velocity_signal` | Retailer / SKU | Average quantity sold per day/week over a defined window. | Identifies fast-moving products and active retailers. |
| `sales_recency_signal` | Retailer / SKU | Days since latest `transaction_date`. | Separates currently active demand from stale sales history. |
| `demand_trend_signal` | Retailer / SKU | Compare recent sales window with prior baseline window. | Detects rising or falling demand. |
| `demand_spike_signal` | Retailer / SKU | Flag when recent sales exceed baseline by a defined threshold. | Supports anomaly or opportunity detection. |
| `product_mix_signal` | Retailer | Share of sales by SKU/product. | Helps identify retailer product focus. |
| `territory_sales_signal` | Territory / SKU | Aggregate retailer sales after joining retailers on `retailer_id`. | Supports territory-level demand context. |
| `sales_opportunity_signal` | Retailer / SKU | Combine high sales velocity with stock or visit gaps. | Supports prioritized follow-up or replenishment action. |

### Strongest Phase 2 Use

Use this dataset as the core private demand signal. It should drive sales movement, demand trend, product opportunity, and demand-spike logic after joining with retailer geography and inventory.

### Required Joins

- `retailers.csv` on `retailer_id`
- `retailer_inventory_weekly.csv` on `retailer_id` and `sku_id`
- `reps_territory.csv` through retailer `territory_id`
- public or grower crop context through product/crop/geography mapping where suitable

### Reliability

High for recorded sales quantity, sales date, product, and retailer-level commercial movement.

Medium for business opportunity unless paired with inventory, visit recency, and product/crop context.

### Caution

POS shows what sold, not what could have sold. It does not directly reveal unmet demand, stock constraints, competitor influence, or recommendation effectiveness. Those require joins with inventory, visits, outcomes, and context.

---

## 5. `retailer_inventory_weekly.csv`

### Dataset Grain

One row per retailer-SKU weekly stock snapshot.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `retailer_id` | Retailer-level join key. |
| `sku_id` | Product SKU in stock. |
| `sku_name` | Product name in stock. |
| `sku_qty` | Quantity on hand at week end. |
| `week_end_date` | Weekly snapshot date. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `current_inventory_signal` | Retailer / SKU | Use latest available `sku_qty` by retailer and SKU. | Measures current known stock position. |
| `stock_out_signal` | Retailer / SKU | Flag when latest `sku_qty` is `0`. | Detects stock-out condition. |
| `low_stock_signal` | Retailer / SKU | Flag when latest `sku_qty` is below a configured threshold. | Supports replenishment need. |
| `inventory_trend_signal` | Retailer / SKU | Compare latest stock with previous weekly snapshots. | Shows whether stock is rising, stable, or falling. |
| `stock_depletion_rate_signal` | Retailer / SKU | Estimate stock decline across weekly snapshots. | Supports early replenishment warning. |
| `inventory_sales_mismatch_signal` | Retailer / SKU | Join with POS to find high sales velocity and low stock. | Identifies urgent replenishment or missed opportunity risk. |
| `stale_inventory_signal` | Retailer / SKU | High stock with low/no recent POS movement. | Supports slow-moving inventory attention. |
| `territory_stock_pressure_signal` | Territory / SKU | Aggregate low-stock/stock-out counts after joining retailer geography. | Supports territory-level stock pressure alerts. |

### Strongest Phase 2 Use

Use this dataset to turn sales demand into operational action. Inventory alone shows stock position, but inventory joined with POS can identify fast-moving products at risk of stock-out or slow-moving products that may need field attention.

### Required Joins

- `retailers.csv` on `retailer_id`
- `retailer_pos.csv` on `retailer_id` and `sku_id`
- `reps_territory.csv` through retailer `territory_id`
- product/category mapping if product-level rules become more detailed

### Reliability

High for weekly stock snapshot values at retailer-SKU level.

Medium for real-time stock status because the data is weekly, not live.

### Caution

Inventory snapshots are not real-time. A stock-out signal should be tied to the latest available `week_end_date`, and stronger action signals should combine inventory with POS velocity and visit recency.

---

## 6. `retailer_visit_log.csv`

### Dataset Grain

One row per representative visit or campaign activity record.

The raw file includes territory and tehsil, but not a direct `retailer_id`.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `rep_id` | Representative activity tracking. |
| `visit_date` | Visit recency and activity timing. |
| `territory_id` | Territory-level join key. |
| `visit_tehsil` | Tehsil-level coverage signal. |
| `visit_type` | Activity type context. |
| `product_recommended` | Product discussed or promoted. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `territory_visit_recency_signal` | Territory | Days since latest visit in a territory. | Identifies territories needing renewed field attention. |
| `tehsil_visit_recency_signal` | Tehsil | Days since latest visit in a tehsil. | Supports local coverage-gap detection. |
| `visit_frequency_signal` | Territory / tehsil | Count visits in a recent window. | Measures recent field activity intensity. |
| `coverage_gap_signal` | Territory / tehsil | Flag areas with no visits in a defined lookback window. | Supports prioritization when paired with demand or risk. |
| `visit_type_mix_signal` | Territory / tehsil | Count activity by `visit_type`. | Separates retailer meetings from campaign activities. |
| `product_followup_signal` | Territory / tehsil / product | Track recent `product_recommended` by geography. | Supports product-specific follow-up planning. |
| `campaign_activity_signal` | Territory / tehsil | Identify campaign-related visits from `visit_type`. | Adds offline activation context. |
| `rep_activity_load_signal` | Rep | Count recent visits by `rep_id`. | Supports workload/context interpretation. |
| `missed_followup_opportunity_signal` | Territory / tehsil | Combine low visit recency with high POS/inventory/risk signals. | Prioritizes areas where field activity may be needed. |

### Strongest Phase 2 Use

Use this dataset to add field activity and coverage context. Its strongest use is identifying where recent field engagement is missing, especially when the same geography also has sales opportunity, stock pressure, campaign interest, or public-risk signals.

### Required Joins

- `reps_territory.csv` on `rep_id` and `territory_id`
- `retailers.csv` through `territory_id` and tehsil alignment
- `retailer_pos.csv` after joining through retailer geography
- `retailer_inventory_weekly.csv` after joining through retailer geography
- public risk signals through territory, district, or tehsil where available

### Reliability

High for representative activity, territory-level visits, tehsil-level visits, visit dates, and promoted product context.

Medium for retailer-level use because the raw file does not include `retailer_id`.

### Caution

Do not treat this file as exact retailer-level visit history unless a valid retailer mapping is introduced. For now, it is strongest at territory and tehsil level.

---

## 7. `digital_funnel_weekly.csv`

### Dataset Grain

One row per campaign-week.

The raw file is campaign-level and does not include retailer, grower, territory, district, or tehsil identifiers.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `campaign_id` | Campaign identifier. |
| `week_start_date` | Weekly time window. |
| `social_post_impression` | Campaign reach. |
| `landing_page_visits` | Campaign interest. |
| `lead_form_submission` | Lead intent. |
| `campaign_crop` | Crop focus. |
| `campaign_product` | Product focus. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `campaign_reach_signal` | Campaign / week | Use `social_post_impression`. | Measures weekly campaign visibility. |
| `campaign_interest_signal` | Campaign / week | Use `landing_page_visits`. | Measures active campaign engagement. |
| `campaign_lead_intent_signal` | Campaign / week | Use `lead_form_submission`. | Measures stronger digital intent. |
| `visit_rate_signal` | Campaign / week | `landing_page_visits / social_post_impression`. | Measures movement from awareness to interest. |
| `lead_conversion_signal` | Campaign / week | `lead_form_submission / landing_page_visits`. | Measures movement from interest to lead intent. |
| `funnel_efficiency_signal` | Campaign / week | `lead_form_submission / social_post_impression`. | Measures overall digital funnel efficiency. |
| `campaign_momentum_signal` | Campaign / product | Compare current week metrics with prior weeks. | Detects rising or falling campaign interest. |
| `crop_product_interest_signal` | Crop / product | Use `campaign_crop`, `campaign_product`, and funnel metrics. | Adds product/crop demand context. |
| `digital_opportunity_context_signal` | Product / crop / time | Combine strong funnel metrics with POS or inventory context. | Supports product opportunity interpretation. |

### Strongest Phase 2 Use

Use this dataset as campaign-level demand context. It can strengthen product or crop opportunity reasoning when digital engagement aligns with POS movement, inventory pressure, grower crop calendars, or public risk signals.

### Required Joins

- Product mapping through `campaign_product`
- Crop mapping through `campaign_crop`
- `retailer_pos.csv` through product and time window where suitable
- `retailer_inventory_weekly.csv` through product and time window where suitable
- `growers.csv` through crop and geography only when a valid aggregation logic exists

### Reliability

High for weekly campaign reach, interest, and lead counts.

Medium for product/crop-level interest.

Low for retailer-level decisions unless joined through a careful product/time/geography design.

### Caution

This dataset should not be used as direct retailer demand. It is best treated as campaign-level digital demand context that can support, but not replace, retailer-level POS, inventory, and visit signals.

---

## 8. `whatsapp_campaign.csv`

### Dataset Grain

One row per WhatsApp campaign message sent to a grower.

The data dictionary states that this file excludes non-smartphone users.

### Available Raw Fields

| Field | Signal Use |
|---|---|
| `id` | Message row identifier. |
| `campaign_product` | Product promoted in the message. |
| `campaign_crop` | Crop associated with the message. |
| `grower_id` | Grower-level join key. |
| `message_sent_date` | Message timing. |
| `delivered_status` | Delivery success. |
| `opened_status` | Message open engagement. |
| `clicked_status` | Stronger tracked-link engagement. |

### Candidate Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `message_delivery_signal` | Grower / campaign | Use `delivered_status`. | Indicates whether the message reached the grower handset. |
| `message_open_signal` | Grower / campaign | Use `opened_status`. | Indicates message-level engagement. |
| `message_click_signal` | Grower / campaign | Use `clicked_status`. | Indicates stronger product/campaign intent. |
| `whatsapp_delivery_rate_signal` | Campaign / product / crop | Delivered messages divided by sent messages. | Measures delivery effectiveness. |
| `whatsapp_open_rate_signal` | Campaign / product / crop | Opened messages divided by delivered or sent messages. | Measures engagement quality. |
| `whatsapp_click_rate_signal` | Campaign / product / crop | Clicked messages divided by delivered, opened, or sent messages. | Measures stronger response. |
| `grower_recent_engagement_signal` | Grower | Most recent open/click event by date. | Supports follow-up timing. |
| `campaign_response_signal` | Crop / product | Aggregate delivery, open, and click signals by crop and product. | Adds campaign response context. |
| `digital_followup_opportunity_signal` | Grower / product | Flag growers with recent click or open. | Supports targeted field or digital follow-up. |
| `communication_reachability_signal` | Grower | Combine message delivery with grower device type. | Helps understand reachable digital audience. |

### Strongest Phase 2 Use

Use this dataset as a direct grower-level digital engagement signal. It can help identify which growers responded to a crop/product message and where follow-up may be useful, especially when joined with grower crop calendar, geography, and product context.

### Required Joins

- `growers.csv` on `grower_id`
- `digital_funnel_weekly.csv` through campaign crop/product and date window, if useful
- public weather, NDVI, and pest context through grower geography after joining `growers.csv`
- retailer or territory context through geography only where the join logic is valid

### Reliability

High for message delivery/open/click status among included smartphone users.

Medium for campaign response context after aggregation.

Low for all-grower representativeness because non-smartphone users are excluded.

### Caution

This dataset should not be treated as a full grower population signal. It reflects WhatsApp-reachable growers only. It should support digital engagement and follow-up context, not replace retailer POS, inventory, or territory-level signals.
