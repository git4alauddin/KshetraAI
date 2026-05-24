# Private Dataset Review

This note documents the private/internal datasets available for Phase 2 signal design.

Source files are kept locally in `private-data/` and are not committed to Git.

---

## 1. `reps_territory.csv`

### Quick Brief

Defines field representatives and their assigned sales territories. Each row maps one representative to one territory and includes the state, district, and tehsil coverage for that territory.

This dataset is the base geography and ownership layer for field-force planning.

### Sample Rows

| rep_id | territory_id | territory_name | state | district | tehsil_list |
|---|---|---|---|---|---|
| REP_0001 | TER_0001 | patna_north_001 | Bihar | Patna | Patna_T001, Patna_T002, Patna_T003, Patna_T004, Patna_T005, Patna_T006, Patna_T007, Patna_T008, Patna_T009, Patna_T010, Patna_T011, Patna_T012 |
| REP_0002 | TER_0002 | hisar_south_002 | Haryana | Hisar | Hisar_T001, Hisar_T002, Hisar_T003, Hisar_T004, Hisar_T005, Hisar_T006, Hisar_T007, Hisar_T008, Hisar_T009, Hisar_T010, Hisar_T011 |
| REP_0003 | TER_0003 | varanasi_east_003 | Uttar Pradesh | Varanasi | Varanasi_T001, Varanasi_T002, Varanasi_T003, Varanasi_T004, Varanasi_T005, Varanasi_T006, Varanasi_T007, Varanasi_T008, Varanasi_T009, Varanasi_T010 |
| REP_0004 | TER_0004 | bharatpur_west_004 | Rajasthan | Bharatpur | Bharatpur_T001, Bharatpur_T002, Bharatpur_T003, Bharatpur_T004, Bharatpur_T005, Bharatpur_T006, Bharatpur_T007, Bharatpur_T008 |

### Field Meaning

| Field | Meaning |
|---|---|
| `rep_id` | Unique identifier for the field representative. |
| `territory_id` | Unique identifier for the assigned territory. |
| `territory_name` | Human-readable territory name. |
| `state` | State where the territory is located. |
| `district` | District where the territory is located. |
| `tehsil_list` | Tehsils covered by the territory, stored as a JSON-style list in the raw file. |

### Phase 2 Signal Potential

- Territory ownership mapping for filtering daily plans by representative.
- Geography join key for connecting retailers, growers, visits, public weather, NDVI, and pest signals.
- Territory coverage breadth using tehsil count.
- Regional grouping for district/state-level performance, risk, or opportunity comparisons.
- Validation layer to ensure visits, retailers, and growers are assigned to known territories.

### Current Caution

This dataset defines coverage and ownership. It does not by itself indicate demand, risk, retailer priority, or visit urgency. Those signals need to come from joined operational and contextual datasets.

---

## 2. `retailers.csv`

### Quick Brief

Defines agricultural retail outlets and their assigned geographic locations. Each row represents one retailer and maps it to a territory, state, district, and tehsil.

This dataset is the base retailer master for retailer-level planning, joins, and filtering.

### Sample Rows

| retailer_id | territory_id | state | district | tehsil |
|---|---|---|---|---|
| RTL_00001 | TER_0001 | Bihar | Patna | Patna_T012 |
| RTL_00002 | TER_0001 | Bihar | Patna | Patna_T004 |
| RTL_00003 | TER_0001 | Bihar | Patna | Patna_T002 |
| RTL_00004 | TER_0001 | Bihar | Patna | Patna_T007 |

### Field Meaning

| Field | Meaning |
|---|---|
| `retailer_id` | Unique identifier for the retail outlet. |
| `territory_id` | Territory assigned to the retailer. |
| `state` | State where the retailer is located. |
| `district` | District where the retailer is located. |
| `tehsil` | Tehsil where the retailer is located. |

### Phase 2 Signal Potential

- Retailer master list for daily plan candidates.
- Territory-level filtering by representative assignment.
- Geography join key for POS, inventory, visits, weather, NDVI, and pest signals.
- Retailer density by territory, district, or tehsil.
- Coverage validation to detect retailers assigned outside known territory geography.

### Current Caution

This dataset identifies where retailers are located and which territory they belong to. It does not by itself indicate retailer importance, sales value, inventory need, relationship strength, or visit urgency.

---

## 3. `growers.csv`

### Quick Brief

Defines grower profiles with geography, demographics, farm size, crop calendar, product scan activity, and offline campaign attendance.

This dataset supports grower-context signals and geography-level crop/engagement understanding.

### Sample Rows

The raw file stores `grower_crop_calendar` as full JSON. It is summarized below for readability.

| grower_id | state | district | tehsil | language | device_type | grower_age | gender | grower_crop_calendar | product_scan | product_name | product_scan_datetime | grower_farm_size | offline_campaign_attended | campaign_attendance_date |
|---|---|---|---|---|---|---:|---|---|---|---|---|---:|---|---|
| GRW_00001 | Rajasthan | Bharatpur | Bharatpur_T023 | Hindi | smartphone | 67 | male | Rabi_2025-26, wheat, sowing 2025-11-01 to 2025-11-25, harvest 2026-03-20 to 2026-04-15 | false |  |  | 3.54 | false |  |
| GRW_00002 | Uttar Pradesh | Kanpur Nagar | Kanpur_Nagar_T023 | Hindi | smartphone | 71 | male | Rabi_2025-26, wheat, sowing 2025-11-01 to 2025-11-25, harvest 2026-03-20 to 2026-04-15 | false |  |  | 1.34 | false |  |
| GRW_00003 | Punjab | Patiala | Patiala_T104 | Punjabi | smartphone | 52 | male | Rabi_2025-26, wheat, sowing 2025-11-01 to 2025-11-25, harvest 2026-03-20 to 2026-04-15 | false |  |  | 0.55 | true | 2026-03-29 |
| GRW_00004 | Rajasthan | Jaipur | Jaipur_T007 | Hindi | smartphone | 65 | male | Rabi_2025-26, wheat, sowing 2025-11-01 to 2025-11-25, harvest 2026-03-20 to 2026-04-15 | false |  |  | 0.79 | true | 2026-01-31 |

### Field Meaning

| Field | Meaning |
|---|---|
| `grower_id` | Unique identifier for the grower. |
| `state` | State where the grower is based. |
| `district` | District where the grower is based. |
| `tehsil` | Tehsil where the grower is based. |
| `language` | Primary local language label. |
| `device_type` | Device category such as smartphone, keypad, or unknown. |
| `grower_age` | Age of the grower. |
| `gender` | Gender label in the dataset. |
| `grower_crop_calendar` | JSON crop calendar with season, crop, sowing window, harvest window, and crop stages. |
| `product_scan` | Whether the grower scanned a product. |
| `product_name` | Product name scanned, when applicable. |
| `product_scan_datetime` | Timestamp of product scan, when applicable. |
| `grower_farm_size` | Farm size in acres. |
| `offline_campaign_attended` | Whether the grower attended an offline campaign. |
| `campaign_attendance_date` | Date of offline campaign attendance, when applicable. |

### Phase 2 Signal Potential

- Crop-stage context from `grower_crop_calendar`.
- Grower engagement signal from product scans and campaign attendance.
- Local communication fit using language and device type.
- Farm-size weighted opportunity context at tehsil, district, or territory level.
- Geography join key for linking grower context with weather, NDVI, pest, and territory data.
- Crop concentration by geography for campaign or advisory planning.

### Current Caution

This dataset is grower-focused, not retailer-focused. It can strengthen territory or crop-context intelligence, but it should not be treated as direct proof of retailer demand unless joined with retailer, sales, campaign, or geography-level signals.

---

## 4. `retailer_pos.csv`

### Quick Brief

Defines granular point-of-sale transaction line items at the retailer and SKU level. Each row represents a product sale line with quantity, price, and transaction date.

This dataset is the main private source for retailer-level sales movement and demand signals.

### Sample Rows

| retailer_id | transaction_id | sku_id | sku_name | sku_qty | sku_price | transaction_date |
|---|---|---|---|---:|---:|---|
| RTL_00001 | POS_f457022d4d51 | SY_SCO_250EC | Score 250 EC | 81 | 1539.21 | 2025-10-10 |
| RTL_00001 | POS_f2f5eaaaf5e4 | SY_SCO_250EC | Score 250 EC | 3 | 1644.39 | 2025-10-14 |
| RTL_00001 | POS_94af270ca790 | SY_AXI_50EC | Axial 50 EC | 1 | 393.85 | 2025-10-18 |
| RTL_00001 | POS_a6e6345ef25c | SY_AXI_50EC | Axial 50 EC | 1 | 1257.72 | 2025-10-18 |

### Field Meaning

| Field | Meaning |
|---|---|
| `retailer_id` | Retailer where the sale was recorded. |
| `transaction_id` | Unique identifier for the sale line. |
| `sku_id` | Product SKU sold. |
| `sku_name` | Product name sold. |
| `sku_qty` | Quantity sold on the transaction line. |
| `sku_price` | Price used on the transaction line. |
| `transaction_date` | Date of sale. |

### Phase 2 Signal Potential

- Retailer sales velocity by SKU and time window.
- Revenue proxy using `sku_qty * sku_price`.
- Recent demand trend by retailer, product, territory, district, or tehsil.
- Product mix and category concentration.
- Sudden demand spike detection when current sales exceed historical baseline.
- Sales opportunity signal when strong demand is paired with low inventory or missed visits.

### Current Caution

This dataset shows recorded sales movement. It does not directly explain why the sale happened, whether demand was unmet, or whether inventory is currently sufficient. Those interpretations require joins with inventory, visits, retailer geography, and contextual signals.

---

## 5. `retailer_inventory_weekly.csv`

### Quick Brief

Defines weekly retailer-level stock snapshots by SKU. Each row represents the quantity on hand for a product at a retailer on a weekly closing date.

This dataset is the main private source for inventory availability, stock-out risk, and replenishment signals.

### Sample Rows

| retailer_id | sku_id | sku_name | sku_qty | week_end_date |
|---|---|---|---:|---|
| RTL_00001 | SY_TILT_250EC | Tilt 250 EC | 94 | 2025-10-05 |
| RTL_00001 | SY_SCO_250EC | Score 250 EC | 122 | 2025-10-05 |
| RTL_00001 | SY_AXI_50EC | Axial 50 EC | 193 | 2025-10-05 |
| RTL_00001 | SY_TILT_250EC | Tilt 250 EC | 94 | 2025-10-12 |

### Field Meaning

| Field | Meaning |
|---|---|
| `retailer_id` | Retailer the stock belongs to. |
| `sku_id` | Product SKU in inventory. |
| `sku_name` | Product name in inventory. |
| `sku_qty` | Quantity on hand at week end. The data dictionary states that `0` indicates out of stock. |
| `week_end_date` | Sunday date closing the weekly stock snapshot. |

### Phase 2 Signal Potential

- Current stock position by retailer and SKU.
- Stock-out detection when `sku_qty` is `0`.
- Low-stock or replenishment pressure based on recent inventory level.
- Inventory trend across weekly snapshots.
- Inventory-sales mismatch when low stock is paired with recent POS movement.
- Product-level visit reason, such as restocking fast-moving SKUs.

### Current Caution

This dataset shows weekly stock quantity, not daily stock movement. It should not be treated as exact real-time inventory. Stronger stock-out or replenishment signals should compare inventory with POS sales velocity and the latest available `week_end_date`.

---

## 6. `retailer_visit_log.csv`

### Quick Brief

Defines historical field visits conducted by representatives. Each row records the representative, visit date, territory, tehsil, visit type, and product discussed or promoted.

This dataset is the main private source for field activity, visit recency, coverage, and promoted-product context.

### Sample Rows

| rep_id | visit_date | territory_id | visit_tehsil | visit_type | product_recommended |
|---|---|---|---|---|---|
| REP_0203 | 2026-03-09 | TER_0203 | Jalgaon_T062 | retailer meeting | Vertimec 1.8 EC |
| REP_0203 | 2026-03-12 | TER_0203 | Jalgaon_T064 | retailer meeting | Tilt 250 EC |
| REP_0203 | 2026-03-12 | TER_0203 | Jalgaon_T063 | campaign_conducted | Cruiser 350 FS |
| REP_0203 | 2026-03-12 | TER_0203 | Jalgaon_T064 | retailer meeting | Cruiser 350 FS |

### Field Meaning

| Field | Meaning |
|---|---|
| `rep_id` | Representative who made the visit. |
| `visit_date` | Date of the field visit. |
| `territory_id` | Territory under which the visit was recorded. |
| `visit_tehsil` | Tehsil where the visit took place. |
| `visit_type` | Type of visit or activity, such as retailer meeting or campaign conducted. |
| `product_recommended` | Product discussed, recommended, or promoted during the visit. |

### Phase 2 Signal Potential

- Visit recency by representative, territory, tehsil, and product.
- Coverage gap signal for areas not visited recently.
- Rep activity pattern by visit type.
- Product promotion history by geography.
- Campaign activity context when `visit_type` is campaign-related.
- Follow-up priority when recent visits are low but sales, inventory, or risk signals are high.

### Current Caution

The raw visit log sample does not include a `retailer_id`. It is useful for territory and tehsil-level coverage, but it should not be treated as exact retailer-level visit history unless joined through additional logic or derived mapping.

---

## 7. `digital_funnel_weekly.csv`

### Quick Brief

Defines weekly performance metrics for primary Rabi digital campaigns. Each row represents one campaign-week with impressions, landing page visits, lead form submissions, crop focus, and campaign product.

This dataset supports campaign-level digital interest and product/crop demand context.

### Sample Rows

| campaign_id | week_start_date | social_post_impression | landing_page_visits | lead_form_submission | campaign_crop | campaign_product |
|---|---|---:|---:|---:|---|---|
| CMP_RABI25_001 | 2025-10-06 | 29663 | 665 | 47 | wheat | Topik 15 WP |
| CMP_RABI25_001 | 2025-10-13 | 14618 | 279 | 14 | wheat | Topik 15 WP |
| CMP_RABI25_001 | 2025-10-20 | 36445 | 753 | 36 | wheat | Topik 15 WP |
| CMP_RABI25_001 | 2025-10-27 | 32487 | 478 | 42 | wheat | Topik 15 WP |

### Field Meaning

| Field | Meaning |
|---|---|
| `campaign_id` | Synthetic campaign identifier. |
| `week_start_date` | Monday opening the campaign week. |
| `social_post_impression` | Weekly social post impression count. |
| `landing_page_visits` | Weekly landing page visits generated by the campaign. |
| `lead_form_submission` | Weekly lead form submissions generated by the campaign. |
| `campaign_crop` | Crop focus of the campaign. |
| `campaign_product` | Product aligned to the campaign. |

### Phase 2 Signal Potential

- Campaign reach using impressions.
- Digital interest using landing page visits.
- Lead intent using lead form submissions.
- Funnel conversion ratios, such as visits per impression and leads per visit.
- Crop-product demand context by campaign week.
- Product opportunity signal when digital interest aligns with POS, inventory, or grower crop context.

### Current Caution

This dataset is campaign-level and weekly. It does not include retailer, grower, territory, or district identifiers in the raw sample rows. Retailer-level use requires careful mapping through crop, product, time window, and geography/context joins.

---

## 8. `whatsapp_campaign.csv`

### Quick Brief

Defines WhatsApp outreach delivery and engagement for crop/product campaign messages. Each row represents one message sent to a grower, with delivery, open, and click statuses.

This dataset supports grower-level communication engagement and campaign response signals.

### Sample Rows

| id | campaign_product | campaign_crop | grower_id | message_sent_date | delivered_status | opened_status | clicked_status |
|---|---|---|---|---|---|---|---|
| WAM_RABI25_00001 | Tilt 250 EC | wheat | GRW_00001 | 2026-03-20 | true | false | false |
| WAM_RABI25_00002 | Tilt 250 EC | wheat | GRW_00002 | 2026-03-31 | true | false | false |
| WAM_RABI25_00003 | Tilt 250 EC | wheat | GRW_00003 | 2026-03-03 | true | false | false |
| WAM_RABI25_00004 | Tilt 250 EC | wheat | GRW_00004 | 2025-10-28 | true | false | false |

### Field Meaning

| Field | Meaning |
|---|---|
| `id` | Unique message row identifier. |
| `campaign_product` | Product promoted in the message. |
| `campaign_crop` | Crop associated with the message. |
| `grower_id` | Grower receiving the message; foreign key to `growers.csv`. |
| `message_sent_date` | Date when the message was sent. |
| `delivered_status` | Whether the message reached the handset. |
| `opened_status` | Whether the grower opened the message. |
| `clicked_status` | Whether the grower clicked a tracked link. |

### Phase 2 Signal Potential

- Message delivery rate by crop, product, or geography after joining with growers.
- Open rate as a grower engagement signal.
- Click rate as a stronger campaign intent signal.
- Campaign response by crop and product.
- Communication readiness by joining with grower device type.
- Follow-up opportunity when a grower clicked or opened a product message.

### Current Caution

The data dictionary states this file excludes non-smartphone users. That means engagement rates from this file should not be treated as representative of all growers. It is strongest as a digital-engagement signal for reachable growers, especially after joining with `growers.csv`.
