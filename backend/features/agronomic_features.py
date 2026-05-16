"""Deterministic agronomic feature builders for Build 02.

These builders convert processed agronomic signal tables into normalized
feature scores. They do not generate priority rankings, recommendations,
anomaly alerts, explanation text, or API/frontend output.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


AGRONOMIC_FEATURE_COLUMNS = (
    "weather_risk_score",
    "pest_disease_risk_score",
    "crop_stage_risk_score",
    "ndvi_stress_score",
)

SEVERITY_SCORE_MAP = {
    "none": 0,
    "low": 30,
    "moderate": 55,
    "medium": 55,
    "high": 80,
    "critical": 95,
}

CROP_STAGE_RISK_MAP = {
    "seedling": 40,
    "vegetative": 45,
    "tillering": 55,
    "branching": 55,
    "flowering": 80,
    "fruiting": 75,
    "boll formation": 80,
    "pod formation": 75,
    "grain filling": 70,
    "tuber initiation": 70,
    "maturity": 35,
    "harvest": 20,
}

NDVI_STRESS_SCORE_MAP = {
    "none": 0,
    "low": 30,
    "moderate": 60,
    "medium": 60,
    "high": 85,
    "critical": 95,
}


class AgronomicFeatureError(ValueError):
    """Raised when agronomic feature generation cannot proceed safely."""


def build_crop_stage_features(crop_context: pd.DataFrame) -> pd.DataFrame:
    """Generate crop-stage vulnerability features."""

    _ensure_columns("crop_context", crop_context, ("entity_id", "crop_stage"))
    features = crop_context.copy()

    if "crop_stage_risk_score" in features.columns:
        score = _score_from_column(features["crop_stage_risk_score"])
    else:
        score = _categorical_score(features["crop_stage"], CROP_STAGE_RISK_MAP, default=40)

    output = pd.DataFrame(
        {
            "entity_id": _clean_text_series(features["entity_id"]),
            "crop_stage_risk_score": score,
        }
    )
    if "crop" in features.columns:
        output["crop"] = _clean_text_series(features["crop"]).str.lower()
    output["crop_stage"] = _clean_text_series(features["crop_stage"]).str.lower()

    return _stable_frame(output, sort_by=("entity_id",))


def build_weather_features(
    weather_signals: pd.DataFrame,
    crop_stage_features: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Generate weather risk features from weather and optional crop-stage context."""

    _ensure_columns("weather_signals", weather_signals, ("entity_id",))
    features = weather_signals.copy()

    if "weather_risk_score" in features.columns:
        score = _score_from_column(features["weather_risk_score"])
    else:
        _ensure_any_column(
            "weather_signals",
            features,
            ("rainfall_deviation_score", "rainfall_7d_mm", "humidity_percent", "temperature_c"),
        )
        score = _weather_score(features)

    output = pd.DataFrame(
        {
            "entity_id": _clean_text_series(features["entity_id"]),
            "weather_risk_score": score,
        }
    )
    if "date" in features.columns:
        output["date"] = _clean_text_series(features["date"])

    if crop_stage_features is not None and "crop_stage_risk_score" in crop_stage_features:
        stage_context = crop_stage_features.loc[
            :, ["entity_id", "crop_stage_risk_score"]
        ].drop_duplicates(subset=["entity_id"])
        output = output.merge(stage_context, on="entity_id", how="left")
        output["weather_risk_score"] = _clamp_score(
            output["weather_risk_score"].fillna(0) * 0.8
            + output["crop_stage_risk_score"].fillna(40) * 0.2
        )
        output = output.drop(columns=["crop_stage_risk_score"])

    return _stable_frame(output, sort_by=_sort_columns(output))


def build_pest_disease_features(pest_signals: pd.DataFrame) -> pd.DataFrame:
    """Generate pest/disease pressure features."""

    _ensure_columns("pest_signals", pest_signals, ("entity_id",))
    features = pest_signals.copy()

    if "pest_disease_risk_score" in features.columns:
        score = _score_from_column(features["pest_disease_risk_score"])
    else:
        _ensure_any_column(
            "pest_signals",
            features,
            ("alert_severity", "pest_alert_active"),
        )
        severity_score = (
            _categorical_score(features["alert_severity"], SEVERITY_SCORE_MAP, default=0)
            if "alert_severity" in features.columns
            else pd.Series([0] * len(features), index=features.index, dtype="Int64")
        )
        active_multiplier = (
            _boolean_series(features["pest_alert_active"]).map({True: 1.0, False: 0.0})
            if "pest_alert_active" in features.columns
            else pd.Series([1.0] * len(features), index=features.index)
        )
        score = _clamp_score(severity_score * active_multiplier)

    output = pd.DataFrame(
        {
            "entity_id": _clean_text_series(features["entity_id"]),
            "pest_disease_risk_score": score,
        }
    )
    if "date" in features.columns:
        output["date"] = _clean_text_series(features["date"])
    if "pest_or_disease_type" in features.columns:
        output["pest_or_disease_type"] = _clean_text_series(
            features["pest_or_disease_type"]
        ).str.lower()
    if "source_type" in features.columns:
        output["source_type"] = _clean_text_series(features["source_type"]).str.lower()

    return _stable_frame(output, sort_by=_sort_columns(output))


def build_ndvi_features(ndvi_signals: pd.DataFrame) -> pd.DataFrame:
    """Generate NDVI crop-stress features."""

    _ensure_columns("ndvi_signals", ndvi_signals, ("entity_id",))
    features = ndvi_signals.copy()

    if "ndvi_stress_score" in features.columns:
        score = _score_from_column(features["ndvi_stress_score"])
    else:
        _ensure_any_column(
            "ndvi_signals",
            features,
            ("ndvi_drop_percent", "ndvi_current", "ndvi_baseline", "ndvi_stress_level"),
        )
        score = _ndvi_score(features)

    output = pd.DataFrame(
        {
            "entity_id": _clean_text_series(features["entity_id"]),
            "ndvi_stress_score": score,
        }
    )
    if "date" in features.columns:
        output["date"] = _clean_text_series(features["date"])
    if "ndvi_stress_level" in features.columns:
        output["ndvi_stress_level"] = _clean_text_series(
            features["ndvi_stress_level"]
        ).str.lower()

    return _stable_frame(output, sort_by=_sort_columns(output))


def build_agronomic_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one entity-level agronomic feature view from available signal tables."""

    feature_frames: list[pd.DataFrame] = []
    crop_stage_features: pd.DataFrame | None = None

    if "crop_context" in datasets:
        crop_stage_features = build_crop_stage_features(datasets["crop_context"])
        feature_frames.append(_latest_by_entity(crop_stage_features))

    if "weather_signals" in datasets:
        feature_frames.append(
            _latest_by_entity(
                build_weather_features(datasets["weather_signals"], crop_stage_features)
            )
        )

    if "pest_signals" in datasets:
        feature_frames.append(
            _latest_by_entity(build_pest_disease_features(datasets["pest_signals"]))
        )

    if "ndvi_signals" in datasets:
        feature_frames.append(_latest_by_entity(build_ndvi_features(datasets["ndvi_signals"])))

    if not feature_frames:
        raise AgronomicFeatureError(
            "At least one agronomic input is required: crop_context, "
            "weather_signals, pest_signals, or ndvi_signals."
        )

    output = feature_frames[0]
    for frame in feature_frames[1:]:
        output = output.merge(frame, on="entity_id", how="outer")

    for column in AGRONOMIC_FEATURE_COLUMNS:
        if column in output.columns:
            output[column] = output[column].fillna(0).astype("Int64")
        else:
            output[column] = pd.Series([0] * len(output), dtype="Int64")

    return _stable_frame(
        output.loc[:, ("entity_id", *AGRONOMIC_FEATURE_COLUMNS)],
        sort_by=("entity_id",),
    )


def _weather_score(features: pd.DataFrame) -> pd.Series:
    if "rainfall_deviation_score" in features.columns:
        rainfall_deviation = _numeric_series(features["rainfall_deviation_score"])
    elif "rainfall_7d_mm" in features.columns:
        rainfall_deviation = _numeric_series(features["rainfall_7d_mm"]) / 2
    else:
        rainfall_deviation = pd.Series([0] * len(features), index=features.index)
    humidity = (
        _numeric_series(features["humidity_percent"])
        if "humidity_percent" in features.columns
        else pd.Series([50] * len(features), index=features.index)
    )
    temperature = (
        _numeric_series(features["temperature_c"])
        if "temperature_c" in features.columns
        else pd.Series([28] * len(features), index=features.index)
    )
    temperature_pressure = (temperature - 25).abs() * 4

    return _clamp_score(
        rainfall_deviation.fillna(0) * 0.45
        + humidity.fillna(50) * 0.35
        + temperature_pressure.fillna(0) * 0.20
    )


def _ndvi_score(features: pd.DataFrame) -> pd.Series:
    if "ndvi_drop_percent" in features.columns:
        return _clamp_score(_numeric_series(features["ndvi_drop_percent"]).fillna(0) * 3)

    if {"ndvi_current", "ndvi_baseline"}.issubset(features.columns):
        current = _numeric_series(features["ndvi_current"])
        baseline = _numeric_series(features["ndvi_baseline"])
        drop_percent = ((baseline - current) / baseline.replace(0, pd.NA)) * 100
        return _clamp_score(drop_percent.fillna(0) * 3)

    return _categorical_score(features["ndvi_stress_level"], NDVI_STRESS_SCORE_MAP, default=0)


def _score_from_column(values: pd.Series) -> pd.Series:
    return _clamp_score(_numeric_series(values))


def _categorical_score(
    values: pd.Series,
    mapping: Mapping[str, int],
    *,
    default: int,
) -> pd.Series:
    normalized = _clean_text_series(values).str.lower()
    return normalized.map(mapping).fillna(default).astype("Int64")


def _boolean_series(values: pd.Series) -> pd.Series:
    normalized = _clean_text_series(values).str.lower()
    return normalized.isin(("true", "1", "yes"))


def _numeric_series(values: pd.Series | int | float) -> pd.Series:
    if isinstance(values, pd.Series):
        return pd.to_numeric(values, errors="coerce")
    return pd.Series([values])


def _clamp_score(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0).clip(0, 100).round().astype("Int64")


def _latest_by_entity(dataframe: pd.DataFrame) -> pd.DataFrame:
    if "date" not in dataframe.columns:
        return dataframe.drop_duplicates(subset=["entity_id"], keep="last")

    return (
        dataframe.sort_values(["entity_id", "date"], kind="mergesort")
        .drop_duplicates(subset=["entity_id"], keep="last")
        .drop(columns=["date"])
        .reset_index(drop=True)
    )


def _sort_columns(dataframe: pd.DataFrame) -> tuple[str, ...]:
    sort_columns = ["entity_id"]
    if "date" in dataframe.columns:
        sort_columns.append("date")
    return tuple(sort_columns)


def _stable_frame(dataframe: pd.DataFrame, *, sort_by: tuple[str, ...]) -> pd.DataFrame:
    return dataframe.sort_values(list(sort_by), kind="mergesort").reset_index(drop=True)


def _ensure_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
    required_columns: tuple[str, ...],
) -> None:
    missing = tuple(column for column in required_columns if column not in dataframe.columns)
    if missing:
        raise AgronomicFeatureError(
            f"{dataset_name}: missing required columns: " + ", ".join(missing)
        )


def _ensure_any_column(
    dataset_name: str,
    dataframe: pd.DataFrame,
    candidate_columns: tuple[str, ...],
) -> None:
    if not any(column in dataframe.columns for column in candidate_columns):
        raise AgronomicFeatureError(
            f"{dataset_name}: expected at least one of: "
            + ", ".join(candidate_columns)
        )


def _clean_text_series(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()
