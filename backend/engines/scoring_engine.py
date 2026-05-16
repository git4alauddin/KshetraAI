"""Weighted priority scoring for Build 03.

This module combines component scores into a final priority score. It does not
classify priority levels, rank entities, generate recommendations, detect
anomalies, or create human-readable explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from backend.engines.component_scorers import (
    ComponentScore,
    component_scores_as_dict,
    load_priority_weight_config,
)


class PriorityScoringError(ValueError):
    """Raised when final priority scoring input is invalid."""


@dataclass(frozen=True)
class PriorityScore:
    """Traceable final priority score before classification and ranking."""

    priority_score: float
    core_urgency_score: float
    travel_penalty: float
    component_scores: dict[str, float]
    applied_weights: dict[str, float]
    component_breakdown: dict[str, dict[str, Any]]

    def to_trace(self) -> dict[str, Any]:
        """Return a stable scoring trace for downstream modules."""

        return {
            "priority_score": self.priority_score,
            "core_urgency_score": self.core_urgency_score,
            "travel_penalty": self.travel_penalty,
            "component_scores": self.component_scores,
            "applied_weights": self.applied_weights,
            "component_breakdown": self.component_breakdown,
        }


def calculate_priority_score(
    component_scores: Mapping[str, ComponentScore],
    config: Mapping[str, Any] | None = None,
) -> PriorityScore:
    """Combine component scores into one final bounded priority score."""

    weight_config = config or load_priority_weight_config()
    weights = {
        component_name: float(weight)
        for component_name, weight in weight_config["component_weights"].items()
    }
    score_range = weight_config["score_range"]
    min_score = float(score_range["min"])
    max_score = float(score_range["max"])

    flat_component_scores = component_scores_as_dict(component_scores)
    _validate_component_inputs(flat_component_scores, weights)

    core_components = tuple(weight_config["component_policy"]["core_urgency_components"])
    penalty_components = tuple(weight_config["component_policy"]["penalty_components"])

    core_urgency_score = sum(
        flat_component_scores[component_name] * weights[component_name]
        for component_name in core_components
    )
    travel_penalty = sum(
        flat_component_scores[component_name] * abs(weights[component_name])
        for component_name in penalty_components
    )
    priority_score = core_urgency_score - travel_penalty

    if weight_config["component_policy"].get("clamp_final_score_to_range", True):
        priority_score = _clamp_score(priority_score, min_score=min_score, max_score=max_score)

    return PriorityScore(
        priority_score=round(priority_score, 4),
        core_urgency_score=round(core_urgency_score, 4),
        travel_penalty=round(travel_penalty, 4),
        component_scores=flat_component_scores,
        applied_weights=weights,
        component_breakdown={
            component_name: score.to_trace()
            for component_name, score in component_scores.items()
        },
    )


def priority_score_as_row(priority_score: PriorityScore) -> dict[str, Any]:
    """Flatten a priority score into stable output columns."""

    return {
        "priority_score": priority_score.priority_score,
        "core_urgency_score": priority_score.core_urgency_score,
        "travel_penalty": priority_score.travel_penalty,
        "component_scores": priority_score.component_scores,
        "component_breakdown": priority_score.component_breakdown,
        "priority_trace": priority_score.to_trace(),
    }


def _validate_component_inputs(
    component_scores: Mapping[str, float],
    component_weights: Mapping[str, float],
) -> None:
    missing_scores = [
        component_name
        for component_name in component_weights
        if component_name not in component_scores
    ]
    if missing_scores:
        raise PriorityScoringError(
            "Missing component scores for final priority scoring: "
            + ", ".join(missing_scores)
        )

    invalid_scores = [
        component_name
        for component_name, score in component_scores.items()
        if score < 0 or score > 100
    ]
    if invalid_scores:
        raise PriorityScoringError(
            "Component scores must be within 0-100: "
            + ", ".join(invalid_scores)
        )


def _clamp_score(score: float, *, min_score: float, max_score: float) -> float:
    return max(min_score, min(max_score, score))
