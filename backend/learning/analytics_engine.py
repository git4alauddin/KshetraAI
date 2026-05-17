"""Outcome analytics summaries for Build 07.

This module creates deterministic summary views from recommendation tracking
and feedback signals. It does not generate recalibration signals, mutate
weights, generate recommendations, detect anomalies, create explanations, call
APIs, or render frontend content.
"""

from __future__ import annotations

import pandas as pd


RECOMMENDATION_EFFECTIVENESS_COLUMNS = [
    "matched_rule_id",
    "tracked_recommendations",
    "outcomes_logged",
    "recommendations_followed",
    "commercial_successes",
    "total_order_value",
    "effectiveness_trace",
]

ALERT_VALIDATION_COLUMNS = [
    "alert_validation_status",
    "alert_count",
    "alert_validation_trace",
]

REP_FEEDBACK_COLUMNS = [
    "feedback_category",
    "feedback_count",
    "learning_ready_count",
    "feedback_summary_trace",
]


class AnalyticsCalculationError(ValueError):
    """Raised when analytics summaries cannot be calculated safely."""


def build_recommendation_effectiveness_summary(
    tracking_view: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize tracked recommendation effectiveness by matched rule."""

    if tracking_view.empty:
        return pd.DataFrame(columns=RECOMMENDATION_EFFECTIVENESS_COLUMNS)
    _require_columns(
        tracking_view,
        (
            "matched_rule_id",
            "tracking_status",
            "recommendation_followed",
            "commercial_success",
            "order_value",
        ),
    )

    rows = []
    for matched_rule_id, group in tracking_view.groupby("matched_rule_id", sort=True):
        tracked_count = len(group)
        outcomes_logged = int((group["tracking_status"] == "outcome_logged").sum())
        followed_count = int(group["recommendation_followed"].map(lambda value: value is True).sum())
        commercial_successes = int(group["commercial_success"].map(lambda value: value is True).sum())
        total_order_value = _numeric_sum(group["order_value"])
        rows.append(
            {
                "matched_rule_id": matched_rule_id,
                "tracked_recommendations": tracked_count,
                "outcomes_logged": outcomes_logged,
                "recommendations_followed": followed_count,
                "commercial_successes": commercial_successes,
                "total_order_value": total_order_value,
                "effectiveness_trace": {
                    "matched_rule_id": matched_rule_id,
                    "tracked_recommendations": tracked_count,
                    "outcomes_logged": outcomes_logged,
                    "recommendations_followed": followed_count,
                    "commercial_successes": commercial_successes,
                },
            }
        )

    return pd.DataFrame(rows, columns=RECOMMENDATION_EFFECTIVENESS_COLUMNS).sort_values(
        "matched_rule_id",
        kind="mergesort",
    ).reset_index(drop=True)


def build_alert_validation_summary(
    tracking_view: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize alert validation outcomes from tracking rows."""

    if tracking_view.empty:
        return pd.DataFrame(columns=ALERT_VALIDATION_COLUMNS)
    _require_columns(tracking_view, ("alert_validated",))

    rows = []
    for status, group in tracking_view.groupby(
        tracking_view["alert_validated"].map(lambda value: str(value)),
        sort=True,
    ):
        count = len(group)
        rows.append(
            {
                "alert_validation_status": status,
                "alert_count": count,
                "alert_validation_trace": {
                    "alert_validation_status": status,
                    "alert_count": count,
                },
            }
        )

    return pd.DataFrame(rows, columns=ALERT_VALIDATION_COLUMNS).reset_index(drop=True)


def build_rep_feedback_summary(
    feedback_signal_view: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize representative feedback categories."""

    if feedback_signal_view.empty:
        return pd.DataFrame(columns=REP_FEEDBACK_COLUMNS)
    _require_columns(feedback_signal_view, ("feedback_category", "learning_ready"))

    rows = []
    for feedback_category, group in feedback_signal_view.groupby("feedback_category", sort=True):
        feedback_count = len(group)
        learning_ready_count = int(group["learning_ready"].map(lambda value: value is True).sum())
        rows.append(
            {
                "feedback_category": feedback_category,
                "feedback_count": feedback_count,
                "learning_ready_count": learning_ready_count,
                "feedback_summary_trace": {
                    "feedback_category": feedback_category,
                    "feedback_count": feedback_count,
                    "learning_ready_count": learning_ready_count,
                },
            }
        )

    return pd.DataFrame(rows, columns=REP_FEEDBACK_COLUMNS).reset_index(drop=True)


def _require_columns(dataframe: pd.DataFrame, required_columns: tuple[str, ...]) -> None:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise AnalyticsCalculationError(
            "Analytics input is missing columns: "
            + ", ".join(missing_columns)
        )


def _numeric_sum(values: pd.Series) -> float:
    numeric_values = pd.to_numeric(values, errors="coerce")
    if numeric_values.isna().any():
        raise AnalyticsCalculationError("order_value must be numeric for analytics.")
    return round(float(numeric_values.sum()), 2)
