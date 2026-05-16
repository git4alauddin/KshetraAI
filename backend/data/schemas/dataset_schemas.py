"""Source dataset schema metadata for the KshetraAI data pipeline.

This module defines the real company-provided CSV source schemas used by
Build 01. It intentionally contains metadata only: no loading, validation,
normalization, joining, scoring, or recommendation logic belongs here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class ForeignKeySpec:
    """Relationship from one source dataset column to another dataset column."""

    column: str
    target_dataset: str
    target_column: str
    required: bool = True


@dataclass(frozen=True)
class DatasetSchema:
    """Declarative schema contract for one company-provided source CSV."""

    name: str
    filename: str
    description: str
    required_columns: tuple[str, ...]
    unique_columns: tuple[str, ...] = ()
    unique_column_groups: tuple[tuple[str, ...], ...] = ()
    id_columns: tuple[str, ...] = ()
    date_columns: tuple[str, ...] = ()
    datetime_columns: tuple[str, ...] = ()
    json_columns: tuple[str, ...] = ()
    boolean_columns: tuple[str, ...] = ()
    numeric_columns: tuple[str, ...] = ()
    non_negative_columns: tuple[str, ...] = ()
    positive_columns: tuple[str, ...] = ()
    categorical_columns: tuple[str, ...] = ()
    nullable_columns: tuple[str, ...] = ()
    allowed_values: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    foreign_keys: tuple[ForeignKeySpec, ...] = ()
    canonical_outputs: tuple[str, ...] = ()

    @property
    def all_columns(self) -> tuple[str, ...]:
        """Return the stable source column order for this dataset."""

        return self.required_columns


REPS_TERRITORY_SCHEMA = DatasetSchema(
    name="reps_territory",
    filename="reps_territory.csv",
    description="Field representatives and assigned sales territory coverage.",
    required_columns=(
        "rep_id",
        "territory_id",
        "territory_name",
        "state",
        "district",
        "tehsil_list",
    ),
    unique_columns=("rep_id", "territory_id"),
    id_columns=("rep_id", "territory_id"),
    json_columns=("tehsil_list",),
    categorical_columns=("territory_name", "state", "district"),
    canonical_outputs=("representatives", "territories"),
)

RETAILERS_SCHEMA = DatasetSchema(
    name="retailers",
    filename="retailers.csv",
    description="Retail outlet master data and territory assignment.",
    required_columns=(
        "retailer_id",
        "territory_id",
        "state",
        "district",
        "tehsil",
    ),
    unique_columns=("retailer_id",),
    id_columns=("retailer_id", "territory_id"),
    categorical_columns=("state", "district", "tehsil"),
    foreign_keys=(
        ForeignKeySpec(
            column="territory_id",
            target_dataset="reps_territory",
            target_column="territory_id",
        ),
    ),
    canonical_outputs=("retailers", "visit_entities"),
)

RETAILER_VISIT_LOG_SCHEMA = DatasetSchema(
    name="retailer_visit_log",
    filename="retailer_visit_log.csv",
    description="Historical field visit activity and promoted products.",
    required_columns=(
        "rep_id",
        "visit_date",
        "territory_id",
        "visit_tehsil",
        "visit_type",
        "product_recommended",
    ),
    id_columns=("rep_id", "territory_id"),
    date_columns=("visit_date",),
    categorical_columns=("visit_tehsil", "visit_type", "product_recommended"),
    nullable_columns=("product_recommended",),
    allowed_values={
        "visit_type": (
            "retailer meeting",
            "grower meeting",
            "campaign_conducted",
        ),
    },
    foreign_keys=(
        ForeignKeySpec(
            column="rep_id",
            target_dataset="reps_territory",
            target_column="rep_id",
        ),
        ForeignKeySpec(
            column="territory_id",
            target_dataset="reps_territory",
            target_column="territory_id",
        ),
    ),
    canonical_outputs=("retailer_visit_log_clean", "visit_history"),
)

RETAILER_INVENTORY_WEEKLY_SCHEMA = DatasetSchema(
    name="retailer_inventory_weekly",
    filename="retailer_inventory_weekly.csv",
    description="Weekly retailer SKU inventory snapshots.",
    required_columns=(
        "retailer_id",
        "sku_id",
        "sku_name",
        "sku_qty",
        "week_end_date",
    ),
    unique_column_groups=(("retailer_id", "sku_id", "week_end_date"),),
    id_columns=("retailer_id", "sku_id"),
    date_columns=("week_end_date",),
    numeric_columns=("sku_qty",),
    non_negative_columns=("sku_qty",),
    categorical_columns=("sku_name",),
    foreign_keys=(
        ForeignKeySpec(
            column="retailer_id",
            target_dataset="retailers",
            target_column="retailer_id",
        ),
    ),
    canonical_outputs=("retailer_inventory_weekly_clean", "inventory_signals"),
)

RETAILER_POS_SCHEMA = DatasetSchema(
    name="retailer_pos",
    filename="retailer_pos.csv",
    description="Retail point-of-sale transaction line items.",
    required_columns=(
        "retailer_id",
        "transaction_id",
        "sku_id",
        "sku_name",
        "sku_qty",
        "sku_price",
        "transaction_date",
    ),
    unique_columns=("transaction_id",),
    id_columns=("retailer_id", "transaction_id", "sku_id"),
    date_columns=("transaction_date",),
    numeric_columns=("sku_qty", "sku_price"),
    positive_columns=("sku_qty", "sku_price"),
    categorical_columns=("sku_name",),
    foreign_keys=(
        ForeignKeySpec(
            column="retailer_id",
            target_dataset="retailers",
            target_column="retailer_id",
        ),
    ),
    canonical_outputs=("retailer_pos_clean", "sales_signals"),
)

GROWERS_SCHEMA = DatasetSchema(
    name="growers",
    filename="growers.csv",
    description="Grower profile, crop calendar, farm size, and engagement context.",
    required_columns=(
        "grower_id",
        "state",
        "district",
        "tehsil",
        "language",
        "device_type",
        "grower_age",
        "gender",
        "grower_crop_calendar",
        "product_scan",
        "product_name",
        "product_scan_datetime",
        "grower_farm_size",
        "offline_campaign_attended",
        "campaign_attendance_date",
    ),
    unique_columns=("grower_id",),
    id_columns=("grower_id",),
    date_columns=("campaign_attendance_date",),
    datetime_columns=("product_scan_datetime",),
    json_columns=("grower_crop_calendar",),
    boolean_columns=("product_scan", "offline_campaign_attended"),
    numeric_columns=("grower_age", "grower_farm_size"),
    non_negative_columns=("grower_age", "grower_farm_size"),
    categorical_columns=(
        "state",
        "district",
        "tehsil",
        "language",
        "device_type",
        "gender",
        "product_name",
    ),
    nullable_columns=(
        "grower_crop_calendar",
        "product_name",
        "product_scan_datetime",
        "campaign_attendance_date",
    ),
    allowed_values={
        "device_type": ("smartphone", "keypad", "unknown"),
        "gender": ("male", "female"),
    },
    canonical_outputs=("growers", "visit_entities", "crop_context"),
)

DIGITAL_FUNNEL_WEEKLY_SCHEMA = DatasetSchema(
    name="digital_funnel_weekly",
    filename="digital_funnel_weekly.csv",
    description="Weekly campaign funnel metrics for Rabi campaigns.",
    required_columns=(
        "campaign_id",
        "week_start_date",
        "social_post_impression",
        "landing_page_visits",
        "lead_form_submission",
        "campaign_crop",
        "campaign_product",
    ),
    unique_column_groups=(("campaign_id", "week_start_date"),),
    id_columns=("campaign_id",),
    date_columns=("week_start_date",),
    numeric_columns=(
        "social_post_impression",
        "landing_page_visits",
        "lead_form_submission",
    ),
    non_negative_columns=(
        "social_post_impression",
        "landing_page_visits",
        "lead_form_submission",
    ),
    categorical_columns=("campaign_crop", "campaign_product"),
    canonical_outputs=("campaign_engagement_clean",),
)

WHATSAPP_CAMPAIGN_SCHEMA = DatasetSchema(
    name="whatsapp_campaign",
    filename="whatsapp_campaign.csv",
    description="Grower WhatsApp campaign delivery and engagement log.",
    required_columns=(
        "id",
        "campaign_product",
        "campaign_crop",
        "grower_id",
        "message_sent_date",
        "delivered_status",
        "opened_status",
        "clicked_status",
    ),
    unique_columns=("id",),
    id_columns=("id", "grower_id"),
    date_columns=("message_sent_date",),
    boolean_columns=("delivered_status", "opened_status", "clicked_status"),
    categorical_columns=("campaign_product", "campaign_crop"),
    foreign_keys=(
        ForeignKeySpec(
            column="grower_id",
            target_dataset="growers",
            target_column="grower_id",
        ),
    ),
    canonical_outputs=("campaign_engagement_clean",),
)

SOURCE_DATASET_SCHEMAS: tuple[DatasetSchema, ...] = (
    REPS_TERRITORY_SCHEMA,
    RETAILERS_SCHEMA,
    RETAILER_VISIT_LOG_SCHEMA,
    RETAILER_INVENTORY_WEEKLY_SCHEMA,
    RETAILER_POS_SCHEMA,
    GROWERS_SCHEMA,
    DIGITAL_FUNNEL_WEEKLY_SCHEMA,
    WHATSAPP_CAMPAIGN_SCHEMA,
)

SOURCE_DATASETS_BY_NAME: Mapping[str, DatasetSchema] = MappingProxyType(
    {schema.name: schema for schema in SOURCE_DATASET_SCHEMAS}
)

SOURCE_DATASETS_BY_FILENAME: Mapping[str, DatasetSchema] = MappingProxyType(
    {schema.filename: schema for schema in SOURCE_DATASET_SCHEMAS}
)

CANONICAL_VIEW_SOURCES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        "representatives": ("reps_territory",),
        "territories": ("reps_territory",),
        "retailers": ("retailers",),
        "growers": ("growers",),
        "visit_entities": ("retailers", "growers"),
        "crop_context": ("growers",),
        "retailer_pos_clean": ("retailer_pos",),
        "sales_signals": ("retailer_pos",),
        "retailer_inventory_weekly_clean": ("retailer_inventory_weekly",),
        "inventory_signals": ("retailer_inventory_weekly",),
        "retailer_visit_log_clean": ("retailer_visit_log",),
        "visit_history": ("retailer_visit_log",),
        "campaign_engagement_clean": (
            "digital_funnel_weekly",
            "whatsapp_campaign",
        ),
    }
)


def get_source_schema(dataset_name: str) -> DatasetSchema:
    """Return schema metadata for a source dataset name."""

    try:
        return SOURCE_DATASETS_BY_NAME[dataset_name]
    except KeyError as exc:
        known = ", ".join(sorted(SOURCE_DATASETS_BY_NAME))
        raise KeyError(f"Unknown source dataset '{dataset_name}'. Known: {known}") from exc


def get_source_schema_for_file(filename: str) -> DatasetSchema:
    """Return schema metadata for a source CSV filename."""

    try:
        return SOURCE_DATASETS_BY_FILENAME[filename]
    except KeyError as exc:
        known = ", ".join(sorted(SOURCE_DATASETS_BY_FILENAME))
        raise KeyError(f"Unknown source file '{filename}'. Known: {known}") from exc


def list_expected_source_files() -> tuple[str, ...]:
    """Return expected source CSV filenames in stable processing order."""

    return tuple(schema.filename for schema in SOURCE_DATASET_SCHEMAS)


def list_source_dataset_names() -> tuple[str, ...]:
    """Return source dataset names in stable processing order."""

    return tuple(schema.name for schema in SOURCE_DATASET_SCHEMAS)


def get_canonical_view_sources(view_name: str) -> tuple[str, ...]:
    """Return source dataset names used to derive a canonical view."""

    try:
        return CANONICAL_VIEW_SOURCES[view_name]
    except KeyError as exc:
        known = ", ".join(sorted(CANONICAL_VIEW_SOURCES))
        raise KeyError(f"Unknown canonical view '{view_name}'. Known: {known}") from exc
