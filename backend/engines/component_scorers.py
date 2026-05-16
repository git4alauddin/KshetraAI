"""Component scoring utilities for the Build 03 priority engine.

This module converts normalized feature scores into component scores only. It
does not calculate final priority, classify urgency, rank entities, generate
recommendations, or produce human-readable explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_PRIORITY_WEIGHTS_PATH = Path("backend/config/priority_weights.yaml")
ENTITY_CONTEXT_COLUMNS = ("entity_id", "territory_id", "entity_type", "primary_crop")


class ComponentScoringError(ValueError):
    """Raised when component scoring input violates the priority contract."""


@dataclass(frozen=True)
class ComponentScore:
    """Traceable score for one priority component."""

    component_name: str
    score: float
    signal_breakdown: dict[str, float]
    applied_weights: dict[str, float]

    def to_trace(self) -> dict[str, Any]:
        """Return a stable trace payload for downstream explainability."""

        return {
            "component_name": self.component_name,
            "score": self.score,
            "signal_breakdown": self.signal_breakdown,
            "applied_weights": self.applied_weights,
        }


def load_priority_weight_config(
    config_path: Path | str = DEFAULT_PRIORITY_WEIGHTS_PATH,
) -> dict[str, Any]:
    """Load priority component and signal weights from YAML."""

    resolved_path = Path(config_path)
    with resolved_path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    _validate_priority_weight_config(config)
    return config


def score_component(
    feature_row: Mapping[str, Any],
    component_name: str,
    config: Mapping[str, Any] | None = None,
) -> ComponentScore:
    """Calculate one bounded component score from normalized feature signals."""

    weight_config = config or load_priority_weight_config()
    signal_weights = weight_config["signal_weights"]
    if component_name not in signal_weights:
        raise ComponentScoringError(f"Unknown priority component: {component_name}")

    min_score = float(weight_config["score_range"]["min"])
    max_score = float(weight_config["score_range"]["max"])
    component_signal_weights = signal_weights[component_name]
    signal_breakdown: dict[str, float] = {}

    for signal_name in component_signal_weights:
        signal_breakdown[signal_name] = _coerce_signal_score(
            feature_row,
            signal_name,
            min_score=min_score,
            max_score=max_score,
            component_name=component_name,
        )

    score = sum(
        signal_breakdown[signal_name] * float(weight)
        for signal_name, weight in component_signal_weights.items()
    )
    score = _clamp_score(score, min_score=min_score, max_score=max_score)

    return ComponentScore(
        component_name=component_name,
        score=round(score, 4),
        signal_breakdown=signal_breakdown,
        applied_weights={name: float(weight) for name, weight in component_signal_weights.items()},
    )


def score_all_components(
    feature_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> dict[str, ComponentScore]:
    """Calculate all configured component scores for one feature row."""

    weight_config = config or load_priority_weight_config()
    return {
        component_name: score_component(feature_row, component_name, weight_config)
        for component_name in weight_config["signal_weights"]
    }


def component_scores_as_dict(
    component_scores: Mapping[str, ComponentScore],
) -> dict[str, float]:
    """Return a flat component-to-score mapping for scoring and ranking modules."""

    return {
        component_name: component_score.score
        for component_name, component_score in component_scores.items()
    }


def build_component_score_view(
    feature_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build a stable entity-level view with component scores and trace payloads."""

    weight_config = config or load_priority_weight_config()
    rows: list[dict[str, Any]] = []

    for row in feature_view.to_dict(orient="records"):
        component_scores = score_all_components(row, weight_config)
        output_row = {
            column: row.get(column, "")
            for column in ENTITY_CONTEXT_COLUMNS
            if column in feature_view.columns
        }
        output_row.update(component_scores_as_dict(component_scores))
        output_row["component_breakdown"] = {
            name: score.to_trace()
            for name, score in component_scores.items()
        }
        rows.append(output_row)

    output = pd.DataFrame(rows)
    if output.empty:
        return output

    if "entity_id" in output.columns:
        output = output.sort_values("entity_id", kind="mergesort")
    return output.reset_index(drop=True)


def _validate_priority_weight_config(config: Mapping[str, Any]) -> None:
    required_sections = ("score_range", "component_weights", "signal_weights")
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise ComponentScoringError(
            "Priority weight config is missing required sections: "
            + ", ".join(missing_sections)
        )

    min_score = float(config["score_range"]["min"])
    max_score = float(config["score_range"]["max"])
    if min_score >= max_score:
        raise ComponentScoringError("Priority score range min must be lower than max.")

    for component_name, signal_weights in config["signal_weights"].items():
        if component_name not in config["component_weights"]:
            raise ComponentScoringError(
                f"Signal weights exist for component without component weight: {component_name}"
            )
        if not signal_weights:
            raise ComponentScoringError(f"Component has no signal weights: {component_name}")
        weight_total = sum(float(weight) for weight in signal_weights.values())
        if round(weight_total, 6) != 1:
            raise ComponentScoringError(
                f"Signal weights for {component_name} must sum to 1.0; found {weight_total}"
            )


def _coerce_signal_score(
    feature_row: Mapping[str, Any],
    signal_name: str,
    *,
    min_score: float,
    max_score: float,
    component_name: str,
) -> float:
    if signal_name not in feature_row:
        raise ComponentScoringError(
            f"Missing required signal '{signal_name}' for component '{component_name}'."
        )

    value = pd.to_numeric(pd.Series([feature_row[signal_name]]), errors="coerce").iloc[0]
    if pd.isna(value):
        raise ComponentScoringError(
            f"Signal '{signal_name}' for component '{component_name}' must be numeric."
        )

    value = float(value)
    if value < min_score or value > max_score:
        raise ComponentScoringError(
            f"Signal '{signal_name}' for component '{component_name}' must be within "
            f"{min_score:g}-{max_score:g}; found {value:g}."
        )
    return value


def _clamp_score(score: float, *, min_score: float, max_score: float) -> float:
    return max(min_score, min(max_score, score))
