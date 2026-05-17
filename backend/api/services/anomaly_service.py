"""Anomaly alert API service helpers for Build 08.

This service reads existing anomaly alert outputs and formats API responses. It
does not detect anomalies, calculate severity, or generate alert evidence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.api.schemas.anomaly_schema import AlertResponse, AlertsResponse


DEFAULT_ANOMALY_ALERTS_PATH = Path("datasets/processed/anomaly_alerts.csv")


class AnomalyServiceError(ValueError):
    """Raised when anomaly alert output cannot be exposed safely."""


def get_alerts_response(
    *,
    territory_id: str | None = None,
    severity: str | None = None,
    anomaly_alerts: pd.DataFrame | None = None,
    data_path: Path | str = DEFAULT_ANOMALY_ALERTS_PATH,
) -> AlertsResponse:
    """Return stable alert response from existing anomaly outputs."""

    source_view = anomaly_alerts if anomaly_alerts is not None else _load_view(data_path)
    if source_view.empty:
        return AlertsResponse(alerts=[])

    _require_columns(
        source_view,
        (
            "alert_id",
            "entity_id",
            "alert_type",
            "severity_score",
            "severity_level",
            "confidence_level",
        ),
    )
    filtered_view = _apply_filters(source_view, territory_id=territory_id, severity=severity)
    alerts = [_alert_response(row) for row in filtered_view.to_dict(orient="records")]
    return AlertsResponse(alerts=alerts)


def _load_view(data_path: Path | str) -> pd.DataFrame:
    resolved_path = Path(data_path)
    if not resolved_path.exists():
        return pd.DataFrame()
    return pd.read_csv(resolved_path)


def _apply_filters(
    anomaly_alerts: pd.DataFrame,
    *,
    territory_id: str | None,
    severity: str | None,
) -> pd.DataFrame:
    output = anomaly_alerts.copy()
    if territory_id is not None and "territory_id" in output.columns:
        output = output[output["territory_id"].astype(str) == str(territory_id)]
    if severity is not None:
        output = output[output["severity_level"].astype(str) == str(severity)]

    sort_columns = [
        column
        for column in ("severity_rank", "entity_id", "alert_type", "alert_id")
        if column in output.columns
    ]
    if "severity_rank" in sort_columns:
        return output.sort_values(
            sort_columns,
            ascending=[False] + [True] * (len(sort_columns) - 1),
            kind="mergesort",
        ).reset_index(drop=True)
    return output.sort_values(sort_columns, kind="mergesort").reset_index(drop=True)


def _alert_response(row: dict[str, Any]) -> AlertResponse:
    return AlertResponse(
        alert_id=_text_value(row["alert_id"], "alert_id"),
        entity_id=_text_value(row["entity_id"], "entity_id"),
        alert_type=_text_value(row["alert_type"], "alert_type"),
        severity_score=_float_value(row["severity_score"], "severity_score"),
        severity_level=_text_value(row["severity_level"], "severity_level"),
        confidence_level=_text_value(row["confidence_level"], "confidence_level"),
    )


def _require_columns(dataframe: pd.DataFrame, required_columns: tuple[str, ...]) -> None:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise AnomalyServiceError(
            "Anomaly alerts are missing columns: "
            + ", ".join(missing_columns)
        )


def _text_value(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise AnomalyServiceError(f"{field} cannot be empty.")
    return text


def _float_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise AnomalyServiceError(f"{field} must be numeric.")
    return float(numeric_value)
