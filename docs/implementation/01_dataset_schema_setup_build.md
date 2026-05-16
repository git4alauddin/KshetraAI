# Build 01 — Dataset & Schema Setup

---

# 1. Build Objective

The purpose of this build is to establish the validated data foundation for KshetraAI.

This build prepares company-provided internal operational data and controlled gap-fill inputs so downstream feature and intelligence components can work from stable, documented, deterministic data views.

This build does not implement scoring, recommendations, anomaly detection, explainability, APIs, or frontend behavior.

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/01_data_pipeline_contract.md`
- `docs/implementation_contracts/00_global_implementation_protocol.md`
- `docs/prompts/01_coding_session_prompt.md`
- `private-data/DATA_DICTIONARY.md`

If conflict exists, use this authority order:

```text
Architecture docs
        ↓
Implementation contracts
        ↓
This build checklist
        ↓
Implementation task prompt
```

---

# 3. Build Scope

## In Scope

- Read company-provided internal data from `private-data/`
- Define source dataset schemas
- Validate required columns
- Validate key uniqueness where applicable
- Validate referential integrity between source files
- Normalize dates, IDs, booleans, and categorical fields
- Build clean canonical internal views
- Prepare source-to-canonical mapping documentation
- Write derived outputs only to `datasets/processed/`
- Keep private source files unmodified

## Out of Scope

- Feature score generation
- Priority scoring
- Next-best-action generation
- Anomaly detection
- Explainability text generation
- Outcome learning logic
- API route implementation
- Frontend implementation
- ML modeling
- Live public data integrations
- Any modification to `private-data/`

---

# 4. Source Data

Internal operational data comes from:

```text
private-data/
```

Expected source files:

| File | Purpose |
|---|---|
| `reps_territory.csv` | Rep and territory mapping |
| `retailers.csv` | Retailer master |
| `retailer_visit_log.csv` | Historical rep activity and visit coverage |
| `retailer_inventory_weekly.csv` | Retailer-SKU weekly inventory snapshots |
| `retailer_pos.csv` | Retail point-of-sale transactions |
| `growers.csv` | Grower profiles, crop calendars, and engagement fields |
| `digital_funnel_weekly.csv` | Weekly digital funnel performance |
| `whatsapp_campaign.csv` | Grower WhatsApp engagement log |

`private-data/` is confidential and must remain ignored by Git.

---

# 5. Canonical Output Views

This build should prepare the foundation for these canonical views:

| Canonical View | Primary Source |
|---|---|
| `representatives` | `reps_territory.csv` |
| `territories` | `reps_territory.csv` |
| `retailers` | `retailers.csv` |
| `growers` | `growers.csv` |
| `visit_entities` | `retailers.csv`, `growers.csv` |
| `retailer_pos_clean` | `retailer_pos.csv` |
| `retailer_inventory_weekly_clean` | `retailer_inventory_weekly.csv` |
| `retailer_visit_log_clean` | `retailer_visit_log.csv` |
| `campaign_engagement_clean` | `digital_funnel_weekly.csv`, `whatsapp_campaign.csv` |

The build may also create mapping metadata that explains how each canonical view was produced.

---

# 6. Expected File Scope

Implementation for this build may modify only:

```text
backend/data/
backend/pipelines/
backend/utils/data_utils.py
datasets/processed/
datasets/synthetic/
tests/
docs/implementation/
```

`datasets/synthetic/` may only be used for missing public/external signals or controlled demo seed data.

---

# 7. Forbidden File Scope

This build must not modify:

```text
private-data/
backend/engines/
backend/features/
backend/anomaly/
backend/explainability/
backend/learning/
backend/api/
frontend/
docs/architecture/
docs/implementation_contracts/
```

Architecture and contract docs may only be changed if the human explicitly requests a documentation revision.

---

# 8. Required Validation Rules

The pipeline must validate:

- required files exist
- required columns exist
- key fields are present
- `rep_id` uniqueness in `reps_territory.csv`
- `territory_id` uniqueness in `reps_territory.csv`
- `retailer_id` uniqueness in `retailers.csv`
- `grower_id` uniqueness in `growers.csv`
- `transaction_id` uniqueness in `retailer_pos.csv`
- `id` uniqueness in `whatsapp_campaign.csv`
- no negative inventory quantity
- no non-positive POS quantity or price
- valid date parsing for date/datetime fields
- valid JSON in `tehsil_list`
- valid JSON in `grower_crop_calendar` where present
- retailer POS retailer IDs exist in retailer master
- inventory retailer IDs exist in retailer master
- retailer territory IDs exist in territory master
- visit rep IDs exist in rep master
- visit territory IDs exist in territory master
- WhatsApp grower IDs exist in grower master

Validation failures must be explicit and operationally understandable.

---

# 9. Normalization Requirements

Normalize:

- date and datetime fields into consistent ISO-compatible date formats
- boolean-like fields into booleans
- IDs as stripped strings
- state, district, tehsil, crop, and product labels into consistent categorical text
- JSON fields into parseable structured objects or validated JSON strings

Do not infer intelligence scores in this build.

---

# 10. Determinism Requirements

This build must be fully deterministic.

Given identical source files:

```text
outputs must remain identical
```

Requirements:

- no randomness
- stable sorting
- stable output column order
- stable validation report structure
- no hidden state
- no timestamp-dependent output values unless explicitly part of a run metadata file

---

# 11. Privacy Requirements

The implementation must protect confidential source data.

Rules:

- do not commit `private-data/`
- do not modify `private-data/`
- do not copy raw private files into tracked folders
- do not print large raw data samples in logs
- derived outputs must avoid exposing unnecessary confidential raw fields
- source-to-canonical mapping may describe columns but should not include sensitive row-level examples

---

# 12. Expected Outputs

At completion, this build should provide:

- schema definitions for source datasets
- reusable CSV loading utilities
- schema validation utilities
- normalization utilities
- clean internal canonical views
- a pipeline runner for Build 01
- a validation report or clear validation summary
- tests for schema validation and deterministic loading behavior

Output location:

```text
datasets/processed/
```

No raw private source data should be written there.

---

# 13. Definition of Done

Build 01 is complete only when:

- all expected source files are recognized
- source schemas are defined
- required columns are validated
- core key uniqueness checks pass or are explicitly reported
- referential integrity checks pass or are explicitly reported
- date, boolean, ID, categorical, and JSON normalization is implemented
- clean canonical views are generated or ready to generate
- generated outputs are deterministic
- no private source files are modified
- no business intelligence logic is introduced
- no feature scores are generated
- no downstream engines are modified
- tests exist for the implemented data pipeline behavior
- documentation clearly explains source-to-canonical mappings

---

# 14. Completion Checklist

## Source Inventory

- [ ] `private-data/` is ignored by Git
- [ ] all expected source files are present
- [ ] `__MACOSX` helper files are ignored by loader logic
- [ ] data dictionary is reviewed

## Schema Validation

- [ ] source schema definitions exist
- [ ] required columns are enforced
- [ ] missing required columns produce explicit errors
- [ ] duplicate key checks are implemented
- [ ] invalid date checks are implemented
- [ ] invalid JSON checks are implemented

## Referential Integrity

- [ ] retailer POS links to retailer master
- [ ] inventory links to retailer master
- [ ] retailers link to territory master
- [ ] visit logs link to rep master
- [ ] visit logs link to territory master
- [ ] WhatsApp records link to grower master

## Normalization

- [ ] IDs are stripped and consistently typed
- [ ] dates are normalized
- [ ] booleans are normalized
- [ ] categorical labels are normalized
- [ ] JSON fields are parsed or validated
- [ ] output column order is stable

## Output Views

- [ ] representatives view exists
- [ ] territories view exists
- [ ] retailers view exists
- [ ] growers view exists
- [ ] visit_entities view exists
- [ ] retailer POS clean view exists
- [ ] retailer inventory clean view exists
- [ ] retailer visit log clean view exists
- [ ] campaign engagement clean view exists

## Architecture Compliance

- [ ] no scoring logic added
- [ ] no recommendation logic added
- [ ] no anomaly logic added
- [ ] no explainability logic added
- [ ] no API/frontend changes added
- [ ] no private source file mutation
- [ ] only allowed files were modified

## Testing

- [ ] schema validation tests pass
- [ ] normalization tests pass
- [ ] referential integrity tests pass
- [ ] deterministic output test passes
- [ ] missing file/column error tests pass

---

# 15. Review Checklist

Before accepting Build 01, review:

| Question | Expected Answer |
|---|---|
| Did this build modify only allowed files? | Yes |
| Did it preserve `private-data/` as read-only? | Yes |
| Did it avoid raw private data commits? | Yes |
| Did it avoid feature scoring? | Yes |
| Did it avoid recommendation logic? | Yes |
| Did it avoid anomaly logic? | Yes |
| Are canonical views traceable to source files? | Yes |
| Are validation failures explicit? | Yes |
| Are outputs deterministic? | Yes |

---

# 16. Build 01 Final Statement

Build 01 is successful when KshetraAI has a clean, validated, deterministic data foundation based on company-provided internal data, with controlled handling for missing external signals and no downstream intelligence logic introduced.
