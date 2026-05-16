"""Deviation detection for Build 05.

This module compares current anomaly signals against baseline signals and
returns traceable deviation records. It does not classify severity, generate
alerts, create recommendations, modify priority scores, or format explanations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_ANOMALY_THRESHOLDS_PATH = Path("backend/config/anomaly_thresholds.yaml")


class DeviationDetectionError(ValueError):
    """Raised when deviation detection input violates the Build 05 contract."""


@dataclass(frozen=True)
class DetectorSpec:
    """Configured deviation detector metadata."""

    detector_id: str
    alert_type: str
    category: str
    current_signal: str
    baseline_signal: str
    deviation_direction: str
    minimum_deviation_score: float
    high_deviation_score: float
    critical_deviation_score: float
    current_signal_weight: float
    deviation_weight: float
    confidence_level: str
    evidence_fields: tuple[str, ...]

    @classmethod
    def from_mapping(cls, detector: Mapping[str, Any]) -> "DetectorSpec":
        weights = detector["severity_signal_weights"]
        return cls(
            detector_id=str(detector["detector_id"]),
            alert_type=str(detector["alert_type"]),
            category=str(detector["category"]),
            current_signal=str(detector["current_signal"]),
            baseline_signal=str(detector["baseline_signal"]),
            deviation_direction=str(detector["deviation_direction"]),
            minimum_deviation_score=float(detector["minimum_deviation_score"]),
            high_deviation_score=float(detector["high_deviation_score"]),
            critical_deviation_score=float(detector["critical_deviation_score"]),
            current_signal_weight=float(weights["current_signal_weight"]),
            deviation_weight=float(weights["deviation_weight"]),
            confidence_level=str(detector["confidence_level"]),
            evidence_fields=tuple(str(field) for field in detector["evidence_fields"]),
        )


@dataclass(frozen=True)
class DeviationRecord:
    """Traceable deviation detected by one configured detector."""

    entity_id: str
    territory_id: str
    detector_id: str
    alert_type: str
    category: str
    current_signal: str
    baseline_signal: str
    current_value: float
    baseline_value: float
    deviation_value: float
    deviation_direction: str
    minimum_deviation_score: float
    confidence_level: str
    evidence_signals: dict[str, Any]

    def to_row(self) -> dict[str, Any]:
        """Return stable row payload for downstream severity and alert steps."""

        return {
            "entity_id": self.entity_id,
            "territory_id": self.territory_id,
            "detector_id": self.detector_id,
            "alert_type": self.alert_type,
            "category": self.category,
            "current_signal": self.current_signal,
            "baseline_signal": self.baseline_signal,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "deviation_value": self.deviation_value,
            "deviation_direction": self.deviation_direction,
            "minimum_deviation_score": self.minimum_deviation_score,
            "confidence_level": self.confidence_level,
            "evidence_signals": self.evidence_signals,
            "deviation_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic deviation trace metadata."""

        return {
            "entity_id": self.entity_id,
            "detector_id": self.detector_id,
            "alert_type": self.alert_type,
            "current_signal": self.current_signal,
            "baseline_signal": self.baseline_signal,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "deviation_value": self.deviation_value,
            "deviation_direction": self.deviation_direction,
            "threshold_used": self.minimum_deviation_score,
            "evidence_signals": self.evidence_signals,
        }


def load_anomaly_threshold_config(
    config_path: Path | str = DEFAULT_ANOMALY_THRESHOLDS_PATH,
) -> dict[str, Any]:
    """Load and validate anomaly threshold configuration."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    _validate_threshold_config(config)
    return config


def list_detector_specs(
    config: Mapping[str, Any] | None = None,
) -> tuple[DetectorSpec, ...]:
    """Return configured detectors in deterministic order."""

    threshold_config = config or load_anomaly_threshold_config()
    detectors = [
        DetectorSpec.from_mapping(detector)
        for detector in threshold_config["detectors"].values()
    ]
    return tuple(sorted(detectors, key=lambda detector: detector.detector_id))


def detect_deviations_for_row(
    anomaly_row: Mapping[str, Any],
    detectors: Sequence[DetectorSpec] | None = None,
) -> tuple[DeviationRecord, ...]:
    """Detect configured deviations for one baseline-enriched anomaly row."""

    loaded_detectors = tuple(detectors) if detectors is not None else list_detector_specs()
    entity_id = str(anomaly_row.get("entity_id", "")).strip()
    if not entity_id:
        raise DeviationDetectionError("Deviation detection requires entity_id.")

    _validate_required_detector_fields(anomaly_row, loaded_detectors)

    records: list[DeviationRecord] = []
    for detector in loaded_detectors:
        current_value = _numeric_value(anomaly_row[detector.current_signal], detector.current_signal)
        baseline_value = _numeric_value(anomaly_row[detector.baseline_signal], detector.baseline_signal)
        deviation_value = _calculate_directional_deviation(
            current_value=current_value,
            baseline_value=baseline_value,
            deviation_direction=detector.deviation_direction,
        )
        if deviation_value < detector.minimum_deviation_score:
            continue
        records.append(
            DeviationRecord(
                entity_id=entity_id,
                territory_id=str(anomaly_row.get("territory_id", "")),
                detector_id=detector.detector_id,
                alert_type=detector.alert_type,
                category=detector.category,
                current_signal=detector.current_signal,
                baseline_signal=detector.baseline_signal,
                current_value=current_value,
                baseline_value=baseline_value,
                deviation_value=round(deviation_value, 4),
                deviation_direction=detector.deviation_direction,
                minimum_deviation_score=detector.minimum_deviation_score,
                confidence_level=detector.confidence_level,
                evidence_signals={
                    field: _to_builtin_value(anomaly_row[field])
                    for field in detector.evidence_fields
                    if field in anomaly_row
                },
            )
        )

    return tuple(sorted(records, key=lambda record: record.detector_id))


def build_deviation_view(
    baseline_feature_view: pd.DataFrame,
    detectors: Sequence[DetectorSpec] | None = None,
) -> pd.DataFrame:
    """Build stable deviation records for a baseline-enriched feature view."""

    loaded_detectors = tuple(detectors) if detectors is not None else list_detector_specs()
    rows: list[dict[str, Any]] = []
    for source_row in baseline_feature_view.to_dict(orient="records"):
        for record in detect_deviations_for_row(source_row, loaded_detectors):
            rows.append(record.to_row())

    output = pd.DataFrame(rows)
    if output.empty:
        return output
    return output.sort_values(
        ["entity_id", "alert_type", "detector_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _validate_threshold_config(config: Mapping[str, Any]) -> None:
    required_sections = ("score_range", "alert_categories", "confidence_levels", "detectors")
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise DeviationDetectionError(
            "Anomaly threshold config is missing required sections: "
            + ", ".join(missing_sections)
        )

    alert_categories = set(config["alert_categories"])
    confidence_levels = set(config["confidence_levels"])
    detector_ids: list[str] = []
    for detector in config["detectors"].values():
        detector_ids.append(str(detector["detector_id"]))
        if detector["category"] not in alert_categories:
            raise DeviationDetectionError(f"Unsupported alert category: {detector['category']}")
        if detector["confidence_level"] not in confidence_levels:
            raise DeviationDetectionError(
                f"Unsupported confidence level: {detector['confidence_level']}"
            )
        if detector["deviation_direction"] not in ("increase", "decrease"):
            raise DeviationDetectionError(
                f"Unsupported deviation_direction: {detector['deviation_direction']}"
            )
        weights = detector["severity_signal_weights"]
        if round(sum(float(weight) for weight in weights.values()), 6) != 1:
            raise DeviationDetectionError(
                f"Severity signal weights must sum to 1.0 for {detector['detector_id']}."
            )
    if len(detector_ids) != len(set(detector_ids)):
        raise DeviationDetectionError("Detector IDs must be unique.")


def _validate_required_detector_fields(
    anomaly_row: Mapping[str, Any],
    detectors: Sequence[DetectorSpec],
) -> None:
    required_fields = {
        field
        for detector in detectors
        for field in (detector.current_signal, detector.baseline_signal, *detector.evidence_fields)
    }
    missing_fields = sorted(field for field in required_fields if field not in anomaly_row)
    if missing_fields:
        raise DeviationDetectionError(
            "Baseline feature row is missing detector fields: "
            + ", ".join(missing_fields)
        )


def _calculate_directional_deviation(
    *,
    current_value: float,
    baseline_value: float,
    deviation_direction: str,
) -> float:
    if deviation_direction == "increase":
        return max(0.0, current_value - baseline_value)
    if deviation_direction == "decrease":
        return max(0.0, baseline_value - current_value)
    raise DeviationDetectionError(f"Unsupported deviation direction: {deviation_direction}")


def _numeric_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise DeviationDetectionError(f"Detector field must be numeric: {field}")
    numeric_value = float(numeric_value)
    if numeric_value < 0 or numeric_value > 100:
        raise DeviationDetectionError(f"Detector field must be within 0-100: {field}")
    return numeric_value


def _to_builtin_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
