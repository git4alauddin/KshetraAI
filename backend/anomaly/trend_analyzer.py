"""Deterministic trend helpers for Build 05 anomaly alerts.

This module derives compact trend metadata from current-vs-baseline anomaly
signals. It does not generate recommendations, priority scores, explanations,
API responses, frontend behavior, or ML predictions.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd


class TrendAnalysisError(ValueError):
    """Raised when trend metadata cannot be derived safely."""


@dataclass(frozen=True)
class TrendSummary:
    """Stable trend metadata for one detected anomaly signal."""

    current_signal: str
    baseline_signal: str
    current_value: float
    baseline_value: float
    deviation_value: float
    deviation_direction: str
    trend_direction: str

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic trend trace metadata."""

        return {
            "current_signal": self.current_signal,
            "baseline_signal": self.baseline_signal,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "deviation_value": self.deviation_value,
            "deviation_direction": self.deviation_direction,
            "trend_direction": self.trend_direction,
        }


def summarize_deviation_trend(deviation_row: Mapping[str, Any]) -> TrendSummary:
    """Summarize current-vs-baseline movement for a severity-classified deviation."""

    required_fields = (
        "current_signal",
        "baseline_signal",
        "current_value",
        "baseline_value",
        "deviation_value",
        "deviation_direction",
    )
    missing_fields = [field for field in required_fields if field not in deviation_row]
    if missing_fields:
        raise TrendAnalysisError(
            "Deviation row is missing trend fields: "
            + ", ".join(missing_fields)
        )

    current_value = _numeric_value(deviation_row["current_value"], "current_value")
    baseline_value = _numeric_value(deviation_row["baseline_value"], "baseline_value")
    deviation_value = _numeric_value(deviation_row["deviation_value"], "deviation_value")
    deviation_direction = str(deviation_row["deviation_direction"])
    if deviation_direction not in ("increase", "decrease"):
        raise TrendAnalysisError(f"Unsupported deviation_direction: {deviation_direction}")

    return TrendSummary(
        current_signal=str(deviation_row["current_signal"]),
        baseline_signal=str(deviation_row["baseline_signal"]),
        current_value=current_value,
        baseline_value=baseline_value,
        deviation_value=deviation_value,
        deviation_direction=deviation_direction,
        trend_direction=_trend_direction(deviation_direction),
    )


def build_supporting_evidence(deviation_row: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Return non-empty structured evidence items for a triggered alert."""

    evidence_signals = deviation_row.get("evidence_signals")
    if not isinstance(evidence_signals, Mapping) or not evidence_signals:
        raise TrendAnalysisError("Triggered anomaly alerts require supporting evidence.")

    evidence_items = [
        {
            "signal": str(signal),
            "value": _to_builtin_value(value),
        }
        for signal, value in sorted(evidence_signals.items())
    ]
    return tuple(evidence_items)


def _trend_direction(deviation_direction: str) -> str:
    if deviation_direction == "increase":
        return "above_baseline"
    return "below_baseline"


def _numeric_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise TrendAnalysisError(f"Trend field must be numeric: {field}")
    return round(float(numeric_value), 4)


def _to_builtin_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
