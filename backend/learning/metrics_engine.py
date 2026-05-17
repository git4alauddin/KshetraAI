"""Outcome metric calculation for Build 07.

This module calculates deterministic aggregate performance metrics from the
canonical outcome log. It does not generate recalibration signals, mutate
weights, generate recommendations, detect anomalies, create explanations, call
APIs, or render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.learning.outcome_logger import load_outcome_metric_config


class MetricsCalculationError(ValueError):
    """Raised when outcome metrics cannot be calculated safely."""


@dataclass(frozen=True)
class PerformanceMetric:
    """One deterministic performance metric row."""

    metric_id: str
    metric_name: str
    numerator: float
    denominator: float
    metric_value: float
    metric_unit: str

    def to_row(self) -> dict[str, Any]:
        """Return stable performance metric row."""

        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "metric_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic metric trace metadata."""

        return {
            "metric_id": self.metric_id,
            "metric_name": self.metric_name,
            "numerator": self.numerator,
            "denominator": self.denominator,
            "metric_unit": self.metric_unit,
        }


def calculate_performance_metrics(
    outcome_log: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Calculate all configured performance metrics from an outcome log."""

    outcome_config = config or load_outcome_metric_config()
    schema = outcome_config["performance_metric_schema"]
    if outcome_log.empty:
        return pd.DataFrame(columns=schema)

    _validate_outcome_log(outcome_log)
    metric_rows = [
        _calculate_metric(outcome_log, metric)
        for metric in outcome_config["metric_definitions"].values()
    ]
    output = pd.DataFrame(
        [metric.to_row() for metric in metric_rows],
        columns=schema,
    )
    return output.sort_values("metric_id", kind="mergesort").reset_index(drop=True)


def _calculate_metric(
    outcome_log: pd.DataFrame,
    metric: Mapping[str, Any],
) -> PerformanceMetric:
    metric_name = str(metric["metric_name"])
    denominator_scope = str(metric["denominator_scope"])
    denominator_mask = _denominator_mask(outcome_log, denominator_scope)
    denominator = float(denominator_mask.sum())

    if metric_name == "average_order_value":
        numerator = _sum_order_value(outcome_log, denominator_mask)
        metric_value = _safe_divide(numerator, denominator)
    elif metric_name == "feedback_positive_rate":
        numerator = _positive_feedback_count(outcome_log, denominator_mask, metric)
        metric_value = _safe_divide(numerator, denominator)
    elif metric_name == "alert_validation_rate":
        numerator = _true_count(outcome_log.loc[denominator_mask, metric["numerator_field"]])
        metric_value = _safe_divide(numerator, denominator)
    else:
        numerator = _true_count(outcome_log.loc[denominator_mask, metric["numerator_field"]])
        metric_value = _safe_divide(numerator, denominator)

    return PerformanceMetric(
        metric_id=str(metric["metric_id"]),
        metric_name=metric_name,
        numerator=round(float(numerator), 4),
        denominator=round(float(denominator), 4),
        metric_value=round(float(metric_value), 4),
        metric_unit=str(metric["metric_unit"]),
    )


def _validate_outcome_log(outcome_log: pd.DataFrame) -> None:
    required_columns = (
        "visit_completed",
        "recommendation_followed",
        "order_placed",
        "order_value",
        "alert_validated",
        "feedback_category",
    )
    missing_columns = [column for column in required_columns if column not in outcome_log.columns]
    if missing_columns:
        raise MetricsCalculationError(
            "Outcome log is missing metric columns: "
            + ", ".join(missing_columns)
        )


def _denominator_mask(
    outcome_log: pd.DataFrame,
    denominator_scope: str,
) -> pd.Series:
    if denominator_scope == "all_outcomes":
        return pd.Series([True] * len(outcome_log), index=outcome_log.index)
    if denominator_scope == "completed_visits":
        return outcome_log["visit_completed"].map(lambda value: value is True)
    if denominator_scope == "alert_outcomes":
        return outcome_log["alert_validated"].map(lambda value: value in (True, False))
    if denominator_scope == "placed_orders":
        return outcome_log["order_placed"].map(lambda value: value is True)
    if denominator_scope == "feedback_outcomes":
        return outcome_log["feedback_category"].map(lambda value: str(value) != "no_feedback")
    raise MetricsCalculationError(f"Unsupported denominator_scope: {denominator_scope}")


def _true_count(values: pd.Series) -> float:
    return float(values.map(lambda value: value is True).sum())


def _sum_order_value(outcome_log: pd.DataFrame, denominator_mask: pd.Series) -> float:
    order_values = pd.to_numeric(outcome_log.loc[denominator_mask, "order_value"], errors="coerce")
    if order_values.isna().any():
        raise MetricsCalculationError("order_value must be numeric for average_order_value.")
    return float(order_values.sum())


def _positive_feedback_count(
    outcome_log: pd.DataFrame,
    denominator_mask: pd.Series,
    metric: Mapping[str, Any],
) -> float:
    positive_categories = set(metric["positive_feedback_categories"])
    return float(
        outcome_log.loc[denominator_mask, "feedback_category"]
        .map(lambda value: str(value) in positive_categories)
        .sum()
    )


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
