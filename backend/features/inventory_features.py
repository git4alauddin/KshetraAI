"""Deterministic inventory feature builders for Build 02.

These builders convert processed inventory and POS tables into normalized
stock urgency features. They do not rank entities, create recommendations,
detect anomalies, or generate explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


INVENTORY_FEATURE_COLUMNS = (
    "stock_level_score",
    "sales_velocity_score",
    "stockout_risk_score",
    "inventory_need_score",
)


class InventoryFeatureError(ValueError):
    """Raised when inventory feature generation cannot proceed safely."""


def build_stock_level_features(
    retailer_inventory_weekly_clean: pd.DataFrame,
) -> pd.DataFrame:
    """Generate low-stock urgency features from latest inventory snapshots."""

    _ensure_columns(
        "retailer_inventory_weekly_clean",
        retailer_inventory_weekly_clean,
        ("retailer_id", "sku_qty", "week_end_date"),
    )
    inventory = retailer_inventory_weekly_clean.copy()
    inventory["entity_id"] = _clean_text_series(inventory["retailer_id"])
    inventory["sku_qty"] = _numeric_series(inventory["sku_qty"])
    inventory["week_end_date"] = pd.to_datetime(inventory["week_end_date"], errors="coerce")
    latest_date = inventory["week_end_date"].max()
    latest_inventory = inventory[inventory["week_end_date"].eq(latest_date)].copy()

    grouped = (
        latest_inventory.groupby("entity_id", as_index=False)
        .agg(current_stock_units=("sku_qty", "sum"))
        .sort_values("entity_id", kind="mergesort")
        .reset_index(drop=True)
    )
    grouped["stock_level_score"] = _inverse_relative_score(grouped["current_stock_units"])
    return grouped.loc[:, ["entity_id", "stock_level_score"]]


def build_sales_velocity_features(retailer_pos_clean: pd.DataFrame) -> pd.DataFrame:
    """Generate recent sales velocity features from POS transactions."""

    _ensure_columns(
        "retailer_pos_clean",
        retailer_pos_clean,
        ("retailer_id", "sku_qty", "transaction_date"),
    )
    pos = retailer_pos_clean.copy()
    pos["entity_id"] = _clean_text_series(pos["retailer_id"])
    pos["sku_qty"] = _numeric_series(pos["sku_qty"])
    pos["transaction_date"] = pd.to_datetime(pos["transaction_date"], errors="coerce")
    max_date = pos["transaction_date"].max()
    recent_cutoff = max_date - pd.Timedelta(days=30)
    recent_pos = pos[pos["transaction_date"].ge(recent_cutoff)].copy()

    grouped = (
        recent_pos.groupby("entity_id", as_index=False)
        .agg(recent_units_sold=("sku_qty", "sum"))
        .sort_values("entity_id", kind="mergesort")
        .reset_index(drop=True)
    )
    grouped["sales_velocity_score"] = _relative_score(grouped["recent_units_sold"])
    return grouped.loc[:, ["entity_id", "sales_velocity_score"]]


def build_inventory_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one entity-level inventory feature view from inventory and POS inputs."""

    if "retailer_inventory_weekly_clean" not in datasets:
        raise InventoryFeatureError("retailer_inventory_weekly_clean is required.")

    stock = build_stock_level_features(datasets["retailer_inventory_weekly_clean"])
    output = stock.copy()

    if "retailer_pos_clean" in datasets:
        velocity = build_sales_velocity_features(datasets["retailer_pos_clean"])
        output = output.merge(velocity, on="entity_id", how="outer")

    for column in INVENTORY_FEATURE_COLUMNS:
        if column in output.columns:
            output[column] = output[column].fillna(0).astype("Int64")
        else:
            output[column] = pd.Series([0] * len(output), dtype="Int64")

    output["stockout_risk_score"] = _clamp_score(
        output["stock_level_score"] * 0.65 + output["sales_velocity_score"] * 0.35
    )
    output["inventory_need_score"] = _clamp_score(
        output["stock_level_score"] * 0.50
        + output["sales_velocity_score"] * 0.25
        + output["stockout_risk_score"] * 0.25
    )

    return _stable_frame(
        output.loc[:, ("entity_id", *INVENTORY_FEATURE_COLUMNS)],
        sort_by=("entity_id",),
    )


def _relative_score(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    max_value = numeric.max()
    if pd.isna(max_value) or max_value <= 0:
        return pd.Series([0] * len(numeric), index=numeric.index, dtype="Int64")
    return _clamp_score((numeric / max_value) * 100)


def _inverse_relative_score(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    max_value = numeric.max()
    if pd.isna(max_value) or max_value <= 0:
        return pd.Series([100] * len(numeric), index=numeric.index, dtype="Int64")
    return _clamp_score(100 - (numeric / max_value) * 100)


def _clamp_score(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0).clip(0, 100).round().astype("Int64")


def _numeric_series(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0)


def _stable_frame(dataframe: pd.DataFrame, *, sort_by: tuple[str, ...]) -> pd.DataFrame:
    return dataframe.sort_values(list(sort_by), kind="mergesort").reset_index(drop=True)


def _ensure_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
    required_columns: tuple[str, ...],
) -> None:
    missing = tuple(column for column in required_columns if column not in dataframe.columns)
    if missing:
        raise InventoryFeatureError(
            f"{dataset_name}: missing required columns: " + ", ".join(missing)
        )


def _clean_text_series(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()

