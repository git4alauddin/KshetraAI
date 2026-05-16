"""Severity classification for Build 05 anomaly deviations.

This module converts deviation records into severity scores and labels. It does
not generate alerts, recommendations, priority rankings, API responses,
frontend behavior, or human-readable explanations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.anomaly.deviation_detector import (
    DeviationRecord,
    DetectorSpec,
    list_detector_specs,
    load_anomaly_threshold_config,
)


class SeverityClassificationError(ValueError):
    """Raised when anomaly severity classification cannot proceed."""


@dataclass(frozen=True)
class SeverityClassification:
    """Traceable severity classification for one detected deviation."""

    entity_id: str
    detector_id: str
    severity_score: float
    severity_level: str
    severity_level_key: str
    severity_rank: int
    score_components: dict[str, float]
    applied_weights: dict[str, float]

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic severity trace metadata."""

        return {
            "entity_id": self.entity_id,
            "detector_id": self.detector_id,
            "severity_score": self.severity_score,
            "severity_level": self.severity_level,
            "severity_level_key": self.severity_level_key,
            "severity_rank": self.severity_rank,
            "score_components": self.score_components,
            "applied_weights": self.applied_weights,
        }


def classify_deviation_severity(
    deviation: DeviationRecord | Mapping[str, Any],
    detector: DetectorSpec | None = None,
    config: Mapping[str, Any] | None = None,
) -> SeverityClassification:
    """Classify one deviation into a configured severity level."""

    threshold_config = config or load_anomaly_threshold_config()
    deviation_row = _deviation_to_mapping(deviation)
    detector_spec = detector or _lookup_detector(deviation_row["detector_id"])

    severity_score = _calculate_severity_score(deviation_row, detector_spec, threshold_config)
    level_key, level_config = _classify_score(severity_score, threshold_config)

    return SeverityClassification(
        entity_id=str(deviation_row["entity_id"]),
        detector_id=str(deviation_row["detector_id"]),
        severity_score=severity_score,
        severity_level=str(level_config["label"]),
        severity_level_key=level_key,
        severity_rank=int(level_config["severity_rank"]),
        score_components={
            "current_value": float(deviation_row["current_value"]),
            "deviation_value": float(deviation_row["deviation_value"]),
        },
        applied_weights={
            "current_signal_weight": detector_spec.current_signal_weight,
            "deviation_weight": detector_spec.deviation_weight,
        },
    )


def add_severity_classification(
    deviation_view: pd.DataFrame,
    detectors: Sequence[DetectorSpec] | None = None,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Add severity score, label, and trace columns to deviation rows."""

    if deviation_view.empty:
        return deviation_view.copy()

    threshold_config = config or load_anomaly_threshold_config()
    detector_map = {
        detector.detector_id: detector
        for detector in (tuple(detectors) if detectors is not None else list_detector_specs(threshold_config))
    }
    output = deviation_view.copy()
    classifications: list[SeverityClassification] = []

    for row in output.to_dict(orient="records"):
        detector_id = str(row["detector_id"])
        if detector_id not in detector_map:
            raise SeverityClassificationError(f"No detector config found for detector_id: {detector_id}")
        classifications.append(
            classify_deviation_severity(row, detector_map[detector_id], threshold_config)
        )

    output["severity_score"] = [
        classification.severity_score
        for classification in classifications
    ]
    output["severity_level"] = [
        classification.severity_level
        for classification in classifications
    ]
    output["severity_level_key"] = [
        classification.severity_level_key
        for classification in classifications
    ]
    output["severity_rank"] = [
        classification.severity_rank
        for classification in classifications
    ]
    output["severity_trace"] = [
        classification.to_trace()
        for classification in classifications
    ]
    return output.sort_values(
        ["entity_id", "severity_rank", "alert_type", "detector_id"],
        ascending=[True, False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)


def _calculate_severity_score(
    deviation_row: Mapping[str, Any],
    detector: DetectorSpec,
    config: Mapping[str, Any],
) -> float:
    current_value = _numeric_value(deviation_row["current_value"], "current_value")
    deviation_value = _numeric_value(deviation_row["deviation_value"], "deviation_value")
    score = (
        current_value * detector.current_signal_weight
        + deviation_value * detector.deviation_weight
    )
    if config["detection_policy"].get("clamp_severity_score_to_range", True):
        score = _clamp_score(
            score,
            min_score=float(config["score_range"]["min"]),
            max_score=float(config["score_range"]["max"]),
        )
    return round(score, 4)


def _classify_score(
    severity_score: float,
    config: Mapping[str, Any],
) -> tuple[str, Mapping[str, Any]]:
    for level_key, level_config in _ordered_levels(config):
        if severity_score >= float(level_config["min_score"]):
            return level_key, level_config
    raise SeverityClassificationError(
        f"Severity score {severity_score:g} did not match any configured severity level."
    )


def _ordered_levels(
    config: Mapping[str, Any],
) -> tuple[tuple[str, Mapping[str, Any]], ...]:
    return tuple(
        sorted(
            config["severity_levels"].items(),
            key=lambda item: float(item[1]["min_score"]),
            reverse=True,
        )
    )


def _lookup_detector(detector_id: str) -> DetectorSpec:
    for detector in list_detector_specs():
        if detector.detector_id == detector_id:
            return detector
    raise SeverityClassificationError(f"No detector config found for detector_id: {detector_id}")


def _deviation_to_mapping(
    deviation: DeviationRecord | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(deviation, DeviationRecord):
        return deviation.to_row()

    required_fields = (
        "entity_id",
        "detector_id",
        "current_value",
        "deviation_value",
    )
    missing_fields = [field for field in required_fields if field not in deviation]
    if missing_fields:
        raise SeverityClassificationError(
            "Deviation record is missing required fields: "
            + ", ".join(missing_fields)
        )
    return deviation


def _numeric_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise SeverityClassificationError(f"Severity field must be numeric: {field}")
    numeric_value = float(numeric_value)
    if numeric_value < 0 or numeric_value > 100:
        raise SeverityClassificationError(f"Severity field must be within 0-100: {field}")
    return numeric_value


def _clamp_score(score: float, *, min_score: float, max_score: float) -> float:
    return max(min_score, min(max_score, score))
