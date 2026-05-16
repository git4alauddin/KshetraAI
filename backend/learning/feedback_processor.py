"""Feedback processing for Build 07.

This module normalizes tracked recommendation outcomes into deterministic
learning input signals. It does not calculate aggregate metrics, generate
recalibration signals, mutate weights, generate recommendations, detect
anomalies, create explanations, call APIs, or render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd


FEEDBACK_SIGNAL_COLUMNS = [
    "feedback_signal_id",
    "recommendation_id",
    "entity_id",
    "outcome_id",
    "feedback_category",
    "explicit_feedback_signal",
    "implicit_acceptance_signal",
    "commercial_signal",
    "alert_validation_signal",
    "overall_feedback_signal",
    "learning_ready",
    "feedback_trace",
]

POSITIVE_FEEDBACK_CATEGORIES = {
    "useful",
    "order_followup_needed",
}
NEGATIVE_FEEDBACK_CATEGORIES = {
    "not_useful",
    "wrong_timing",
    "incorrect_risk",
    "customer_not_interested",
}


class FeedbackProcessingError(ValueError):
    """Raised when feedback processing input is invalid."""


@dataclass(frozen=True)
class FeedbackSignal:
    """Deterministic learning input signal from one tracked recommendation."""

    feedback_signal_id: str
    recommendation_id: str
    entity_id: str
    outcome_id: str
    feedback_category: str
    explicit_feedback_signal: str
    implicit_acceptance_signal: str
    commercial_signal: str
    alert_validation_signal: str
    overall_feedback_signal: str
    learning_ready: bool

    def to_row(self) -> dict[str, Any]:
        """Return stable feedback signal row."""

        return {
            "feedback_signal_id": self.feedback_signal_id,
            "recommendation_id": self.recommendation_id,
            "entity_id": self.entity_id,
            "outcome_id": self.outcome_id,
            "feedback_category": self.feedback_category,
            "explicit_feedback_signal": self.explicit_feedback_signal,
            "implicit_acceptance_signal": self.implicit_acceptance_signal,
            "commercial_signal": self.commercial_signal,
            "alert_validation_signal": self.alert_validation_signal,
            "overall_feedback_signal": self.overall_feedback_signal,
            "learning_ready": self.learning_ready,
            "feedback_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic feedback trace metadata."""

        return {
            "feedback_signal_id": self.feedback_signal_id,
            "recommendation_id": self.recommendation_id,
            "entity_id": self.entity_id,
            "outcome_id": self.outcome_id,
            "feedback_category": self.feedback_category,
            "signals": {
                "explicit": self.explicit_feedback_signal,
                "acceptance": self.implicit_acceptance_signal,
                "commercial": self.commercial_signal,
                "alert_validation": self.alert_validation_signal,
            },
            "overall_feedback_signal": self.overall_feedback_signal,
            "learning_ready": self.learning_ready,
        }


def process_feedback(
    tracking_row: Mapping[str, Any],
) -> FeedbackSignal:
    """Normalize one recommendation tracking row into a learning input signal."""

    _require_fields(
        tracking_row,
        (
            "recommendation_id",
            "entity_id",
            "outcome_id",
            "tracking_status",
            "feedback_category",
            "recommendation_followed",
            "commercial_success",
            "alert_validated",
        ),
    )

    recommendation_id = str(tracking_row["recommendation_id"])
    entity_id = str(tracking_row["entity_id"])
    outcome_id = str(tracking_row.get("outcome_id", "") or "")
    tracking_status = str(tracking_row["tracking_status"])
    feedback_category = str(tracking_row["feedback_category"])

    if tracking_status == "no_outcome_logged":
        return FeedbackSignal(
            feedback_signal_id=_build_signal_id(entity_id, recommendation_id),
            recommendation_id=recommendation_id,
            entity_id=entity_id,
            outcome_id=outcome_id,
            feedback_category=feedback_category,
            explicit_feedback_signal="pending",
            implicit_acceptance_signal="pending",
            commercial_signal="pending",
            alert_validation_signal="pending",
            overall_feedback_signal="pending",
            learning_ready=False,
        )

    explicit_signal = _explicit_feedback_signal(feedback_category)
    acceptance_signal = _boolean_signal(tracking_row["recommendation_followed"], "accepted", "rejected")
    commercial_signal = _boolean_signal(tracking_row["commercial_success"], "positive", "negative")
    alert_signal = _alert_validation_signal(tracking_row["alert_validated"])
    overall_signal = _overall_feedback_signal(
        explicit_signal,
        acceptance_signal,
        commercial_signal,
        alert_signal,
    )

    return FeedbackSignal(
        feedback_signal_id=_build_signal_id(entity_id, recommendation_id),
        recommendation_id=recommendation_id,
        entity_id=entity_id,
        outcome_id=outcome_id,
        feedback_category=feedback_category,
        explicit_feedback_signal=explicit_signal,
        implicit_acceptance_signal=acceptance_signal,
        commercial_signal=commercial_signal,
        alert_validation_signal=alert_signal,
        overall_feedback_signal=overall_signal,
        learning_ready=True,
    )


def build_feedback_signal_view(
    tracking_view: pd.DataFrame,
) -> pd.DataFrame:
    """Build stable feedback signals from recommendation tracking rows."""

    if tracking_view.empty:
        return pd.DataFrame(columns=FEEDBACK_SIGNAL_COLUMNS)

    rows = [
        process_feedback(row).to_row()
        for row in tracking_view.to_dict(orient="records")
    ]
    output = pd.DataFrame(rows, columns=FEEDBACK_SIGNAL_COLUMNS)
    return output.sort_values(
        ["entity_id", "recommendation_id", "feedback_signal_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _require_fields(
    tracking_row: Mapping[str, Any],
    required_fields: tuple[str, ...],
) -> None:
    missing_fields = [field for field in required_fields if field not in tracking_row]
    if missing_fields:
        raise FeedbackProcessingError(
            "Tracking row is missing feedback fields: "
            + ", ".join(missing_fields)
        )


def _explicit_feedback_signal(feedback_category: str) -> str:
    if feedback_category in POSITIVE_FEEDBACK_CATEGORIES:
        return "positive"
    if feedback_category in NEGATIVE_FEEDBACK_CATEGORIES:
        return "negative"
    if feedback_category == "no_feedback":
        return "neutral"
    raise FeedbackProcessingError(f"Unsupported feedback_category: {feedback_category}")


def _boolean_signal(value: Any, positive_label: str, negative_label: str) -> str:
    if isinstance(value, bool):
        return positive_label if value else negative_label
    raise FeedbackProcessingError("Expected boolean tracking signal.")


def _alert_validation_signal(value: Any) -> str:
    if isinstance(value, bool):
        return "validated" if value else "not_validated"
    if str(value) == "unknown":
        return "unknown"
    raise FeedbackProcessingError("alert_validated must be true, false, or unknown.")


def _overall_feedback_signal(
    explicit_signal: str,
    acceptance_signal: str,
    commercial_signal: str,
    alert_validation_signal: str,
) -> str:
    positive_count = sum(
        signal in {"positive", "accepted", "validated"}
        for signal in (explicit_signal, acceptance_signal, commercial_signal, alert_validation_signal)
    )
    negative_count = sum(
        signal in {"negative", "rejected", "not_validated"}
        for signal in (explicit_signal, acceptance_signal, commercial_signal, alert_validation_signal)
    )
    if positive_count > negative_count:
        return "positive"
    if negative_count > positive_count:
        return "negative"
    return "neutral"


def _build_signal_id(entity_id: str, recommendation_id: str) -> str:
    return f"FEEDBACK_{_normalize_id(entity_id)}_{_normalize_id(recommendation_id)}"


def _normalize_id(value: str) -> str:
    return "".join(
        character if character.isalnum() else "_"
        for character in value.upper()
    ).strip("_")
