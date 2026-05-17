"""Human-reviewable recalibration signal generation for Build 07.

This module evaluates configured outcome metrics against review-only
recalibration rules. It does not mutate priority weights, rewrite decision
rules, change anomaly thresholds, retrain models, generate recommendations,
detect anomalies, create explanations, call APIs, or render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_RECALIBRATION_RULES_PATH = Path("backend/config/recalibration_rules.yaml")


class RecalibrationSignalError(ValueError):
    """Raised when recalibration signals cannot be generated safely."""


@dataclass(frozen=True)
class RecalibrationSignal:
    """One human-reviewable recalibration suggestion."""

    signal_id: str
    signal_type: str
    source_metric: str
    affected_component: str
    trigger_condition: str
    suggestion_text: str
    requires_human_review: bool
    metric_value: float
    metric_denominator: float
    rule_id: str

    def to_row(self) -> dict[str, Any]:
        """Return stable recalibration signal row."""

        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "source_metric": self.source_metric,
            "affected_component": self.affected_component,
            "trigger_condition": self.trigger_condition,
            "suggestion_text": self.suggestion_text,
            "requires_human_review": self.requires_human_review,
            "signal_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic audit metadata for this signal."""

        return {
            "rule_id": self.rule_id,
            "source_metric": self.source_metric,
            "metric_value": self.metric_value,
            "metric_denominator": self.metric_denominator,
            "trigger_condition": self.trigger_condition,
            "requires_human_review": self.requires_human_review,
        }


def load_recalibration_config(
    config_path: Path | str = DEFAULT_RECALIBRATION_RULES_PATH,
) -> dict[str, Any]:
    """Load and validate recalibration signal configuration."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    _validate_recalibration_config(config)
    return config


def generate_recalibration_signals(
    performance_metrics: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Generate review-only recalibration signals from performance metrics."""

    recalibration_config = config or load_recalibration_config()
    _validate_recalibration_config(recalibration_config)
    signal_schema = recalibration_config["signal_schema"]
    if performance_metrics.empty:
        return pd.DataFrame(columns=signal_schema)

    _require_metric_columns(performance_metrics)
    metric_lookup = _build_metric_lookup(performance_metrics)
    signals = [
        signal
        for rule in recalibration_config["recalibration_rules"].values()
        for signal in [_evaluate_rule(rule, metric_lookup)]
        if signal is not None
    ]
    if not signals:
        return pd.DataFrame(columns=signal_schema)

    output = pd.DataFrame([signal.to_row() for signal in signals], columns=signal_schema)
    return output.sort_values(
        recalibration_config["recalibration_policy"]["deterministic_sort_keys"],
        kind="mergesort",
    ).reset_index(drop=True)


def _evaluate_rule(
    rule: Mapping[str, Any],
    metric_lookup: Mapping[str, Mapping[str, Any]],
) -> RecalibrationSignal | None:
    source_metric = str(rule["source_metric"])
    if source_metric not in metric_lookup:
        raise RecalibrationSignalError(f"Missing source_metric for recalibration: {source_metric}")

    metric = metric_lookup[source_metric]
    trigger = rule["trigger"]
    metric_value = _numeric_value(metric["metric_value"], f"{source_metric}.metric_value")
    denominator = _numeric_value(metric["denominator"], f"{source_metric}.denominator")
    minimum_denominator = _numeric_value(
        trigger["minimum_denominator"],
        f"{source_metric}.minimum_denominator",
    )
    if denominator < minimum_denominator:
        return None

    operator = str(trigger["operator"])
    threshold = _numeric_value(trigger["threshold"], f"{source_metric}.threshold")
    if not _triggered(metric_value, operator, threshold):
        return None

    if rule["requires_human_review"] is not True:
        raise RecalibrationSignalError(
            f"{rule['rule_id']} must require human review."
        )

    return RecalibrationSignal(
        signal_id=_build_signal_id(str(rule["rule_id"])),
        signal_type=str(rule["signal_type"]),
        source_metric=source_metric,
        affected_component=str(rule["affected_component"]),
        trigger_condition=_build_trigger_condition(operator, threshold, minimum_denominator),
        suggestion_text=str(rule["suggestion_text"]),
        requires_human_review=True,
        metric_value=round(metric_value, 4),
        metric_denominator=round(denominator, 4),
        rule_id=str(rule["rule_id"]),
    )


def _validate_recalibration_config(config: Mapping[str, Any]) -> None:
    required_sections = (
        "recalibration_policy",
        "signal_schema",
        "signal_types",
        "recalibration_rules",
        "safety_constraints",
    )
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise RecalibrationSignalError(
            "Recalibration config is missing sections: "
            + ", ".join(missing_sections)
        )

    policy = config["recalibration_policy"]
    if policy["mode"] != "human_review_only":
        raise RecalibrationSignalError("Recalibration mode must be human_review_only.")
    forbidden_policy_flags = (
        "automatic_weight_updates_allowed",
        "automatic_rule_updates_allowed",
        "automatic_threshold_updates_allowed",
    )
    for policy_flag in forbidden_policy_flags:
        if policy[policy_flag]:
            raise RecalibrationSignalError(f"{policy_flag} must be false.")

    signal_types = set(config["signal_types"])
    for rule_key, rule in config["recalibration_rules"].items():
        if rule["signal_type"] not in signal_types:
            raise RecalibrationSignalError(f"{rule_key} has unsupported signal_type.")
        if rule["requires_human_review"] is not True:
            raise RecalibrationSignalError(f"{rule_key} must require human review.")
        if rule["trigger"]["operator"] not in ("gte", "lte"):
            raise RecalibrationSignalError(f"{rule_key} has unsupported trigger operator.")


def _require_metric_columns(performance_metrics: pd.DataFrame) -> None:
    required_columns = ("metric_name", "metric_value", "denominator")
    missing_columns = [
        column for column in required_columns if column not in performance_metrics.columns
    ]
    if missing_columns:
        raise RecalibrationSignalError(
            "Performance metrics are missing columns: "
            + ", ".join(missing_columns)
        )


def _build_metric_lookup(performance_metrics: pd.DataFrame) -> dict[str, Mapping[str, Any]]:
    metric_lookup: dict[str, Mapping[str, Any]] = {}
    for row in performance_metrics.to_dict(orient="records"):
        metric_name = str(row["metric_name"])
        if metric_name in metric_lookup:
            raise RecalibrationSignalError(f"Duplicate metric_name: {metric_name}")
        metric_lookup[metric_name] = row
    return metric_lookup


def _numeric_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise RecalibrationSignalError(f"{field} must be numeric.")
    return float(numeric_value)


def _triggered(metric_value: float, operator: str, threshold: float) -> bool:
    if operator == "gte":
        return metric_value >= threshold
    if operator == "lte":
        return metric_value <= threshold
    raise RecalibrationSignalError(f"Unsupported trigger operator: {operator}")


def _build_signal_id(rule_id: str) -> str:
    return f"SIGNAL_{rule_id}"


def _build_trigger_condition(
    operator: str,
    threshold: float,
    minimum_denominator: float,
) -> str:
    return (
        f"metric_value {operator} {threshold:g}; "
        f"denominator >= {minimum_denominator:g}"
    )
