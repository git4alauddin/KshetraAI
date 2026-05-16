"""Alert generation for Build 05 anomaly deviations.

This module turns severity-classified deviations into structured anomaly alert
records and trace log rows. It does not generate priority rankings,
recommendations, explanation text, API responses, or frontend behavior.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.anomaly.trend_analyzer import (
    TrendAnalysisError,
    build_supporting_evidence,
    summarize_deviation_trend,
)


DETERMINISTIC_DETECTED_AT = "configured_static_detection_run"

ALERT_OUTPUT_COLUMNS = [
    "alert_id",
    "entity_id",
    "territory_id",
    "detector_id",
    "alert_type",
    "category",
    "severity_score",
    "severity_level",
    "severity_rank",
    "confidence_level",
    "supporting_evidence",
    "detected_at",
    "anomaly_trace",
]

TRACE_OUTPUT_COLUMNS = [
    "alert_id",
    "entity_id",
    "territory_id",
    "detector_id",
    "alert_type",
    "current_signal",
    "baseline_signal",
    "current_value",
    "baseline_value",
    "deviation_value",
    "threshold_used",
    "severity_score",
    "severity_level",
    "confidence_level",
    "triggered_rule",
    "detected_at",
]


class AlertGenerationError(ValueError):
    """Raised when anomaly alerts cannot be generated safely."""


@dataclass(frozen=True)
class AnomalyAlert:
    """Structured anomaly or opportunity alert with trace metadata."""

    alert_id: str
    entity_id: str
    territory_id: str
    detector_id: str
    alert_type: str
    category: str
    severity_score: float
    severity_level: str
    severity_rank: int
    confidence_level: str
    supporting_evidence: tuple[dict[str, Any], ...]
    detected_at: str
    anomaly_trace: dict[str, Any]

    def to_row(self) -> dict[str, Any]:
        """Return a stable alert output row."""

        return {
            "alert_id": self.alert_id,
            "entity_id": self.entity_id,
            "territory_id": self.territory_id,
            "detector_id": self.detector_id,
            "alert_type": self.alert_type,
            "category": self.category,
            "severity_score": self.severity_score,
            "severity_level": self.severity_level,
            "severity_rank": self.severity_rank,
            "confidence_level": self.confidence_level,
            "supporting_evidence": list(self.supporting_evidence),
            "detected_at": self.detected_at,
            "anomaly_trace": self.anomaly_trace,
        }

    def to_trace_row(self) -> dict[str, Any]:
        """Return a stable trace log row for this alert."""

        return {
            "alert_id": self.alert_id,
            "entity_id": self.entity_id,
            "territory_id": self.territory_id,
            "detector_id": self.detector_id,
            "alert_type": self.alert_type,
            "current_signal": self.anomaly_trace["current_signal"],
            "baseline_signal": self.anomaly_trace["baseline_signal"],
            "current_value": self.anomaly_trace["current_value"],
            "baseline_value": self.anomaly_trace["baseline_value"],
            "deviation_value": self.anomaly_trace["deviation_value"],
            "threshold_used": self.anomaly_trace["threshold_used"],
            "severity_score": self.severity_score,
            "severity_level": self.severity_level,
            "confidence_level": self.confidence_level,
            "triggered_rule": self.detector_id,
            "detected_at": self.detected_at,
        }


def generate_alert(
    severity_row: Mapping[str, Any],
    *,
    detected_at: str = DETERMINISTIC_DETECTED_AT,
) -> AnomalyAlert:
    """Generate one evidence-backed alert from one severity-classified deviation."""

    _validate_alert_row(severity_row)
    entity_id = str(severity_row["entity_id"]).strip()
    detector_id = str(severity_row["detector_id"]).strip()
    if not entity_id:
        raise AlertGenerationError("Alert generation requires entity_id.")
    if not detector_id:
        raise AlertGenerationError("Alert generation requires detector_id.")

    try:
        trend_summary = summarize_deviation_trend(severity_row)
        supporting_evidence = build_supporting_evidence(severity_row)
    except TrendAnalysisError as error:
        raise AlertGenerationError(str(error)) from error
    anomaly_trace = _build_anomaly_trace(severity_row, trend_summary.to_trace())

    return AnomalyAlert(
        alert_id=_build_alert_id(entity_id, detector_id),
        entity_id=entity_id,
        territory_id=str(severity_row.get("territory_id", "")),
        detector_id=detector_id,
        alert_type=str(severity_row["alert_type"]),
        category=str(severity_row["category"]),
        severity_score=_numeric_value(severity_row["severity_score"], "severity_score"),
        severity_level=str(severity_row["severity_level"]),
        severity_rank=int(severity_row["severity_rank"]),
        confidence_level=str(severity_row["confidence_level"]),
        supporting_evidence=supporting_evidence,
        detected_at=str(detected_at),
        anomaly_trace=anomaly_trace,
    )


def build_alert_view(
    severity_view: pd.DataFrame,
    *,
    detected_at: str = DETERMINISTIC_DETECTED_AT,
) -> pd.DataFrame:
    """Build stable anomaly alert rows from severity-classified deviations."""

    if severity_view.empty:
        return pd.DataFrame(columns=ALERT_OUTPUT_COLUMNS)

    alerts = [
        generate_alert(row, detected_at=detected_at)
        for row in severity_view.to_dict(orient="records")
    ]
    output = pd.DataFrame(
        [alert.to_row() for alert in alerts],
        columns=ALERT_OUTPUT_COLUMNS,
    )
    return _sort_alerts(output)


def build_trace_log_view(alert_view: pd.DataFrame) -> pd.DataFrame:
    """Build deterministic anomaly trace log rows from generated alerts."""

    if alert_view.empty:
        return pd.DataFrame(columns=TRACE_OUTPUT_COLUMNS)

    _validate_alert_view_for_trace(alert_view)
    rows = []
    for alert_row in alert_view.to_dict(orient="records"):
        alert = _alert_from_row(alert_row)
        rows.append(alert.to_trace_row())

    output = pd.DataFrame(rows, columns=TRACE_OUTPUT_COLUMNS)
    return output.sort_values(
        ["entity_id", "alert_type", "detector_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _build_alert_id(entity_id: str, detector_id: str) -> str:
    return f"ALERT_{_normalize_id(entity_id)}_{_normalize_id(detector_id)}"


def _normalize_id(value: str) -> str:
    return "".join(
        character if character.isalnum() else "_"
        for character in value.upper()
    ).strip("_")


def _build_anomaly_trace(
    severity_row: Mapping[str, Any],
    trend_trace: Mapping[str, Any],
) -> dict[str, Any]:
    deviation_trace = severity_row.get("deviation_trace", {})
    severity_trace = severity_row.get("severity_trace", {})
    return {
        "entity_id": str(severity_row["entity_id"]),
        "territory_id": str(severity_row.get("territory_id", "")),
        "detector_id": str(severity_row["detector_id"]),
        "alert_type": str(severity_row["alert_type"]),
        "category": str(severity_row["category"]),
        "current_signal": str(severity_row["current_signal"]),
        "baseline_signal": str(severity_row["baseline_signal"]),
        "current_value": _numeric_value(severity_row["current_value"], "current_value"),
        "baseline_value": _numeric_value(severity_row["baseline_value"], "baseline_value"),
        "deviation_value": _numeric_value(severity_row["deviation_value"], "deviation_value"),
        "threshold_used": _numeric_value(
            severity_row["minimum_deviation_score"],
            "minimum_deviation_score",
        ),
        "severity_score": _numeric_value(severity_row["severity_score"], "severity_score"),
        "severity_level": str(severity_row["severity_level"]),
        "confidence_level": str(severity_row["confidence_level"]),
        "triggered_rule": str(severity_row["detector_id"]),
        "trend": dict(trend_trace),
        "deviation_trace": dict(deviation_trace) if isinstance(deviation_trace, Mapping) else {},
        "severity_trace": dict(severity_trace) if isinstance(severity_trace, Mapping) else {},
    }


def _validate_alert_row(severity_row: Mapping[str, Any]) -> None:
    required_fields = (
        "entity_id",
        "territory_id",
        "detector_id",
        "alert_type",
        "category",
        "current_signal",
        "baseline_signal",
        "current_value",
        "baseline_value",
        "deviation_value",
        "minimum_deviation_score",
        "confidence_level",
        "evidence_signals",
        "severity_score",
        "severity_level",
        "severity_rank",
    )
    missing_fields = [field for field in required_fields if field not in severity_row]
    if missing_fields:
        raise AlertGenerationError(
            "Severity row is missing alert fields: "
            + ", ".join(missing_fields)
        )


def _validate_alert_view_for_trace(alert_view: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in ALERT_OUTPUT_COLUMNS
        if column not in alert_view.columns
    ]
    if missing_columns:
        raise AlertGenerationError(
            "Alert view is missing trace columns: "
            + ", ".join(missing_columns)
        )


def _alert_from_row(alert_row: Mapping[str, Any]) -> AnomalyAlert:
    supporting_evidence = alert_row["supporting_evidence"]
    if not isinstance(supporting_evidence, list) or not supporting_evidence:
        raise AlertGenerationError("Alert trace rows require non-empty supporting_evidence.")
    anomaly_trace = alert_row["anomaly_trace"]
    if not isinstance(anomaly_trace, Mapping):
        raise AlertGenerationError("Alert trace rows require anomaly_trace metadata.")
    return AnomalyAlert(
        alert_id=str(alert_row["alert_id"]),
        entity_id=str(alert_row["entity_id"]),
        territory_id=str(alert_row["territory_id"]),
        detector_id=str(alert_row["detector_id"]),
        alert_type=str(alert_row["alert_type"]),
        category=str(alert_row["category"]),
        severity_score=_numeric_value(alert_row["severity_score"], "severity_score"),
        severity_level=str(alert_row["severity_level"]),
        severity_rank=int(alert_row["severity_rank"]),
        confidence_level=str(alert_row["confidence_level"]),
        supporting_evidence=tuple(supporting_evidence),
        detected_at=str(alert_row["detected_at"]),
        anomaly_trace=dict(anomaly_trace),
    )


def _sort_alerts(alert_view: pd.DataFrame) -> pd.DataFrame:
    return alert_view.sort_values(
        ["entity_id", "severity_rank", "alert_type", "detector_id"],
        ascending=[True, False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)


def _numeric_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise AlertGenerationError(f"Alert field must be numeric: {field}")
    return round(float(numeric_value), 4)
