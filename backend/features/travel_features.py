"""Deterministic travel feature builders for Build 02.

These builders convert lightweight travel signals into normalized route cost
features. They do not optimize routes, rank entities, create recommendations,
detect anomalies, or generate explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


TRAVEL_FEATURE_COLUMNS = ("travel_cost_score",)


class TravelFeatureError(ValueError):
    """Raised when travel feature generation cannot proceed safely."""


def build_travel_cost_features(travel_signals: pd.DataFrame) -> pd.DataFrame:
    """Generate travel-cost features from distance, time, and clustering signals."""

    _ensure_columns("travel_signals", travel_signals, ("entity_id",))
    signals = travel_signals.copy()

    if "travel_cost_score" in signals.columns:
        score = _clamp_score(_numeric_series(signals["travel_cost_score"]))
    else:
        _ensure_any_column(
            "travel_signals",
            signals,
            ("distance_km", "estimated_route_time_min", "nearby_cluster_count", "route_efficiency_score"),
        )
        distance_penalty = (
            _relative_score(_numeric_series(signals["distance_km"]))
            if "distance_km" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index, dtype="Int64")
        )
        time_penalty = (
            _relative_score(_numeric_series(signals["estimated_route_time_min"]))
            if "estimated_route_time_min" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index, dtype="Int64")
        )
        cluster_bonus = (
            _relative_score(_numeric_series(signals["nearby_cluster_count"]))
            if "nearby_cluster_count" in signals.columns
            else pd.Series([0] * len(signals), index=signals.index, dtype="Int64")
        )
        route_efficiency = (
            _clamp_score(_numeric_series(signals["route_efficiency_score"]))
            if "route_efficiency_score" in signals.columns
            else cluster_bonus
        )
        score = _clamp_score(
            distance_penalty * 0.45
            + time_penalty * 0.35
            + (100 - route_efficiency) * 0.20
        )

    return _stable_frame(
        pd.DataFrame(
            {
                "entity_id": _clean_text_series(signals["entity_id"]),
                "travel_cost_score": score,
            }
        ),
        sort_by=("entity_id",),
    )


def build_travel_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one entity-level travel feature view."""

    if "travel_signals" not in datasets:
        raise TravelFeatureError("travel_signals is required.")

    output = build_travel_cost_features(datasets["travel_signals"])
    output["travel_cost_score"] = output["travel_cost_score"].fillna(0).astype("Int64")
    return output.loc[:, ("entity_id", *TRAVEL_FEATURE_COLUMNS)]


def _relative_score(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    max_value = numeric.max()
    if pd.isna(max_value) or max_value <= 0:
        return pd.Series([0] * len(numeric), index=numeric.index, dtype="Int64")
    return _clamp_score((numeric / max_value) * 100)


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
        raise TravelFeatureError(
            f"{dataset_name}: missing required columns: " + ", ".join(missing)
        )


def _ensure_any_column(
    dataset_name: str,
    dataframe: pd.DataFrame,
    candidate_columns: tuple[str, ...],
) -> None:
    if not any(column in dataframe.columns for column in candidate_columns):
        raise TravelFeatureError(
            f"{dataset_name}: expected at least one of: "
            + ", ".join(candidate_columns)
        )


def _clean_text_series(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()

