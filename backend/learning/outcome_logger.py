"""Outcome logging for Build 07.

This module normalizes submitted field outcomes into a canonical outcome log.
It does not calculate metrics, generate recalibration signals, mutate weights,
generate recommendations, detect anomalies, create explanations, call APIs, or
render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_OUTCOME_METRICS_PATH = Path("backend/config/outcome_metrics.yaml")


class OutcomeLoggingError(ValueError):
    """Raised when outcome logging input violates the Build 07 contract."""


@dataclass(frozen=True)
class OutcomeRecord:
    """Canonical field outcome record."""

    outcome_id: str
    recommendation_id: str
    alert_id: str
    entity_id: str
    rep_id: str
    visit_completed: bool
    recommendation_followed: bool
    sale_made: bool
    order_placed: bool
    order_value: float
    alert_validated: bool | str
    feedback_category: str
    rep_feedback: str
    submitted_at: str

    def to_row(self) -> dict[str, Any]:
        """Return stable canonical outcome row."""

        return {
            "outcome_id": self.outcome_id,
            "recommendation_id": self.recommendation_id,
            "alert_id": self.alert_id,
            "entity_id": self.entity_id,
            "rep_id": self.rep_id,
            "visit_completed": self.visit_completed,
            "recommendation_followed": self.recommendation_followed,
            "sale_made": self.sale_made,
            "order_placed": self.order_placed,
            "order_value": self.order_value,
            "alert_validated": self.alert_validated,
            "feedback_category": self.feedback_category,
            "rep_feedback": self.rep_feedback,
            "submitted_at": self.submitted_at,
            "outcome_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic audit metadata for the outcome record."""

        return {
            "outcome_id": self.outcome_id,
            "recommendation_id": self.recommendation_id,
            "alert_id": self.alert_id,
            "entity_id": self.entity_id,
            "rep_id": self.rep_id,
            "commercial_success": self.sale_made and self.order_placed and self.order_value > 0,
            "recommendation_acceptance": self.recommendation_followed,
            "visit_executed": self.visit_completed,
            "alert_validation_status": self.alert_validated,
            "feedback_category": self.feedback_category,
        }


def load_outcome_metric_config(
    config_path: Path | str = DEFAULT_OUTCOME_METRICS_PATH,
) -> dict[str, Any]:
    """Load and validate outcome metric configuration."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    _validate_outcome_config(config)
    return config


def log_outcome(
    outcome_submission: Mapping[str, Any],
    *,
    known_recommendation_ids: Sequence[str] | None = None,
    config: Mapping[str, Any] | None = None,
) -> OutcomeRecord:
    """Normalize one field outcome submission into a canonical record."""

    outcome_config = config or load_outcome_metric_config()
    _require_fields(
        outcome_submission,
        (
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
        ),
    )

    recommendation_id = _required_text(outcome_submission["recommendation_id"], "recommendation_id")
    _validate_known_recommendation(
        recommendation_id,
        known_recommendation_ids,
        outcome_config["outcome_policy"],
    )
    entity_id = _required_text(outcome_submission["entity_id"], "entity_id")
    rep_id = _required_text(outcome_submission["rep_id"], "rep_id")
    feedback_category = _feedback_category(outcome_submission["feedback_category"], outcome_config)
    alert_id = str(outcome_submission.get("alert_id", "") or "")
    submitted_at = str(
        outcome_submission.get(
            "submitted_at",
            outcome_config["outcome_policy"]["default_submitted_at"],
        )
    )

    return OutcomeRecord(
        outcome_id=str(
            outcome_submission.get("outcome_id")
            or _build_outcome_id(entity_id, recommendation_id)
        ),
        recommendation_id=recommendation_id,
        alert_id=alert_id,
        entity_id=entity_id,
        rep_id=rep_id,
        visit_completed=_bool_value(outcome_submission["visit_completed"], "visit_completed"),
        recommendation_followed=_bool_value(
            outcome_submission["recommendation_followed"],
            "recommendation_followed",
        ),
        sale_made=_bool_value(outcome_submission["sale_made"], "sale_made"),
        order_placed=_bool_value(outcome_submission["order_placed"], "order_placed"),
        order_value=_order_value(outcome_submission["order_value"]),
        alert_validated=_alert_validation_value(outcome_submission["alert_validated"]),
        feedback_category=feedback_category,
        rep_feedback=str(outcome_submission.get("rep_feedback", "") or ""),
        submitted_at=submitted_at,
    )


def build_outcome_log(
    outcome_submissions: pd.DataFrame,
    *,
    known_recommendation_ids: Sequence[str] | None = None,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build a stable canonical outcome log from submitted field outcomes."""

    outcome_config = config or load_outcome_metric_config()
    schema = outcome_config["outcome_log_schema"]
    if outcome_submissions.empty:
        return pd.DataFrame(columns=schema)

    rows = [
        log_outcome(
            submission,
            known_recommendation_ids=known_recommendation_ids,
            config=outcome_config,
        ).to_row()
        for submission in outcome_submissions.to_dict(orient="records")
    ]
    output = pd.DataFrame(rows, columns=schema)
    return output.sort_values(
        outcome_config["outcome_policy"]["deterministic_sort_keys"],
        kind="mergesort",
    ).reset_index(drop=True)


def _validate_outcome_config(config: Mapping[str, Any]) -> None:
    required_sections = (
        "outcome_policy",
        "valid_feedback_categories",
        "valid_outcome_statuses",
        "outcome_log_schema",
        "performance_metric_schema",
        "metric_definitions",
    )
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise OutcomeLoggingError(
            "Outcome metric config is missing required sections: "
            + ", ".join(missing_sections)
        )
    if not config["valid_feedback_categories"]:
        raise OutcomeLoggingError("valid_feedback_categories cannot be empty.")
    for field, field_config in config["valid_outcome_statuses"].items():
        if not field_config.get("allowed_values"):
            raise OutcomeLoggingError(f"{field}: allowed_values cannot be empty.")


def _require_fields(
    outcome_submission: Mapping[str, Any],
    required_fields: Sequence[str],
) -> None:
    missing_fields = [field for field in required_fields if field not in outcome_submission]
    if missing_fields:
        raise OutcomeLoggingError(
            "Outcome submission is missing required fields: "
            + ", ".join(missing_fields)
        )


def _validate_known_recommendation(
    recommendation_id: str,
    known_recommendation_ids: Sequence[str] | None,
    policy: Mapping[str, Any],
) -> None:
    if not policy["require_known_recommendation_id"] or known_recommendation_ids is None:
        return
    if recommendation_id not in set(str(value) for value in known_recommendation_ids):
        raise OutcomeLoggingError(f"Unknown recommendation_id: {recommendation_id}")


def _required_text(value: Any, field: str) -> str:
    text_value = str(value or "").strip()
    if not text_value:
        raise OutcomeLoggingError(f"Outcome submission requires {field}.")
    return text_value


def _feedback_category(value: Any, config: Mapping[str, Any]) -> str:
    category = str(value or "").strip()
    if category not in set(config["valid_feedback_categories"]):
        raise OutcomeLoggingError(f"Unsupported feedback_category: {category}")
    return category


def _bool_value(value: Any, field: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized_value = value.strip().lower()
        if normalized_value == "true":
            return True
        if normalized_value == "false":
            return False
    raise OutcomeLoggingError(f"Outcome field must be boolean: {field}")


def _alert_validation_value(value: Any) -> bool | str:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized_value = value.strip().lower()
        if normalized_value == "true":
            return True
        if normalized_value == "false":
            return False
        if normalized_value == "unknown":
            return "unknown"
    raise OutcomeLoggingError("Outcome field must be true, false, or unknown: alert_validated")


def _order_value(value: Any) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise OutcomeLoggingError("order_value must be numeric.")
    numeric_value = float(numeric_value)
    if numeric_value < 0:
        raise OutcomeLoggingError("order_value must be non-negative.")
    return round(numeric_value, 2)


def _build_outcome_id(entity_id: str, recommendation_id: str) -> str:
    return f"OUTCOME_{_normalize_id(entity_id)}_{_normalize_id(recommendation_id)}"


def _normalize_id(value: str) -> str:
    return "".join(
        character if character.isalnum() else "_"
        for character in value.upper()
    ).strip("_")
