# Geography Boundaries Feature

## Quick Brief

Geography boundaries provide the spatial reference layer used to connect public datasets with KshetraAI operating territories.

For Phase 2, geography boundaries should primarily support district and tehsil-level aggregation, matching, and explanation.

This feature does not directly create agronomic risk by itself. Its main job is to make public-private joins reliable.

---

## What Geography Boundaries Represent

Geography boundaries can help define:

- state boundary
- district or jila boundary
- tehsil, taluka, mandal, or block boundary
- village or local body boundary, if reliable
- spatial relationship between public data and sales territories
- clipping area for satellite observations
- aggregation area for weather, pest, and crop-stage signals

---

## Why This Feature Matters

Public and private datasets often use different geography formats.

Example mismatch:

```text
Private data: Ludhiana_T004
Public advisory: Ludhiana district
Satellite data: pixel grid
Weather data: gridded cell or station
```

The geography boundary layer helps normalize these into one working geography structure.

It supports:

- satellite image clipping
- weather aggregation
- pest advisory matching
- crop calendar matching
- territory-to-tehsil mapping
- explanation of where a signal came from

---

## Recommended Phase 2 Geography Grain

For Phase 2, the preferred practical grain is:

```text
District -> Tehsil
```

This is detailed enough for operational planning while still realistic for public/private data joining.

Farm-level or field-level claims should be avoided unless reliable farm boundaries, GPS coordinates, or plot polygons are available.

---

## Geography Hierarchy

Recommended hierarchy:

```text
State
  -> District / Jila
  -> Tehsil / Taluka / Mandal / Block
  -> Village / Gram Panchayat / Town
  -> Field / Farm plot
```

Different Indian states may use different local administrative terms.

For KshetraAI, these should be normalized into standard internal fields rather than treated as separate concepts everywhere.

---

## Expected Source Types

Geography boundary data may come from:

- public administrative boundary shapefiles
- government GIS portals
- Survey of India or state-level references, where available
- district or tehsil boundary GeoJSON files
- manually curated mapping tables, where boundary files are incomplete

The preferred processing format should be:

```text
GeoJSON
```

GeoJSON is easier to inspect, version, and use in Python geospatial workflows after converting from shapefile.

---

## Core Boundary Fields

Recommended boundary reference fields:

| Field | Meaning |
|---|---|
| `state_name` | State name |
| `state_code` | Standardized state code, if available |
| `district_name` | District or jila name |
| `district_code` | Standardized district code, if available |
| `tehsil_name` | Tehsil, taluka, mandal, or block name |
| `tehsil_code` | Standardized tehsil-level code, if available |
| `geometry` | Polygon or multipolygon boundary |
| `geometry_source` | Source of boundary file |
| `geometry_valid_from` | Date/version of boundary reference, if available |
| `boundary_confidence` | High, medium, or low |

---

## Normalized Geography Reference Table

Recommended normalized table:

```text
geography_boundaries
```

Recommended fields:

| Field | Meaning |
|---|---|
| `geography_id` | Internal stable geography ID |
| `geography_level` | State, district, tehsil, village, or field |
| `parent_geography_id` | Parent geography reference |
| `canonical_name` | Standard internal name |
| `alternate_names` | Known spelling/local-language variants |
| `state_name` | State |
| `district_name` | District |
| `tehsil_name` | Tehsil/taluka/mandal/block |
| `geometry_available_flag` | Whether polygon geometry is available |
| `geometry_file_ref` | File path or source reference |
| `join_confidence` | High, medium, or low |

---

## Spatial Join Logic

Boundary data can support three main join patterns.

| Join Type | Example | Use |
|---|---|---|
| Name/code match | Retailer tehsil matches boundary tehsil | Public-private geography alignment |
| Point-in-polygon | Retailer or market coordinate falls inside tehsil polygon | Coordinate-based mapping |
| Polygon clipping | Satellite pixels clipped to tehsil polygon | NDVI/NDWI/LST aggregation |

If coordinates are missing, use name/code matching with confidence labels.

If polygons are missing, use district or tehsil mapping tables as fallback.

---

## Boundary Confidence Logic

Every geography match should carry confidence.

| Confidence | Meaning |
|---|---|
| `high` | Exact code match or reliable point-in-polygon match |
| `medium` | Strong name match with district/state agreement |
| `low` | Fuzzy name match or broad district/state fallback |
| `unknown` | Match cannot be confirmed |

This is important because downstream signals should not appear more precise than the geography match allows.

---

## Aggregation Use Cases

Geography boundaries are needed to produce public-data features at the operating geography level.

| Feature | Geography Use |
|---|---|
| NDVI | Clip satellite pixels to tehsil/district |
| NDWI | Clip satellite pixels to tehsil/district |
| LST | Aggregate thermal pixels to tehsil/district |
| Rainfall | Map gridded or station rainfall to geography |
| Weather context | Aggregate weather observations/forecast |
| Pest advisory | Match advisory geography to operating geography |
| Crop stage | Select crop calendar by geography |

---

## Feature Output

Recommended output fields:

| Field | Meaning |
|---|---|
| `geography_id` | Internal geography identifier |
| `geography_level` | District, tehsil, village, etc. |
| `canonical_name` | Standard internal geography name |
| `state_name` | State |
| `district_name` | District |
| `tehsil_name` | Tehsil/taluka/mandal/block |
| `geometry_available_flag` | Whether boundary polygon is available |
| `geometry_quality_label` | High, medium, low, or unknown |
| `join_method` | Code, name, fuzzy, point-in-polygon, or fallback |
| `join_confidence` | High, medium, low, or unknown |
| `source_name` | Boundary source |
| `source_version` | Source version/date, if available |

---

## Signals That Use Geography Boundaries

Geography boundaries support:

- crop health signal
- moisture stress signal
- heat stress signal
- pest/disease risk signal
- weather risk signal
- crop-stage sensitivity signal
- geography alignment signal
- territory priority signal

This feature is most important for making the signals trustworthy and traceable.

---

## Explainability Example

Example explanation text:

```text
The crop-health signal was aggregated at tehsil level using the matched territory boundary. Satellite observations were clipped to the tehsil polygon before generating NDVI and NDWI summaries.
```

For lower-confidence matching:

```text
The public signal is shown at district level because a reliable tehsil boundary match was not available.
```

---

## Current Caution

Do not overclaim precision.

If the signal is district-level, do not describe it as exact retailer-level or farm-level evidence.

Prefer:

```text
district-level risk context
```

or:

```text
tehsil-level crop-health context
```

Avoid:

```text
this retailer's nearby field is stressed
```

unless there is reliable coordinate or plot-level evidence.
