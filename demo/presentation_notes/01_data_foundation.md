# Data Foundation

## Purpose

Build a reliable data foundation for KshetraAI by separating raw source data from processed, demo-safe operational views.

## Implementation Summary

- Implemented schema definitions for the company-provided internal dataset.
- Created a deterministic Build 01 pipeline for loading, validating, normalizing, and joining source files.
- Established a private raw data boundary through ignored `private-data/`.
- Established a public raw data boundary through ignored `public-data/`.
- Added a public-data processing workflow for weather, crop context, NDVI metadata, and pest references.

## How It Works

Internal CSV files are validated against schema definitions, normalized into canonical forms, joined into feature-ready views, and written as processed outputs. Public data is processed separately into public signal tables so it can be integrated later without mixing raw private and public sources.

## Data Sources

Internal schemas implemented in code:

- `reps_territory.csv`
- `retailers.csv`
- `retailer_visit_log.csv`
- `retailer_inventory_weekly.csv`
- `retailer_pos.csv`
- `growers.csv`
- `digital_funnel_weekly.csv`
- `whatsapp_campaign.csv`

Public-data foundation:

- weather signals from fetched Open-Meteo data
- controlled crop-stage context
- Sentinel-2 scene metadata / NDVI reference tables
- pest surveillance source references

## Demo Evidence

Canonical processed views include:

- `representatives`
- `territories`
- `retailers`
- `growers`
- `visit_entities`
- `crop_context`
- `retailer_pos_clean`
- `retailer_inventory_weekly_clean`
- `retailer_visit_log_clean`
- `campaign_engagement_clean`

Public processed outputs include:

- `datasets/processed/public/weather_signals.csv`
- `datasets/processed/public/crop_context.csv`
- `datasets/processed/public/ndvi_scene_inventory.csv`
- `datasets/processed/public/ndvi_signals.csv`
- `datasets/processed/public/pest_source_references.csv`
- `datasets/processed/public/pest_signals.csv`

## Current Public Signal Truth

- Weather data is usable as public signal data.
- Crop-stage context is curated/controlled for the demo.
- NDVI is currently metadata/reference level, not raster-derived crop health scoring.
- Pest data is currently reference-level, not active live pest outbreak detection.
- Public processed tables exist, but are not fully merged into the main private/public feature generation run yet.

## Verification

Relevant implementation areas:

- `backend/data/schemas/dataset_schemas.py`
- `backend/pipelines/pipeline_runner.py`
- `scripts/process_public_data.py`
- `tests/test_public_data_processing.py`

## Current Limits

- Raw private data is local only and should not be shared.
- Live public API calls are not used during the judge demo.
- Public NDVI and pest signals are foundations, not full production-grade integrations.

## Judge Takeaway

KshetraAI starts from a controlled, schema-driven data foundation with clear privacy boundaries and a dedicated path for public-domain signal integration.
