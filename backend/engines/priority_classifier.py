"""Priority score classification for Build 03.

This module assigns configured priority levels to final priority scores. It
does not rank entities, generate recommendations, detect anomalies, or produce
human-readable explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_DECISION_THRESHOLDS_PATH = Path("backend/config/decision_thresholds.yaml")


class PriorityClassificationError(ValueError):
    """Raised when priority classification input violates the contract."""


@dataclass(frozen=True)
class PriorityClassification:
    """Traceable priority level assignment for one score."""

    priority_level: str
    priority_level_key: str
    priority_severity_rank: int
    score: float
    matched_min_score: float

    def to_trace(self) -> dict[str, Any]:
        """Return a stable classification trace for downstream modules."""

        return {
            "priority_level": self.priority_level,
            "priority_level_key": self.priority_level_key,
            "priority_severity_rank": self.priority_severity_rank,
            "score": self.score,
            "matched_min_score": self.matched_min_score,
        }


def load_decision_threshold_config(
    config_path: Path | str = DEFAULT_DECISION_THRESHOLDS_PATH,
) -> dict[str, Any]:
    """Load priority classification thresholds from YAML."""

    resolved_path = Path(config_path)
    with resolved_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    _validate_decision_threshold_config(config)
    return config


def classify_priority_score(
    priority_score: Any,
    config: Mapping[str, Any] | None = None,
) -> PriorityClassification:
    """Assign a configured priority level to one final priority score."""

    threshold_config = config or load_decision_threshold_config()
    score = _coerce_priority_score(priority_score, threshold_config)

    for level_key, level_config in _ordered_levels(threshold_config):
        min_score = float(level_config["min_score"])
        if score >= min_score:
            return PriorityClassification(
                priority_level=str(level_config["label"]),
                priority_level_key=level_key,
                priority_severity_rank=int(level_config["severity_rank"]),
                score=score,
                matched_min_score=min_score,
            )

    raise PriorityClassificationError(
        f"Priority score {score:g} did not match any configured priority level."
    )


def add_priority_classification(
    priority_scores: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Add priority level columns to a priority score view."""

    if "priority_score" not in priority_scores.columns:
        raise PriorityClassificationError(
            "Priority score view is missing required column: priority_score"
        )

    threshold_config = config or load_decision_threshold_config()
    output = priority_scores.copy()
    classifications = [
        classify_priority_score(score, threshold_config)
        for score in output["priority_score"].tolist()
    ]

    output["priority_level"] = [
        classification.priority_level
        for classification in classifications
    ]
    output["priority_level_key"] = [
        classification.priority_level_key
        for classification in classifications
    ]
    output["priority_severity_rank"] = [
        classification.priority_severity_rank
        for classification in classifications
    ]
    output["classification_trace"] = [
        classification.to_trace()
        for classification in classifications
    ]
    return output


def _validate_decision_threshold_config(config: Mapping[str, Any]) -> None:
    required_sections = ("score_range", "priority_levels", "classification_policy")
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise PriorityClassificationError(
            "Decision threshold config is missing required sections: "
            + ", ".join(missing_sections)
        )

    score_range = config["score_range"]
    min_score = float(score_range["min"])
    max_score = float(score_range["max"])
    if min_score >= max_score:
        raise PriorityClassificationError("Priority score range min must be lower than max.")

    priority_levels = config["priority_levels"]
    if not priority_levels:
        raise PriorityClassificationError("At least one priority level is required.")

    seen_labels: set[str] = set()
    seen_ranks: set[int] = set()
    for level_key, level_config in priority_levels.items():
        for field in ("label", "severity_rank", "min_score", "max_score"):
            if field not in level_config:
                raise PriorityClassificationError(
                    f"Priority level '{level_key}' is missing required field: {field}"
                )

        label = str(level_config["label"])
        severity_rank = int(level_config["severity_rank"])
        level_min = float(level_config["min_score"])
        level_max = float(level_config["max_score"])
        if label in seen_labels:
            raise PriorityClassificationError(f"Duplicate priority label: {label}")
        if severity_rank in seen_ranks:
            raise PriorityClassificationError(f"Duplicate priority severity rank: {severity_rank}")
        if level_min < min_score or level_max > max_score or level_min > level_max:
            raise PriorityClassificationError(
                f"Priority level '{level_key}' is outside the configured score range."
            )
        seen_labels.add(label)
        seen_ranks.add(severity_rank)


def _ordered_levels(
    config: Mapping[str, Any],
) -> tuple[tuple[str, Mapping[str, Any]], ...]:
    return tuple(
        sorted(
            config["priority_levels"].items(),
            key=lambda item: float(item[1]["min_score"]),
            reverse=True,
        )
    )


def _coerce_priority_score(
    priority_score: Any,
    config: Mapping[str, Any],
) -> float:
    value = pd.to_numeric(pd.Series([priority_score]), errors="coerce").iloc[0]
    if pd.isna(value):
        raise PriorityClassificationError("Priority score must be numeric.")

    value = float(value)
    min_score = float(config["score_range"]["min"])
    max_score = float(config["score_range"]["max"])
    if value < min_score or value > max_score:
        raise PriorityClassificationError(
            f"Priority score must be within {min_score:g}-{max_score:g}; found {value:g}."
        )
    return value
