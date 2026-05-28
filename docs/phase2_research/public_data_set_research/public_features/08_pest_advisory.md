# Pest Advisory Feature

## Quick Brief

Pest advisory is a public advisory/reference feature that captures recent pest or disease guidance for a crop and geography.

For KshetraAI, pest advisory should be used as evidence of possible pest/disease risk, not as confirmed pest infestation.

This feature supports explainable pest-risk reasoning by preserving source, date, geography, crop, pest/disease, severity, and advisory text.

---

## What Pest Advisory Represents

Pest advisory can help describe:

- recent pest or disease warning
- crop-specific advisory evidence
- district/block/tehsil-level pest context
- recommended monitoring or action
- pest/disease risk timing
- advisory-backed field follow-up need

---

## What Pest Advisory Does Not Prove Alone

Pest advisory alone does not prove:

- confirmed local infestation
- exact pest population count
- exact farm-level pest presence
- exact retailer product demand
- guaranteed crop damage

It should be interpreted with:

- crop match
- geography match
- advisory recency
- severity or advisory language
- crop stage
- weather context
- NDVI/NDWI/LST anomalies where relevant

---

## Expected Source Types

Pest advisory data may come from:

- government pest bulletins
- agromet advisories
- ICAR/KVK advisories
- state agriculture department advisories
- pest surveillance references
- PDF or webpage bulletins

Initial implementation may be manual or semi-manual before automation.

---

## Normalized Advisory Record

Recommended normalized table:

```text
pest_advisory_references
```

Recommended fields:

| Field | Meaning |
|---|---|
| `advisory_id` | Internal unique advisory record ID |
| `source_name` | Source name, such as IMD Agromet, ICAR/KVK, PPQS, or state department |
| `source_type` | Bulletin, PDF, webpage, advisory, or surveillance note |
| `source_url_or_file` | Link or local file reference |
| `advisory_date` | Date advisory was issued |
| `valid_from` | Advisory relevance start date, if available |
| `valid_to` | Advisory relevance end date, if available |
| `state` | State |
| `district` | District / jila |
| `tehsil_or_block` | Tehsil, taluka, mandal, block, or local geography if available |
| `crop` | Crop mentioned |
| `pest_or_disease` | Pest, disease, or biotic stress mentioned |
| `severity_level` | Low, moderate, high, or unknown |
| `advisory_text` | Short advisory text or summary |
| `recommended_action` | Action suggested by the source, if available |
| `evidence_summary` | Short reason why this advisory matters |
| `confidence_level` | Low, medium, or high |
| `parsed_by` | Manual, semi_manual, or automated |

---

## Recency Logic

Pest advisory relevance should decay over time.

Recommended recency fields:

| Field | Meaning |
|---|---|
| `days_since_advisory` | Difference between target date and advisory date |
| `advisory_recency_label` | Recent, active, stale, or expired |
| `advisory_active_flag` | Whether advisory is still considered relevant |

Example MVP logic:

| Days Since Advisory | Recency Label |
|---:|---|
| 0-7 | Recent |
| 8-21 | Active |
| 22-45 | Stale |
| 46+ | Expired |

Exact windows should be configurable by crop/pest/source if needed.

---

## Crop Match Logic

Pest advisory should be relevant only when crop context matches.

Example:

```text
advisory crop = cotton
target crop = cotton
crop_match = true
```

If crop is missing or broad:

```text
crop_match = unknown
confidence lowered
```

Recommended fields:

| Field | Meaning |
|---|---|
| `target_crop` | Crop being evaluated |
| `advisory_crop` | Crop from advisory |
| `crop_match_flag` | true, false, or unknown |
| `crop_match_confidence` | high, medium, low |

---

## Geography Match Logic

Pest advisory should be matched to the target geography as specifically as possible.

Preferred matching order:

```text
tehsil/block
-> district
-> state
```

Recommended fields:

| Field | Meaning |
|---|---|
| `target_geography_id` | Tehsil/district being evaluated |
| `advisory_geography_level` | tehsil, block, district, state, or unknown |
| `geography_match_flag` | true, false, or unknown |
| `geography_match_level` | exact, district, state, broad, or unknown |
| `geography_match_confidence` | high, medium, low |

District-level advisories can support district/tehsil risk context, but should not be overclaimed as exact local infestation.

---

## Severity Logic

Severity may be explicit or inferred from advisory wording.

Preferred values:

| Severity | Meaning |
|---|---|
| `low` | Advisory mentions monitoring or low-level concern |
| `moderate` | Advisory indicates active watch or management need |
| `high` | Advisory indicates severe/high risk or urgent action |
| `unknown` | Severity not available or not confidently parsed |

If severity is not clearly available, keep it as:

```text
unknown
```

Do not invent severity.

---

## Feature Output

Recommended pest advisory feature fields:

| Field | Meaning |
|---|---|
| `advisory_id` | Advisory record ID |
| `source_name` | Source of advisory |
| `source_type` | Source format/type |
| `source_url_or_file` | Source link or file path |
| `target_date` | Date being evaluated |
| `advisory_date` | Date advisory was issued |
| `days_since_advisory` | Advisory age |
| `advisory_recency_label` | Recent, active, stale, or expired |
| `advisory_active_flag` | Whether advisory is still relevant |
| `target_geography_id` | Geography being evaluated |
| `advisory_geography_level` | Geography grain from source |
| `geography_match_flag` | Whether advisory matches target geography |
| `geography_match_confidence` | High, medium, or low |
| `target_crop` | Crop being evaluated |
| `advisory_crop` | Crop mentioned in advisory |
| `crop_match_flag` | Whether crop matches |
| `pest_or_disease` | Pest or disease mentioned |
| `severity_level` | Low, moderate, high, or unknown |
| `recommended_action` | Source-backed suggested action |
| `evidence_summary` | Explainable advisory summary |
| `confidence_level` | Feature confidence |

---

## Signals That Use Pest Advisory

Pest advisory is used by:

- Pest / Disease Risk Signal

It may also support:

- Crop Health Signal explanation
- territory priority context
- campaign timing context
- contextual next best action

---

## Example Signal Support

Strong pest advisory evidence:

```text
recent advisory
+ crop match
+ district/tehsil geography match
+ severity available
+ crop stage susceptible
+ weather conditions supportive
```

Weak evidence:

```text
old advisory
or broad geography only
or crop mismatch
or severity unknown
or low source confidence
```

---

## Explainability Example

```text
A recent district-level advisory mentioned sucking pest risk in cotton.
The advisory is active, the target crop matches cotton, and the crop is in a sensitive stage.
This supports a pest-risk watch signal, but does not confirm local infestation.
```

---

## Current Caution

Pest advisory is evidence, not confirmation.

Safe claim:

```text
recent pest advisory evidence supports pest-risk context
```

Avoid claim:

```text
confirmed pest outbreak detected
```

unless structured surveillance data and validation are available.
