"""Deterministic sales feature builders for Build 02.

These builders convert processed POS, campaign, and grower context into
normalized commercial opportunity features. They do not rank entities, create
recommendations, detect anomalies, or generate explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


SALES_FEATURE_COLUMNS = (
    "historical_sales_score",
    "seasonal_product_relevance",
    "purchase_history_score",
    "crop_acreage_score",
    "sales_opportunity_score",
)


class SalesFeatureError(ValueError):
    """Raised when sales feature generation cannot proceed safely."""


def build_historical_sales_features(retailer_pos_clean: pd.DataFrame) -> pd.DataFrame:
    """Generate sales strength and purchase-history features from POS records."""

    _ensure_columns(
        "retailer_pos_clean",
        retailer_pos_clean,
        ("retailer_id", "transaction_id", "sku_qty", "sku_price", "transaction_date"),
    )
    pos = retailer_pos_clean.copy()
    pos["entity_id"] = _clean_text_series(pos["retailer_id"])
    pos["line_value"] = _numeric_series(pos["sku_qty"]) * _numeric_series(pos["sku_price"])
    pos["transaction_date"] = pd.to_datetime(pos["transaction_date"], errors="coerce")

    grouped = (
        pos.groupby("entity_id", as_index=False)
        .agg(
            total_sales_value=("line_value", "sum"),
            total_quantity=("sku_qty", lambda series: _numeric_series(series).sum()),
            transaction_count=("transaction_id", "nunique"),
            last_transaction_date=("transaction_date", "max"),
        )
        .sort_values("entity_id", kind="mergesort")
        .reset_index(drop=True)
    )
    max_date = grouped["last_transaction_date"].max()
    days_since_last = (max_date - grouped["last_transaction_date"]).dt.days.fillna(999)

    historical_sales_score = _relative_score(grouped["total_sales_value"])
    frequency_score = _relative_score(grouped["transaction_count"])
    recency_score = _clamp_score(100 - days_since_last * 5)
    purchase_history_score = _clamp_score(frequency_score * 0.6 + recency_score * 0.4)

    return _stable_frame(
        pd.DataFrame(
            {
                "entity_id": grouped["entity_id"],
                "historical_sales_score": historical_sales_score,
                "purchase_history_score": purchase_history_score,
            }
        ),
        sort_by=("entity_id",),
    )


def build_seasonal_relevance_features(
    retailer_pos_clean: pd.DataFrame,
    campaign_engagement_clean: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Generate seasonal product relevance from POS products and campaign context."""

    _ensure_columns("retailer_pos_clean", retailer_pos_clean, ("retailer_id", "sku_name"))
    pos = retailer_pos_clean.copy()
    pos["entity_id"] = _clean_text_series(pos["retailer_id"])

    if campaign_engagement_clean is None or campaign_engagement_clean.empty:
        grouped = pos.loc[:, ["entity_id"]].drop_duplicates()
        grouped["seasonal_product_relevance"] = 50
        return _stable_frame(grouped, sort_by=("entity_id",))

    _ensure_columns(
        "campaign_engagement_clean",
        campaign_engagement_clean,
        ("campaign_product",),
    )
    campaign_products = set(
        _clean_text_series(campaign_engagement_clean["campaign_product"])
        .str.lower()
        .loc[lambda series: series.ne("")]
        .tolist()
    )
    pos["sku_name_clean"] = _clean_text_series(pos["sku_name"]).str.lower()
    pos["campaign_match"] = pos["sku_name_clean"].isin(campaign_products).astype(int)

    grouped = (
        pos.groupby("entity_id", as_index=False)
        .agg(campaign_match_rate=("campaign_match", "mean"))
        .sort_values("entity_id", kind="mergesort")
        .reset_index(drop=True)
    )
    grouped["seasonal_product_relevance"] = _clamp_score(40 + grouped["campaign_match_rate"] * 60)
    return grouped.loc[:, ["entity_id", "seasonal_product_relevance"]]


def build_crop_acreage_features(growers: pd.DataFrame) -> pd.DataFrame:
    """Generate crop-acreage commercial scale features for grower entities."""

    _ensure_columns("growers", growers, ("grower_id", "grower_farm_size"))
    features = growers.copy()
    output = pd.DataFrame(
        {
            "entity_id": _clean_text_series(features["grower_id"]),
            "crop_acreage_score": _relative_score(_numeric_series(features["grower_farm_size"])),
        }
    )
    return _stable_frame(output, sort_by=("entity_id",))


def build_sales_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one entity-level sales feature view from available commercial inputs."""

    if "retailer_pos_clean" not in datasets and "growers" not in datasets:
        raise SalesFeatureError(
            "At least one sales input is required: retailer_pos_clean or growers."
        )

    feature_frames: list[pd.DataFrame] = []
    if "retailer_pos_clean" in datasets:
        sales_history = build_historical_sales_features(datasets["retailer_pos_clean"])
        seasonal_relevance = build_seasonal_relevance_features(
            datasets["retailer_pos_clean"],
            datasets.get("campaign_engagement_clean"),
        )
        feature_frames.extend([sales_history, seasonal_relevance])

    if "growers" in datasets:
        feature_frames.append(build_crop_acreage_features(datasets["growers"]))

    output = feature_frames[0]
    for frame in feature_frames[1:]:
        output = output.merge(frame, on="entity_id", how="outer")

    for column in SALES_FEATURE_COLUMNS:
        if column in output.columns:
            output[column] = output[column].fillna(0).astype("Int64")
        else:
            output[column] = pd.Series([0] * len(output), dtype="Int64")

    output["sales_opportunity_score"] = _clamp_score(
        output["historical_sales_score"] * 0.35
        + output["seasonal_product_relevance"] * 0.25
        + output["purchase_history_score"] * 0.25
        + output["crop_acreage_score"] * 0.15
    )

    return _stable_frame(
        output.loc[:, ("entity_id", *SALES_FEATURE_COLUMNS)],
        sort_by=("entity_id",),
    )


def _relative_score(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    max_value = numeric.max()
    if pd.isna(max_value) or max_value <= 0:
        return pd.Series([0] * len(numeric), index=numeric.index, dtype="Int64")
    return _clamp_score((numeric / max_value) * 100)


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
        raise SalesFeatureError(
            f"{dataset_name}: missing required columns: " + ", ".join(missing)
        )


def _clean_text_series(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()

