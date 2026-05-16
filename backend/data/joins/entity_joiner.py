"""Canonical entity join helpers for KshetraAI Build 01.

This module builds deterministic in-memory canonical views from validated and
normalized source DataFrames. It does not write processed files, generate
features, score priorities, or create recommendations.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

import pandas as pd


CANONICAL_VIEW_ORDER = (
    "representatives",
    "territories",
    "retailers",
    "growers",
    "visit_entities",
    "retailer_pos_clean",
    "retailer_inventory_weekly_clean",
    "retailer_visit_log_clean",
    "campaign_engagement_clean",
)

REQUIRED_SOURCE_DATASETS = (
    "reps_territory",
    "retailers",
    "retailer_visit_log",
    "retailer_inventory_weekly",
    "retailer_pos",
    "growers",
    "digital_funnel_weekly",
    "whatsapp_campaign",
)


class EntityJoinError(ValueError):
    """Raised when canonical joins cannot be built safely."""


def build_canonical_views(
    datasets: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Build all Build 01 canonical views in stable order."""

    _require_datasets(datasets, REQUIRED_SOURCE_DATASETS)

    representatives = build_representatives(datasets["reps_territory"])
    territories = build_territories(datasets["reps_territory"])
    retailers = build_retailers(datasets["retailers"], territories)
    growers = build_growers(datasets["growers"], territories)
    visit_entities = build_visit_entities(retailers, growers)
    retailer_pos_clean = build_retailer_pos_clean(datasets["retailer_pos"], retailers)
    retailer_inventory_weekly_clean = build_retailer_inventory_weekly_clean(
        datasets["retailer_inventory_weekly"],
        retailers,
    )
    retailer_visit_log_clean = build_retailer_visit_log_clean(
        datasets["retailer_visit_log"],
        representatives,
        territories,
    )
    campaign_engagement_clean = build_campaign_engagement_clean(
        datasets["digital_funnel_weekly"],
        datasets["whatsapp_campaign"],
    )

    return {
        "representatives": representatives,
        "territories": territories,
        "retailers": retailers,
        "growers": growers,
        "visit_entities": visit_entities,
        "retailer_pos_clean": retailer_pos_clean,
        "retailer_inventory_weekly_clean": retailer_inventory_weekly_clean,
        "retailer_visit_log_clean": retailer_visit_log_clean,
        "campaign_engagement_clean": campaign_engagement_clean,
    }


def build_representatives(reps_territory: pd.DataFrame) -> pd.DataFrame:
    """Build the representative assignment view."""

    required_columns = ("rep_id", "territory_id", "territory_name", "state", "district")
    _ensure_columns("reps_territory", reps_territory, required_columns)

    return _stable_frame(
        reps_territory.loc[:, list(required_columns)].drop_duplicates(),
        sort_by=("rep_id",),
    )


def build_territories(reps_territory: pd.DataFrame) -> pd.DataFrame:
    """Build the territory master view."""

    required_columns = (
        "territory_id",
        "territory_name",
        "state",
        "district",
        "tehsil_list",
    )
    _ensure_columns("reps_territory", reps_territory, required_columns)

    return _stable_frame(
        reps_territory.loc[:, list(required_columns)].drop_duplicates(),
        sort_by=("territory_id",),
    )


def build_retailers(
    retailers: pd.DataFrame,
    territories: pd.DataFrame,
) -> pd.DataFrame:
    """Build retailer master view with territory context attached."""

    _ensure_columns(
        "retailers",
        retailers,
        ("retailer_id", "territory_id", "state", "district", "tehsil"),
    )
    _ensure_columns(
        "territories",
        territories,
        ("territory_id", "territory_name"),
    )

    merged = retailers.merge(
        territories.loc[:, ["territory_id", "territory_name"]],
        on="territory_id",
        how="left",
        validate="many_to_one",
    )
    return _stable_frame(
        merged.loc[
            :,
            [
                "retailer_id",
                "territory_id",
                "territory_name",
                "state",
                "district",
                "tehsil",
            ],
        ],
        sort_by=("retailer_id",),
    )


def build_growers(
    growers: pd.DataFrame,
    territories: pd.DataFrame,
) -> pd.DataFrame:
    """Build grower master view with best-effort territory assignment."""

    _ensure_columns(
        "growers",
        growers,
        (
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
    )

    territory_lookup = _build_territory_tehsil_lookup(territories)
    enriched = growers.copy()
    enriched["territory_id"] = enriched.apply(
        lambda row: territory_lookup.get(
            _territory_lookup_key(row["state"], row["district"], row["tehsil"])
        ),
        axis=1,
    ).astype("string")
    enriched["territory_name"] = enriched["territory_id"].map(
        territories.set_index("territory_id")["territory_name"]
    ).astype("string")

    return _stable_frame(
        enriched.loc[
            :,
            [
                "grower_id",
                "territory_id",
                "territory_name",
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
            ],
        ],
        sort_by=("grower_id",),
    )


def build_visit_entities(
    retailers: pd.DataFrame,
    growers: pd.DataFrame,
) -> pd.DataFrame:
    """Build the combined retailer/grower visit entity view."""

    retailer_entities = pd.DataFrame(
        {
            "entity_id": retailers["retailer_id"],
            "source_id": retailers["retailer_id"],
            "entity_type": "retailer",
            "territory_id": retailers["territory_id"],
            "territory_name": retailers["territory_name"],
            "state": retailers["state"],
            "district": retailers["district"],
            "tehsil": retailers["tehsil"],
            "preferred_language": "",
            "primary_crop": "",
        }
    )
    grower_entities = pd.DataFrame(
        {
            "entity_id": growers["grower_id"],
            "source_id": growers["grower_id"],
            "entity_type": "grower",
            "territory_id": growers["territory_id"],
            "territory_name": growers["territory_name"],
            "state": growers["state"],
            "district": growers["district"],
            "tehsil": growers["tehsil"],
            "preferred_language": growers["language"],
            "primary_crop": growers["grower_crop_calendar"].map(_extract_primary_crop),
        }
    )

    combined = pd.concat([retailer_entities, grower_entities], ignore_index=True)
    return _stable_frame(combined, sort_by=("entity_type", "entity_id"))


def build_retailer_pos_clean(
    retailer_pos: pd.DataFrame,
    retailers: pd.DataFrame,
) -> pd.DataFrame:
    """Build POS view with retailer geography attached."""

    _ensure_columns(
        "retailer_pos",
        retailer_pos,
        (
            "retailer_id",
            "transaction_id",
            "sku_id",
            "sku_name",
            "sku_qty",
            "sku_price",
            "transaction_date",
        ),
    )
    context = retailers.loc[
        :, ["retailer_id", "territory_id", "state", "district", "tehsil"]
    ]
    merged = retailer_pos.merge(
        context,
        on="retailer_id",
        how="left",
        validate="many_to_one",
    )
    return _stable_frame(
        merged.loc[
            :,
            [
                "transaction_id",
                "retailer_id",
                "territory_id",
                "state",
                "district",
                "tehsil",
                "sku_id",
                "sku_name",
                "sku_qty",
                "sku_price",
                "transaction_date",
            ],
        ],
        sort_by=("transaction_date", "transaction_id"),
    )


def build_retailer_inventory_weekly_clean(
    retailer_inventory_weekly: pd.DataFrame,
    retailers: pd.DataFrame,
) -> pd.DataFrame:
    """Build weekly inventory view with retailer geography attached."""

    _ensure_columns(
        "retailer_inventory_weekly",
        retailer_inventory_weekly,
        ("retailer_id", "sku_id", "sku_name", "sku_qty", "week_end_date"),
    )
    context = retailers.loc[
        :, ["retailer_id", "territory_id", "state", "district", "tehsil"]
    ]
    merged = retailer_inventory_weekly.merge(
        context,
        on="retailer_id",
        how="left",
        validate="many_to_one",
    )
    return _stable_frame(
        merged.loc[
            :,
            [
                "retailer_id",
                "territory_id",
                "state",
                "district",
                "tehsil",
                "sku_id",
                "sku_name",
                "sku_qty",
                "week_end_date",
            ],
        ],
        sort_by=("week_end_date", "retailer_id", "sku_id"),
    )


def build_retailer_visit_log_clean(
    retailer_visit_log: pd.DataFrame,
    representatives: pd.DataFrame,
    territories: pd.DataFrame,
) -> pd.DataFrame:
    """Build visit log view with representative and territory context attached."""

    _ensure_columns(
        "retailer_visit_log",
        retailer_visit_log,
        (
            "rep_id",
            "visit_date",
            "territory_id",
            "visit_tehsil",
            "visit_type",
            "product_recommended",
        ),
    )
    rep_context = representatives.loc[:, ["rep_id", "territory_id"]].rename(
        columns={"territory_id": "rep_territory_id"}
    )
    territory_context = territories.loc[:, ["territory_id", "territory_name", "state", "district"]]

    merged = retailer_visit_log.merge(
        rep_context,
        on="rep_id",
        how="left",
        validate="many_to_one",
    ).merge(
        territory_context,
        on="territory_id",
        how="left",
        validate="many_to_one",
    )

    return _stable_frame(
        merged.loc[
            :,
            [
                "rep_id",
                "rep_territory_id",
                "visit_date",
                "territory_id",
                "territory_name",
                "state",
                "district",
                "visit_tehsil",
                "visit_type",
                "product_recommended",
            ],
        ],
        sort_by=("visit_date", "rep_id", "territory_id", "visit_tehsil"),
    )


def build_campaign_engagement_clean(
    digital_funnel_weekly: pd.DataFrame,
    whatsapp_campaign: pd.DataFrame,
) -> pd.DataFrame:
    """Build a unified campaign engagement event view."""

    _ensure_columns(
        "digital_funnel_weekly",
        digital_funnel_weekly,
        (
            "campaign_id",
            "week_start_date",
            "social_post_impression",
            "landing_page_visits",
            "lead_form_submission",
            "campaign_crop",
            "campaign_product",
        ),
    )
    _ensure_columns(
        "whatsapp_campaign",
        whatsapp_campaign,
        (
            "id",
            "campaign_product",
            "campaign_crop",
            "grower_id",
            "message_sent_date",
            "delivered_status",
            "opened_status",
            "clicked_status",
        ),
    )

    funnel_events = pd.DataFrame(
        {
            "event_id": digital_funnel_weekly["campaign_id"].astype("string")
            + "|"
            + digital_funnel_weekly["week_start_date"].astype("string"),
            "event_type": "digital_funnel_weekly",
            "event_date": digital_funnel_weekly["week_start_date"],
            "campaign_id": digital_funnel_weekly["campaign_id"],
            "campaign_crop": digital_funnel_weekly["campaign_crop"],
            "campaign_product": digital_funnel_weekly["campaign_product"],
            "grower_id": "",
            "social_post_impression": digital_funnel_weekly["social_post_impression"],
            "landing_page_visits": digital_funnel_weekly["landing_page_visits"],
            "lead_form_submission": digital_funnel_weekly["lead_form_submission"],
            "delivered_status": _empty_series(len(digital_funnel_weekly), "boolean"),
            "opened_status": _empty_series(len(digital_funnel_weekly), "boolean"),
            "clicked_status": _empty_series(len(digital_funnel_weekly), "boolean"),
        }
    )
    whatsapp_events = pd.DataFrame(
        {
            "event_id": whatsapp_campaign["id"],
            "event_type": "whatsapp_campaign",
            "event_date": whatsapp_campaign["message_sent_date"],
            "campaign_id": "",
            "campaign_crop": whatsapp_campaign["campaign_crop"],
            "campaign_product": whatsapp_campaign["campaign_product"],
            "grower_id": whatsapp_campaign["grower_id"],
            "social_post_impression": _empty_series(len(whatsapp_campaign), "Int64"),
            "landing_page_visits": _empty_series(len(whatsapp_campaign), "Int64"),
            "lead_form_submission": _empty_series(len(whatsapp_campaign), "Int64"),
            "delivered_status": whatsapp_campaign["delivered_status"],
            "opened_status": whatsapp_campaign["opened_status"],
            "clicked_status": whatsapp_campaign["clicked_status"],
        }
    )

    combined = pd.concat([funnel_events, whatsapp_events], ignore_index=True)
    return _stable_frame(combined, sort_by=("event_date", "event_type", "event_id"))


def _build_territory_tehsil_lookup(territories: pd.DataFrame) -> dict[tuple[str, str, str], str]:
    _ensure_columns(
        "territories",
        territories,
        ("territory_id", "state", "district", "tehsil_list"),
    )
    lookup: dict[tuple[str, str, str], str] = {}

    for _, row in territories.iterrows():
        tehsils = _parse_tehsil_list(row["tehsil_list"])
        for tehsil in tehsils:
            key = _territory_lookup_key(row["state"], row["district"], tehsil)
            lookup.setdefault(key, str(row["territory_id"]))

    return lookup


def _parse_tehsil_list(value: object) -> tuple[str, ...]:
    if pd.isna(value) or str(value).strip() == "":
        return ()
    parsed = json.loads(str(value))
    if not isinstance(parsed, list):
        raise EntityJoinError("territories.tehsil_list must contain a JSON array.")
    return tuple(str(item) for item in parsed)


def _territory_lookup_key(state: object, district: object, tehsil: object) -> tuple[str, str, str]:
    return (_clean_key(state), _clean_key(district), _clean_key(tehsil))


def _extract_primary_crop(crop_calendar: object) -> str:
    if pd.isna(crop_calendar) or str(crop_calendar).strip() == "":
        return ""

    parsed = json.loads(str(crop_calendar))
    if isinstance(parsed, dict):
        for key in ("crop", "primary_crop", "main_crop", "campaign_crop"):
            value = parsed.get(key)
            if value:
                return str(value)
    return ""


def _require_datasets(
    datasets: Mapping[str, pd.DataFrame],
    required_names: tuple[str, ...],
) -> None:
    missing = tuple(name for name in required_names if name not in datasets)
    if missing:
        raise EntityJoinError("Missing datasets for canonical joins: " + ", ".join(missing))


def _ensure_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
    required_columns: tuple[str, ...],
) -> None:
    missing = tuple(column for column in required_columns if column not in dataframe.columns)
    if missing:
        raise EntityJoinError(
            f"{dataset_name}: missing required columns for join: " + ", ".join(missing)
        )


def _stable_frame(dataframe: pd.DataFrame, *, sort_by: tuple[str, ...]) -> pd.DataFrame:
    sorted_frame = dataframe.sort_values(list(sort_by), kind="mergesort").reset_index(
        drop=True
    )
    return sorted_frame.loc[:, list(dataframe.columns)]


def _clean_key(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).strip().casefold().split())


def _empty_series(length: int, dtype: str) -> pd.Series:
    return pd.Series([pd.NA] * length, dtype=dtype)
