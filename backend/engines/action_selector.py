"""Safe action selection helpers for Build 04.

This module normalizes structured recommendation actions into deterministic
action selections. It does not generate explanation text, priority scores,
anomaly alerts, API responses, frontend content, or free-form advice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from backend.engines.recommendation_engine import NO_MATCH_RULE_ID, RecommendationRecord


RULE_TYPE_TO_ACTION_CATEGORY = {
    "agronomic": "agronomic_advisory",
    "inventory": "inventory_follow_up",
    "sales": "sales_opportunity",
    "relationship": "relationship_follow_up",
    "competitive": "competitive_response",
    "none": "no_recommendation",
}


class ActionSelectionError(ValueError):
    """Raised when recommendation actions cannot be selected safely."""


@dataclass(frozen=True)
class SelectedAction:
    """Normalized action selected from a structured recommendation."""

    action_id: str
    action_category: str
    source_rule_id: str
    confidence_level: str
    recommended_product_category: str

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic action selection trace metadata."""

        return {
            "action_id": self.action_id,
            "action_category": self.action_category,
            "source_rule_id": self.source_rule_id,
            "confidence_level": self.confidence_level,
            "recommended_product_category": self.recommended_product_category,
        }


def select_actions(
    recommendations: Sequence[RecommendationRecord | Mapping[str, Any]],
) -> tuple[SelectedAction, ...]:
    """Select stable, deduplicated actions from recommendation records."""

    selected_actions: list[SelectedAction] = []
    seen_actions: set[str] = set()

    for recommendation in recommendations:
        recommendation_data = _recommendation_to_mapping(recommendation)
        rule_type = str(recommendation_data["rule_type"])
        action_category = RULE_TYPE_TO_ACTION_CATEGORY.get(rule_type)
        if action_category is None:
            raise ActionSelectionError(f"Unsupported recommendation rule_type: {rule_type}")

        for action_id in recommendation_data["recommended_actions"]:
            _validate_action_id(action_id)
            if action_id in seen_actions:
                continue
            seen_actions.add(action_id)
            selected_actions.append(
                SelectedAction(
                    action_id=action_id,
                    action_category=action_category,
                    source_rule_id=str(recommendation_data["matched_rule_id"]),
                    confidence_level=str(recommendation_data["confidence_level"]),
                    recommended_product_category=str(
                        recommendation_data["recommended_product_category"]
                    ),
                )
            )

    return tuple(selected_actions)


def _recommendation_to_mapping(
    recommendation: RecommendationRecord | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(recommendation, RecommendationRecord):
        return recommendation.to_row()

    required_fields = (
        "matched_rule_id",
        "rule_type",
        "recommended_actions",
        "recommended_product_category",
        "confidence_level",
    )
    missing_fields = [
        field for field in required_fields if field not in recommendation
    ]
    if missing_fields:
        raise ActionSelectionError(
            "Recommendation record is missing required fields: "
            + ", ".join(missing_fields)
        )
    if recommendation["matched_rule_id"] == NO_MATCH_RULE_ID:
        return {
            **recommendation,
            "rule_type": "none",
        }
    return recommendation


def _validate_action_id(action_id: Any) -> None:
    if not isinstance(action_id, str) or not action_id.strip():
        raise ActionSelectionError("Recommended action IDs must be non-empty strings.")
    if action_id != action_id.lower() or " " in action_id:
        raise ActionSelectionError(
            f"Recommended action ID must be lower snake-case style: {action_id}"
        )
