"""Deterministic competitive feature builders for Build 02.

These builders convert competitor signals and optional sales context into
normalized competitive pressure features. They do not rank entities, create
recommendations, detect anomalies, or generate explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


COMPETITOR_FEATURE_COLUMNS = ("competitive_pressure_score",)


class CompetitorFeatureError(ValueError):
    """Raised when competitive feature generation cannot proceed safely."""


def build_competitor_pressure_features(
    competitor_signals: pd.DataFrame,
    retailer_pos_clean: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Generate competitive pressure features."""

    _ensure_columns("competitor_signals", competitor_signals, ("entity_id",))
    signals = competitor_signals.copy()

    if "competitive_pressure_score" in signals.columns:
        score = _clamp_score(_numeric_series(signals["competitive_pressure_score"]))
    else:
        promotion_score = (
            _boolean_series(signals["competitor_promotion_active"]).astype(int) * 70
            if "competitor_promotion_active" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index)
        )
        discount_score = (
            _categorical_score(signals["competitor_discount_level"])
            if "competitor_discount_level" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index)
        )
        availability_score = (
            _clamp_score(_numeric_series(signals["competitor_availability_score"]))
            if "competitor_availability_score" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index, dtype="Int64")
        )
        sales_drop_score = (
            _clamp_score(_numeric_series(signals["regional_sales_drop_score"]))
            if "regional_sales_drop_score" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index, dtype="Int64")
        )
        score = _clamp_score(
            promotion_score * 0.30
            + discount_score * 0.25
            + availability_score * 0.25
            + sales_drop_score * 0.20
        )

    output = pd.DataFrame(
        {
            "entity_id": _clean_text_series(signals["entity_id"]),
            "competitive_pressure_score": score,
        }
    )

    if retailer_pos_clean is not None and not retailer_pos_clean.empty:
        sales_context = _sales_decline_proxy(retailer_pos_clean)
        output = output.merge(sales_context, on="entity_id", how="left")
        output["competitive_pressure_score"] = _clamp_score(
            output["competitive_pressure_score"].fillna(0) * 0.85
            + output["sales_decline_proxy_score"].fillna(0) * 0.15
        )
        output = output.drop(columns=["sales_decline_proxy_score"])

    return _stable_frame(output, sort_by=("entity_id",))


def build_competitor_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one entity-level competitive feature view."""

    if "competitor_signals" not in datasets:
        raise CompetitorFeatureError("competitor_signals is required.")

    output = build_competitor_pressure_features(
        datasets["competitor_signals"],
        datasets.get("retailer_pos_clean"),
    )
    for column in COMPETITOR_FEATURE_COLUMNS:
        output[column] = output[column].fillna(0).astype("Int64")
    return output.loc[:, ("entity_id", *COMPETITOR_FEATURE_COLUMNS)]


def _sales_decline_proxy(retailer_pos_clean: pd.DataFrame) -> pd.DataFrame:
    if not {"retailer_id", "sku_qty", "transaction_date"}.issubset(retailer_pos_clean.columns):
        return pd.DataFrame(columns=["entity_id", "sales_decline_proxy_score"])

    pos = retailer_pos_clean.copy()
    pos["entity_id"] = _clean_text_series(pos["retailer_id"])
    pos["sku_qty"] = _numeric_series(pos["sku_qty"])
    pos["transaction_date"] = pd.to_datetime(pos["transaction_date"], errors="coerce")
    max_date = pos["transaction_date"].max()
    recent = pos[pos["transaction_date"].ge(max_date - pd.Timedelta(days=30))]
    prior = pos[pos["transaction_date"].lt(max_date - pd.Timedelta(days=30))]

    recent_units = recent.groupby("entity_id")["sku_qty"].sum()
    prior_units = prior.groupby("entity_id")["sku_qty"].sum()
    entity_ids = sorted(set(recent_units.index).union(set(prior_units.index)))
    proxy = pd.DataFrame({"entity_id": entity_ids})
    proxy["recent_units"] = proxy["entity_id"].map(recent_units).fillna(0)
    proxy["prior_units"] = proxy["entity_id"].map(prior_units).fillna(0)
    proxy["sales_decline_proxy_score"] = _clamp_score(
        ((proxy["prior_units"] - proxy["recent_units"]) / proxy["prior_units"].replace(0, pd.NA)).fillna(0)
        * 100
    )
    return proxy.loc[:, ["entity_id", "sales_decline_proxy_score"]]


def _categorical_score(values: pd.Series) -> pd.Series:
    return (
        _clean_text_series(values)
        .str.lower()
        .map({"none": 0, "low": 30, "medium": 60, "moderate": 60, "high": 85, "critical": 100})
        .fillna(0)
        .astype("Int64")
    )


def _boolean_series(values: pd.Series) -> pd.Series:
    return _clean_text_series(values).str.lower().isin(("true", "1", "yes"))


def _numeric_series(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0)


def _clamp_score(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0).clip(0, 100).round().astype("Int64")


def _stable_frame(dataframe: pd.DataFrame, *, sort_by: tuple[str, ...]) -> pd.DataFrame:
    return dataframe.sort_values(list(sort_by), kind="mergesort").reset_index(drop=True)


def _ensure_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
    required_columns: tuple[str, ...],
) -> None:
    missing = tuple(column for column in required_columns if column not in dataframe.columns)
    if missing:
        raise CompetitorFeatureError(
            f"{dataset_name}: missing required columns: " + ", ".join(missing)
        )


def _clean_text_series(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()

