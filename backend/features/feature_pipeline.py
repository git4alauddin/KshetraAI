"""Feature pipeline output views for KshetraAI Build 02.

This module orchestrates existing feature builders into stable feature-ready
views. It does not rank entities, generate recommendations, detect anomalies,
generate explanation text, or implement API/frontend behavior.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from backend.features.agronomic_features import build_agronomic_feature_view
from backend.features.competitor_features import build_competitor_feature_view
from backend.features.feature_registry import feature_registry_rows, list_feature_names
from backend.features.inventory_features import build_inventory_feature_view
from backend.features.relationship_features import build_relationship_feature_view
from backend.features.sales_features import build_sales_feature_view
from backend.features.travel_features import build_travel_feature_view


FEATURE_OUTPUT_VIEW_ORDER = (
    "priority_feature_view",
    "contextual_feature_view",
    "anomaly_feature_view",
    "feature_registry",
)

ENTITY_CONTEXT_COLUMNS = (
    "entity_id",
    "territory_id",
    "entity_type",
    "primary_crop",
)

PRIORITY_FEATURE_COLUMNS = list_feature_names()

CONTEXTUAL_FEATURE_COLUMNS = (
    "entity_id",
    "territory_id",
    "entity_type",
    "primary_crop",
    "weather_risk_score",
    "pest_disease_risk_score",
    "crop_stage_risk_score",
    "inventory_need_score",
    "sales_opportunity_score",
    "relationship_need_score",
    "competitive_pressure_score",
    "account_priority_score",
    "campaign_engagement_score",
)

ANOMALY_FEATURE_COLUMNS = (
    "entity_id",
    "territory_id",
    "weather_risk_score",
    "pest_disease_risk_score",
    "ndvi_stress_score",
    "sales_opportunity_score",
    "inventory_need_score",
    "stockout_risk_score",
    "competitive_pressure_score",
)


class FeaturePipelineError(ValueError):
    """Raised when feature output views cannot be built safely."""


def build_feature_output_views(
    datasets: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Build all Build 02 feature output views in stable order."""

    feature_view = build_combined_feature_view(datasets)
    priority_feature_view = _select_columns(
        feature_view,
        ("entity_id", "territory_id", "entity_type", "primary_crop", *PRIORITY_FEATURE_COLUMNS),
    )
    contextual_feature_view = _select_columns(feature_view, CONTEXTUAL_FEATURE_COLUMNS)
    anomaly_feature_view = _select_columns(feature_view, ANOMALY_FEATURE_COLUMNS)
    registry = build_feature_registry_view()

    return {
        "priority_feature_view": priority_feature_view,
        "contextual_feature_view": contextual_feature_view,
        "anomaly_feature_view": anomaly_feature_view,
        "feature_registry": registry,
    }


def build_combined_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one stable entity-level feature table from available inputs."""

    feature_frames = _build_available_feature_frames(datasets)
    if not feature_frames:
        raise FeaturePipelineError("No feature-producing input datasets were provided.")

    base = _build_entity_base(datasets, feature_frames)
    output = base
    for frame in feature_frames:
        output = output.merge(frame, on="entity_id", how="left")

    for feature_name in PRIORITY_FEATURE_COLUMNS:
        if feature_name in output.columns:
            output[feature_name] = output[feature_name].fillna(0).astype("Int64")
        else:
            output[feature_name] = pd.Series([0] * len(output), dtype="Int64")

    output = _validate_feature_ranges(output, PRIORITY_FEATURE_COLUMNS)
    return _stable_frame(
        output.loc[:, ("entity_id", "territory_id", "entity_type", "primary_crop", *PRIORITY_FEATURE_COLUMNS)],
        sort_by=("entity_id",),
    )


def build_feature_registry_view() -> pd.DataFrame:
    """Return feature registry metadata as a stable DataFrame."""

    return pd.DataFrame(feature_registry_rows()).sort_values(
        "feature_name",
        kind="mergesort",
    ).reset_index(drop=True)


def write_feature_output_views(
    feature_views: Mapping[str, pd.DataFrame],
    output_dir: Path | str,
) -> dict[str, Path]:
    """Write Build 02 feature output views as deterministic CSV files."""

    resolved_output_dir = Path(output_dir).expanduser().resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    output_paths: dict[str, Path] = {}
    for view_name in FEATURE_OUTPUT_VIEW_ORDER:
        output_path = resolved_output_dir / f"{view_name}.csv"
        feature_views[view_name].to_csv(output_path, index=False, lineterminator="\n")
        output_paths[view_name] = output_path
    return output_paths


def _build_available_feature_frames(
    datasets: Mapping[str, pd.DataFrame],
) -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []

    if any(key in datasets for key in ("crop_context", "weather_signals", "pest_signals", "ndvi_signals")):
        frames.append(build_agronomic_feature_view(datasets))

    if "retailer_pos_clean" in datasets or "growers" in datasets:
        frames.append(build_sales_feature_view(datasets))

    if "retailer_inventory_weekly_clean" in datasets:
        frames.append(build_inventory_feature_view(datasets))

    if any(key in datasets for key in ("retailer_visit_log_clean", "visit_entities", "campaign_engagement_clean")):
        frames.append(build_relationship_feature_view(datasets))

    if "competitor_signals" in datasets:
        frames.append(build_competitor_feature_view(datasets))

    if "travel_signals" in datasets:
        frames.append(build_travel_feature_view(datasets))

    return frames


def _build_entity_base(
    datasets: Mapping[str, pd.DataFrame],
    feature_frames: list[pd.DataFrame],
) -> pd.DataFrame:
    if "visit_entities" in datasets and "entity_id" in datasets["visit_entities"].columns:
        base = datasets["visit_entities"].copy()
        for column in ENTITY_CONTEXT_COLUMNS:
            if column not in base.columns:
                base[column] = ""
        return _stable_frame(base.loc[:, list(ENTITY_CONTEXT_COLUMNS)], sort_by=("entity_id",))

    entity_ids = sorted(
        {
            str(entity_id)
            for frame in feature_frames
            for entity_id in frame["entity_id"].astype("string").fillna("").tolist()
            if str(entity_id).strip()
        }
    )
    return pd.DataFrame(
        {
            "entity_id": entity_ids,
            "territory_id": [""] * len(entity_ids),
            "entity_type": [""] * len(entity_ids),
            "primary_crop": [""] * len(entity_ids),
        }
    )


def _select_columns(dataframe: pd.DataFrame, columns: tuple[str, ...]) -> pd.DataFrame:
    selected = dataframe.copy()
    for column in columns:
        if column not in selected.columns:
            selected[column] = 0 if column.endswith("_score") else ""
    return selected.loc[:, list(columns)]


def _validate_feature_ranges(
    dataframe: pd.DataFrame,
    feature_columns: tuple[str, ...],
) -> pd.DataFrame:
    invalid_columns: list[str] = []
    for column in feature_columns:
        values = pd.to_numeric(dataframe[column], errors="coerce")
        if values.isna().any() or not values.between(0, 100).all():
            invalid_columns.append(column)
    if invalid_columns:
        raise FeaturePipelineError(
            "Feature columns must be numeric and within 0-100: "
            + ", ".join(invalid_columns)
        )
    return dataframe


def _stable_frame(dataframe: pd.DataFrame, *, sort_by: tuple[str, ...]) -> pd.DataFrame:
    return dataframe.sort_values(list(sort_by), kind="mergesort").reset_index(drop=True)

