# Public Dataset Plan

This note defines the public datasets that would add meaningful value to KshetraAI in Phase 2.

This is a planning document. It focuses first on what data would be useful and why, before finalizing exact providers, APIs, or implementation.

---

## Selection Principle

Public datasets should be included only if they improve one or more of these system goals:

- better visit prioritization
- stronger next best action recommendations
- better anomaly or risk detection
- better explanation quality
- better timing/context for field action

Public data should not be added only because it is available.

---

## Priority 1: Weather Dataset

### What We Want

- rainfall
- temperature
- humidity
- wind speed
- recent weather history
- short-range forecast
- date and geography

### Why It Adds Value

Weather directly affects crop stress, pest/disease risk, spray timing, and field visit urgency.

### Signals It Can Support

- rainfall deviation signal
- heat stress signal
- humidity disease-risk signal
- spray suitability signal
- weather-risk priority boost
- weather-backed advisory context

### Engines Helped

- Priority Engine
- Contextual Decision Engine
- Anomaly Detection Engine
- Explainability Engine

### Planning Note

Weather should be one of the first public datasets integrated because it is actionable, explainable, and easy for field users to understand.

---

## Priority 2: Pest Surveillance / Pest Advisory Dataset

### What We Want

- pest name or pest category
- affected crop
- affected geography
- advisory date
- severity or advisory level, if available
- advisory text or recommendation, if available

### Why It Adds Value

Pest risk can quickly change visit priority and next best action. It is also highly explainable because the system can show the advisory as evidence.

### Signals It Can Support

- pest-risk signal
- crop-specific pest alert
- district/tehsil pest advisory signal
- pest-driven visit priority boost
- pest-related product recommendation context

### Engines Helped

- Priority Engine
- Contextual Decision Engine
- Anomaly Detection Engine
- Explainability Engine

### Planning Note

Pest data is especially valuable when joined with crop calendar, grower crop context, and territory geography.

---

## Priority 3: NDVI / Satellite Crop Health Dataset

### What We Want

- NDVI value
- NDVI change over time
- NDVI anomaly or deviation from baseline
- scene date
- geography
- cloud cover or quality indicator

### Why It Adds Value

NDVI can help identify vegetation stress or crop-health changes that may not be visible in sales or inventory data.

### Signals It Can Support

- crop-health stress signal
- NDVI anomaly signal
- vegetation decline signal
- geography-level crop stress alert
- crop-health evidence for explanations

### Engines Helped

- Priority Engine
- Anomaly Detection Engine
- Explainability Engine

### Planning Note

NDVI should be treated as a geography-level context signal unless we have reliable farm or field boundaries. It should not be overclaimed as exact farm-level diagnosis.

---

## Priority 4: Crop Calendar Dataset

### What We Want

- crop
- geography
- season
- sowing window
- growth stages
- harvest window
- stage timing by region

### Why It Adds Value

Crop calendar data makes recommendations timing-aware. The same product or advisory may be relevant in one crop stage and irrelevant in another.

### Signals It Can Support

- crop-stage signal
- sowing window signal
- flowering/vegetative/harvest stage context
- stage-aware product recommendation context
- stage-aware pest/weather risk interpretation

### Engines Helped

- Contextual Decision Engine
- Priority Engine
- Explainability Engine

### Planning Note

Crop calendar should be used to interpret other signals, especially pest, weather, NDVI, and grower crop context.

---

## Priority 5: Administrative Geography Dataset

### What We Want

- state
- district
- tehsil/block
- village or local body reference, if available and reliable
- market location if available
- latitude/longitude or boundary reference
- standardized geography names/codes

### Why It Adds Value

Public and private datasets often use different geography names and grains. A geography reference layer helps connect them safely.

### Signals It Can Support

- geography normalization signal
- territory-to-public-data join support
- district/tehsil mapping validation
- public/private data alignment

### Engines Helped

- Data Foundation
- Feature Generation Pipeline
- Explainability Engine

### Planning Note

This dataset may not directly create a business signal, but it improves the reliability of all public-private joins.

---

## Geography Grain Planning

Public data should be joined at the deepest reliable geography level available.

Recommended working hierarchy:

```text
State
  -> District / Jila
  -> Tehsil / Taluka / Mandal / Block
  -> Village / Gram Panchayat / Town
  -> Field / Farm plot
```

### Practical Use In KshetraAI

| Geography Level | Feasibility | Recommended Use |
|---|---|---|
| District | High | Broad public signals such as pest advisories, market prices, weather fallback, and reporting. |
| Tehsil / Taluka / Mandal | High to medium | Best Phase 2 operating grain because private retailer and grower data already include tehsil-like fields. |
| Village / local body | Medium to low | Useful only if reliable boundaries, names, or coordinates are available and can be matched. |
| Farm / field plot | Low with current data | Avoid farm-level claims unless field boundaries, GPS coordinates, or farm polygons are available. |

### Planning Decision

For Phase 2, the preferred practical grain is:

```text
District -> Tehsil
```

Tehsil-level signals are detailed enough for operational planning while still realistic for public/private data joins.

Satellite stress, weather risk, and pest signals should be described as geography-level risk signals unless reliable farm or field boundaries are available.

---

## Priority 6: Market / Mandi Price Dataset

### What We Want

- crop
- market/mandi
- district/state
- modal price
- min/max price
- date

### Why It Adds Value

Market price can provide economic context for crop timing, farmer selling behavior, and potential demand cycles.

### Signals It Can Support

- crop price trend signal
- market opportunity context
- harvest/sales timing context
- regional demand timing support

### Engines Helped

- Contextual Decision Engine
- Priority Engine
- Explainability Engine

### Planning Note

Market price is useful, but it should be secondary. It is less directly tied to immediate retailer action than weather, pest, NDVI, inventory, and POS.

---

## Priority 7: Soil / Agro-Climatic Context Dataset

### What We Want

- soil type
- agro-climatic zone
- rainfall zone
- irrigation context, if available
- crop suitability context

### Why It Adds Value

Soil and agro-climatic context can improve background agronomic reasoning and explain why some regions are more exposed to certain risks.

### Signals It Can Support

- agro-climatic risk context
- crop suitability context
- background stress sensitivity signal
- regional explanation context

### Engines Helped

- Explainability Engine
- Contextual Decision Engine
- Priority Engine

### Planning Note

This should be treated as a slow-changing background context layer, not as a fast operational trigger.

---

## Priority 8: Holiday / Local Seasonality Dataset

### What We Want

- public holidays
- major local events
- agricultural season windows
- festival dates
- date and geography where relevant

### Why It Adds Value

Local timing can affect field visits, campaign performance, and retailer availability.

### Signals It Can Support

- visit timing context
- campaign timing context
- seasonality adjustment signal
- field availability context

### Engines Helped

- Priority Engine
- Frontend Workflow
- Contextual Decision Engine

### Planning Note

This is useful but lower priority. It should be added only after stronger agronomic and operational public datasets are stable.

---

## Recommended Phase 2 Public Dataset Order

1. Weather dataset
2. Pest surveillance / pest advisory dataset
3. NDVI / satellite crop health dataset
4. Crop calendar dataset
5. Administrative geography dataset
6. Market / mandi price dataset
7. Soil / agro-climatic context dataset
8. Holiday / local seasonality dataset

---

## Strongest Initial Public Signal Bundle

For the first Phase 2 improvement cycle, the strongest public signal bundle is:

```text
Weather + Pest Advisory + NDVI + Crop Calendar
```

Together, these can support:

- crop stress detection
- pest risk alerts
- crop-stage-aware recommendations
- weather-backed visit priority
- satellite-backed crop-health context
- stronger explainability evidence

This bundle should be prioritized before lower-impact public context layers.

---

## Final Strong Public Signals

These are the strongest public-data-backed signals to design for Phase 2.

| Signal | Public Data Needed | Signal Level | Why It Is Strong |
|---|---|---|---|
| `satellite_weather_crop_stress_signal` | NDVI, NDWI, LST, rainfall, crop calendar | Tehsil / district / crop | Combines vegetation vigor, water condition, thermal stress, rainfall deficit, and crop-stage sensitivity. |
| `pest_risk_signal` | Pest advisory / pest surveillance, crop calendar, geography | District / tehsil / crop | Directly supports pest-driven alerts, visit urgency, and contextual recommendations. |
| `weather_risk_signal` | Rainfall, temperature, humidity, wind, forecast | District / tehsil | Supports crop stress, disease risk, spray timing, and visit prioritization. |
| `crop_stage_sensitivity_signal` | Crop calendar | Crop / geography / date | Helps interpret whether stress or pest risk is operationally urgent at the current crop stage. |
| `spray_suitability_signal` | Weather forecast, rainfall, wind, humidity | District / tehsil / date | Helps decide whether field advisory or spray-related action is timely. |
| `ndvi_crop_health_signal` | NDVI time series and quality metadata | Tehsil / district | Provides vegetation health context, especially when compared with baseline. |
| `moisture_stress_signal` | NDWI, rainfall, weather history | Tehsil / district | Helps distinguish water/moisture stress from generic vegetation decline. |
| `thermal_stress_signal` | LST, temperature | Tehsil / district | Highlights heat or surface-temperature pressure. |
| `market_price_context_signal` | Mandi/market price data | District / market / crop | Adds economic context for crop timing and potential demand behavior. |
| `geography_alignment_signal` | Administrative geography boundaries/codes | State / district / tehsil | Makes public-private joins more reliable and explainable. |
| `agro_climatic_context_signal` | Soil, agro-climatic zone, rainfall zone | District / tehsil | Adds slow-changing background context for risk interpretation. |
| `seasonality_timing_signal` | Holidays, season windows, local calendar | Date / geography | Supports visit timing, campaign timing, and planning context. |

### Highest-Value Public Signals

The top public signals for KshetraAI are:

1. `satellite_weather_crop_stress_signal`
2. `pest_risk_signal`
3. `weather_risk_signal`
4. `crop_stage_sensitivity_signal`
5. `geography_alignment_signal`

These should be prioritized because they can directly improve prioritization, recommendations, alerts, and explanations.
