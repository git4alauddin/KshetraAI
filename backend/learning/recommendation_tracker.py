"""Recommendation outcome tracking for Build 07.

This module links recommendation outputs to logged field outcomes and derives
row-level tracking signals. It does not calculate aggregate metrics, generate
recalibration signals, mutate weights, generate recommendations, detect
anomalies, create explanations, call APIs, or render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd


RECOMMENDATION_TRACKING_COLUMNS = [
    "recommendation_id",
    "entity_id",
    "matched_rule_id",
    "recommended_actions",
    "recommended_product_category",
    "recommendation_confidence_level",
    "outcome_id",
    "rep_id",
    "visit_completed",
    "recommendation_followed",
    "sale_made",
    "order_placed",
    "order_value",
    "commercial_success",
    "alert_id",
    "alert_validated",
    "feedback_category",
    "submitted_at",
    "tracking_status",
    "tracking_trace",
]


class RecommendationTrackingError(ValueError):
    """Raised when recommendation tracking inputs are invalid."""


@dataclass(frozen=True)
class RecommendationTrackingRecord:
    """Tracked recommendation with optional linked outcome."""

    recommendation_id: str
    entity_id: str
    matched_rule_id: str
    recommended_actions: list[str]
    recommended_product_category: str
    recommendation_confidence_level: str
    outcome_id: str
    rep_id: str
    visit_completed: bool | None
    recommendation_followed: bool | None
    sale_made: bool | None
    order_placed: bool | None
    order_value: float
    commercial_success: bool
    alert_id: str
    alert_validated: bool | str
    feedback_category: str
    submitted_at: str
    tracking_status: str

    def to_row(self) -> dict[str, Any]:
        """Return stable recommendation tracking row."""

        return {
            "recommendation_id": self.recommendation_id,
            "entity_id": self.entity_id,
            "matched_rule_id": self.matched_rule_id,
            "recommended_actions": self.recommended_actions,
            "recommended_product_category": self.recommended_product_category,
            "recommendation_confidence_level": self.recommendation_confidence_level,
            "outcome_id": self.outcome_id,
            "rep_id": self.rep_id,
            "visit_completed": self.visit_completed,
            "recommendation_followed": self.recommendation_followed,
            "sale_made": self.sale_made,
            "order_placed": self.order_placed,
            "order_value": self.order_value,
            "commercial_success": self.commercial_success,
            "alert_id": self.alert_id,
            "alert_validated": self.alert_validated,
            "feedback_category": self.feedback_category,
            "submitted_at": self.submitted_at,
            "tracking_status": self.tracking_status,
            "tracking_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic tracking trace metadata."""

        return {
            "recommendation_id": self.recommendation_id,
            "entity_id": self.entity_id,
            "matched_rule_id": self.matched_rule_id,
            "outcome_id": self.outcome_id,
            "tracking_status": self.tracking_status,
            "accepted": self.recommendation_followed is True,
            "visit_completed": self.visit_completed is True,
            "commercial_success": self.commercial_success,
            "alert_validated": self.alert_validated,
        }


def track_recommendation(
    recommendation_row: Mapping[str, Any],
    outcome_row: Mapping[str, Any] | None = None,
) -> RecommendationTrackingRecord:
    """Track one recommendation against an optional logged outcome."""

    _require_fields(
        recommendation_row,
        (
            "entity_id",
            "matched_rule_id",
            "recommended_actions",
            "recommended_product_category",
            "confidence_level",
        ),
        "recommendation",
    )
    recommendation_id = _recommendation_id(recommendation_row)
    entity_id = str(recommendation_row["entity_id"])

    if outcome_row is None:
        return RecommendationTrackingRecord(
            recommendation_id=recommendation_id,
            entity_id=entity_id,
            matched_rule_id=str(recommendation_row["matched_rule_id"]),
            recommended_actions=_actions(recommendation_row["recommended_actions"]),
            recommended_product_category=str(recommendation_row["recommended_product_category"]),
            recommendation_confidence_level=str(recommendation_row["confidence_level"]),
            outcome_id="",
            rep_id="",
            visit_completed=None,
            recommendation_followed=None,
            sale_made=None,
            order_placed=None,
            order_value=0.0,
            commercial_success=False,
            alert_id="",
            alert_validated="unknown",
            feedback_category="no_feedback",
            submitted_at="",
            tracking_status="no_outcome_logged",
        )

    _require_fields(
        outcome_row,
        (
            "outcome_id",
            "recommendation_id",
            "entity_id",
            "rep_id",
            "visit_completed",
            "recommendation_followed",
            "sale_made",
            "order_placed",
            "order_value",
            "alert_validated",
            "feedback_category",
            "submitted_at",
        ),
        "outcome",
    )
    if str(outcome_row["recommendation_id"]) != recommendation_id:
        raise RecommendationTrackingError(
            "Outcome recommendation_id does not match recommendation row."
        )
    if str(outcome_row["entity_id"]) != entity_id:
        raise RecommendationTrackingError("Outcome entity_id does not match recommendation row.")

    sale_made = _bool_or_none(outcome_row["sale_made"], "sale_made")
    order_placed = _bool_or_none(outcome_row["order_placed"], "order_placed")
    order_value = _numeric_order_value(outcome_row["order_value"])

    return RecommendationTrackingRecord(
        recommendation_id=recommendation_id,
        entity_id=entity_id,
        matched_rule_id=str(recommendation_row["matched_rule_id"]),
        recommended_actions=_actions(recommendation_row["recommended_actions"]),
        recommended_product_category=str(recommendation_row["recommended_product_category"]),
        recommendation_confidence_level=str(recommendation_row["confidence_level"]),
        outcome_id=str(outcome_row["outcome_id"]),
        rep_id=str(outcome_row["rep_id"]),
        visit_completed=_bool_or_none(outcome_row["visit_completed"], "visit_completed"),
        recommendation_followed=_bool_or_none(
            outcome_row["recommendation_followed"],
            "recommendation_followed",
        ),
        sale_made=sale_made,
        order_placed=order_placed,
        order_value=order_value,
        commercial_success=bool(sale_made and order_placed and order_value > 0),
        alert_id=str(outcome_row.get("alert_id", "") or ""),
        alert_validated=_alert_validated(outcome_row["alert_validated"]),
        feedback_category=str(outcome_row["feedback_category"]),
        submitted_at=str(outcome_row["submitted_at"]),
        tracking_status="outcome_logged",
    )


def build_recommendation_tracking_view(
    recommendation_view: pd.DataFrame,
    outcome_log: pd.DataFrame,
) -> pd.DataFrame:
    """Build stable row-level recommendation tracking outputs."""

    if recommendation_view.empty:
        return pd.DataFrame(columns=RECOMMENDATION_TRACKING_COLUMNS)

    _validate_recommendation_view(recommendation_view)
    outcome_map = _outcome_map(outcome_log)
    records = []
    for recommendation_row in recommendation_view.to_dict(orient="records"):
        recommendation_id = _recommendation_id(recommendation_row)
        records.append(
            track_recommendation(
                recommendation_row,
                outcome_map.get(recommendation_id),
            ).to_row()
        )

    output = pd.DataFrame(records, columns=RECOMMENDATION_TRACKING_COLUMNS)
    return output.sort_values(
        ["entity_id", "recommendation_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _outcome_map(outcome_log: pd.DataFrame) -> dict[str, Mapping[str, Any]]:
    if outcome_log.empty:
        return {}
    if "recommendation_id" not in outcome_log.columns:
        raise RecommendationTrackingError("Outcome log is missing recommendation_id.")

    rows = {}
    for outcome_row in outcome_log.sort_values(
        ["recommendation_id", "outcome_id"],
        kind="mergesort",
    ).to_dict(orient="records"):
        recommendation_id = str(outcome_row["recommendation_id"])
        rows.setdefault(recommendation_id, outcome_row)
    return rows


def _validate_recommendation_view(recommendation_view: pd.DataFrame) -> None:
    required_columns = (
        "entity_id",
        "matched_rule_id",
        "recommended_actions",
        "recommended_product_category",
        "confidence_level",
    )
    missing_columns = [column for column in required_columns if column not in recommendation_view.columns]
    if missing_columns:
        raise RecommendationTrackingError(
            "Recommendation view is missing tracking columns: "
            + ", ".join(missing_columns)
        )


def _require_fields(
    row: Mapping[str, Any],
    required_fields: tuple[str, ...],
    row_type: str,
) -> None:
    missing_fields = [field for field in required_fields if field not in row]
    if missing_fields:
        raise RecommendationTrackingError(
            f"{row_type} row is missing tracking fields: "
            + ", ".join(missing_fields)
        )


def _recommendation_id(recommendation_row: Mapping[str, Any]) -> str:
    value = recommendation_row.get("recommendation_id") or recommendation_row.get("matched_rule_id")
    recommendation_id = str(value or "").strip()
    if not recommendation_id:
        raise RecommendationTrackingError("Recommendation row requires recommendation_id or matched_rule_id.")
    return recommendation_id


def _actions(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(action) for action in value]
    if isinstance(value, tuple):
        return [str(action) for action in value]
    raise RecommendationTrackingError("recommended_actions must be a list or tuple.")


def _bool_or_none(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    raise RecommendationTrackingError(f"Tracking field must be boolean: {field}")


def _alert_validated(value: Any) -> bool | str:
    if isinstance(value, bool):
        return value
    if str(value) == "unknown":
        return "unknown"
    raise RecommendationTrackingError("alert_validated must be true, false, or unknown.")


def _numeric_order_value(value: Any) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise RecommendationTrackingError("order_value must be numeric.")
    numeric_value = float(numeric_value)
    if numeric_value < 0:
        raise RecommendationTrackingError("order_value must be non-negative.")
    return round(numeric_value, 2)
