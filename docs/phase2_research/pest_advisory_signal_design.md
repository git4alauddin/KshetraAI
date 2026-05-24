# Pest Advisory Signal Design

This note defines a practical Phase 2 design for using public pest advisory or pest surveillance information in KshetraAI.

The goal is not to claim perfect real-time pest outbreak detection. The goal is to convert available pest advisories into structured, explainable signals that can support prioritization, recommendations, alerts, and explanations.

---

## Core Challenge

Pest data is valuable but usually messy.

Common issues:

- sources may be PDFs, bulletins, advisories, webpages, or images
- records may not be available through a clean API
- geography may be broad, often state/district/block rather than tehsil
- severity may be textual rather than numeric
- pest and crop names may vary across documents
- advisories may be irregularly published
- many sources provide advisory evidence, not measured pest population counts

Because of this, Phase 2 should start with a controlled advisory-ingestion design.

---

## Recommended First Approach

Start with normalized advisory reference records.

Instead of trying to build a perfect pest surveillance pipeline immediately, create a structured table:

```text
pest_advisory_references
```

This table should capture official or trusted pest/crop advisory evidence in a consistent format.

---

## Target Normalized Schema

| Field | Meaning |
|---|---|
| `advisory_id` | Internal unique identifier for the advisory record. |
| `source_name` | Name of the source, such as IMD Agromet, ICAR/KVK, PPQS, or state agriculture department. |
| `source_type` | Source format such as bulletin, PDF, webpage, advisory, or surveillance note. |
| `source_url_or_file` | Link or local file reference. |
| `advisory_date` | Date the advisory was issued or published. |
| `valid_from` | Start date for advisory relevance, if available. |
| `valid_to` | End date for advisory relevance, if available. |
| `state` | State or union territory. |
| `district` | District / jila level geography. |
| `tehsil_or_block` | Tehsil, taluka, mandal, block, or local advisory geography if available. |
| `crop` | Crop mentioned in the advisory. |
| `pest_or_disease` | Pest, disease, or biotic stress mentioned. |
| `severity_level` | Normalized severity: low, moderate, high, or unknown. |
| `advisory_text` | Short advisory text or summary. |
| `recommended_action` | Action suggested by the source, if available. |
| `evidence_summary` | Short explanation of why this advisory matters. |
| `confidence_level` | Confidence in the parsed advisory: low, medium, or high. |
| `parsed_by` | Manual, semi_manual, or automated. |

---

## Example Record

```text
advisory_id: PEST_ADV_0001
source_name: IMD Agromet Advisory
source_type: bulletin
source_url_or_file: source link or local file path
advisory_date: 2026-05-17
valid_from: 2026-05-17
valid_to: 2026-05-24
state: Punjab
district: Amritsar
tehsil_or_block: unknown
crop: cotton
pest_or_disease: sucking pest
severity_level: moderate
advisory_text: Recent advisory mentions monitoring for sucking pest risk in cotton.
recommended_action: Monitor crop and follow local crop protection advisory.
evidence_summary: Recent crop-specific pest advisory exists for the district.
confidence_level: medium
parsed_by: manual
```

---

## Practical Source Categories

### 1. IMD Agromet Advisories

IMD Agromet advisories can include crop-specific weather and pest/disease advice at district or block level.

Useful for:

- pest/disease advisory evidence
- weather-linked crop risk
- crop-stage and operation advice
- district/block context

Reference:

```text
https://agromet.imd.gov.in/
```

### 2. ICAR / KVK / DAMU Advisories

Krishi Vigyan Kendra and District Agro-Met Unit advisories often publish crop-specific advisory bulletins for local regions.

Useful for:

- district/block crop advice
- pest/disease management recommendations
- locally relevant advisory context

Example reference:

```text
https://icarnagaland.nic.in/Agromet_Advisory.html
```

### 3. PPQS / National Pest Monitoring References

PPQS and national pest monitoring documents can support the surveillance framework and terminology.

Useful for:

- pest monitoring process understanding
- standard operating framework
- pest surveillance governance

Reference:

```text
https://ppqs.gov.in/sites/default/files/sop_on_national_system_for_pest_monitoring_response_mechanism.pdf
```

### 4. State Agriculture Department Advisories

State agriculture departments may publish crop advisories, pest alerts, and crop protection recommendations.

Useful for:

- state-specific crop/pest context
- regional advisory evidence
- locally actionable recommendations

Planning note:

These may vary widely by state and format.

---

## Phase 2 Ingestion Strategy

### Step 1: Manual Reference Collection

Start with a small set of trusted advisory records.

Recommended initial scope:

```text
10-30 advisory records
```

Focus on:

- target demo geographies
- target crops
- recent advisories
- crop/pest combinations that can connect to private product, POS, inventory, or grower context

### Step 2: Normalize The Records

Convert each advisory into `pest_advisory_references`.

Normalize:

- crop names
- pest/disease names
- geography names
- dates
- severity labels
- source metadata

### Step 3: Generate Signals

Convert advisory records into deterministic signals.

### Step 4: Add Semi-Automation Later

After schema and logic are stable, add fetchers or parsers for specific source formats.

Avoid building broad scrapers before the signal design is stable.

---

## Candidate Pest Signals

| Signal | Level | Logic | Use |
|---|---|---|---|
| `pest_advisory_presence_signal` | District / crop | Recent advisory exists for crop/geography. | Adds pest-risk evidence. |
| `pest_recency_signal` | District / crop / date | Advisory is recent within a configured lookback window. | Prioritizes fresh advisories over stale ones. |
| `pest_crop_match_signal` | Crop | Advisory crop matches grower/private crop context. | Prevents irrelevant pest evidence. |
| `pest_geography_match_signal` | District / tehsil | Advisory geography matches retailer/grower/territory geography. | Keeps signal locally relevant. |
| `pest_severity_signal` | District / crop | Use normalized severity level if available. | Supports alert priority. |
| `pest_weather_support_signal` | District / crop | Weather conditions support pest/disease risk pattern. | Strengthens advisory confidence. |
| `pest_crop_stage_support_signal` | Crop / stage | Crop stage is susceptible to the pest/disease. | Improves recommendation timing. |
| `pest_action_context_signal` | Crop / product | Advisory action aligns with a product/advisory category. | Supports next best action generation. |

---

## Initial Signal Logic

Start simple:

```text
if recent advisory exists
and crop matches
and geography matches
then pest_advisory_presence_signal = true
```

Then strengthen:

```text
pest_risk_level =
    advisory recency
  + crop match
  + geography match
  + severity level
  + weather support
  + crop-stage support
```

Recommended classification:

| Evidence | Pest Risk Level |
|---|---|
| advisory exists but crop/geography weak | Low |
| recent advisory + crop match + geography match | Moderate |
| recent advisory + crop match + geography match + severity/weather/stage support | High |

---

## Engine Usage

### Priority Engine

Use pest risk to boost priority for territories, tehsils, or retailers in affected crop/geography contexts.

### Contextual Decision Engine

Use pest advisory evidence to guide next best action:

- monitor crop condition
- discuss relevant crop protection category
- advise retailer/grower on local pest advisory
- check inventory for relevant crop protection product category

### Anomaly Detection Engine

Create alerts when:

- pest risk appears in a geography
- pest risk is recent and severe
- pest risk overlaps with crop stage and weather support
- pest risk overlaps with inventory shortage for relevant product category

### Explainability Engine

Show advisory evidence:

- source
- advisory date
- crop
- pest/disease
- geography
- severity
- summary

---

## Reliability Rules

### Strong Signal

```text
Recent advisory
+ crop match
+ geography match
+ severity or action text available
+ weather or crop-stage support
```

### Medium Signal

```text
Recent advisory
+ crop match
+ broad district/state geography
```

### Weak Signal

```text
Old advisory
or crop not clearly matched
or geography too broad
or source confidence low
```

---

## Honest Claim

Safe claim:

```text
KshetraAI can integrate recent pest advisory evidence into field-force prioritization, recommendations, alerts, and explanations.
```

Avoid claiming:

```text
KshetraAI performs real-time pest outbreak detection.
```

Unless we later obtain structured live surveillance data and validate the pipeline.

---

## Current Caution

Pest advisories should be treated as evidence, not absolute truth.

They should support the system decision, but the system should remain explainable and human-governed.

Field confirmation or agronomist review may still be needed before treating a pest advisory as confirmed local infestation.
