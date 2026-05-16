"""Advisory action bundling for Build 04.

This module turns structured recommendation records into entity-level advisory
bundles. It does not generate human-readable explanation text, priority scores,
anomaly alerts, API responses, frontend content, or free-form advice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.engines.action_selector import SelectedAction, select_actions
from backend.engines.contextual_decision_engine import ENTITY_CONTEXT_COLUMNS
from backend.engines.recommendation_engine import NO_MATCH_RULE_ID, RecommendationRecord


CONFIDENCE_RANKS = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


class AdvisorySelectionError(ValueError):
    """Raised when advisory action bundles cannot be built safely."""


@dataclass(frozen=True)
class AdvisoryBundle:
    """Entity-level advisory/action bundle from structured recommendations."""

    entity_id: str
    advisory_actions: tuple[str, ...]
    action_categories: tuple[str, ...]
    recommended_product_categories: tuple[str, ...]
    confidence_level: str
    matched_rule_ids: tuple[str, ...]
    risk_or_opportunity_labels: tuple[str, ...]
    selected_actions: tuple[SelectedAction, ...]

    def to_row(self) -> dict[str, Any]:
        """Return a stable advisory bundle row."""

        return {
            "entity_id": self.entity_id,
            "advisory_actions": list(self.advisory_actions),
            "action_categories": list(self.action_categories),
            "recommended_product_categories": list(self.recommended_product_categories),
            "confidence_level": self.confidence_level,
            "matched_rule_ids": list(self.matched_rule_ids),
            "risk_or_opportunity_labels": list(self.risk_or_opportunity_labels),
            "advisory_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic advisory trace metadata."""

        return {
            "entity_id": self.entity_id,
            "confidence_level": self.confidence_level,
            "matched_rule_ids": list(self.matched_rule_ids),
            "selected_actions": [
                action.to_trace()
                for action in self.selected_actions
            ],
            "risk_or_opportunity_labels": list(self.risk_or_opportunity_labels),
            "recommended_product_categories": list(self.recommended_product_categories),
        }


def build_advisory_bundle(
    recommendations: Sequence[RecommendationRecord | Mapping[str, Any]],
) -> AdvisoryBundle:
    """Build one entity-level advisory bundle from recommendation records."""

    if not recommendations:
        raise AdvisorySelectionError("At least one recommendation is required.")

    recommendation_rows = [_recommendation_to_mapping(recommendation) for recommendation in recommendations]
    entity_ids = {str(row["entity_id"]) for row in recommendation_rows}
    if len(entity_ids) != 1:
        raise AdvisorySelectionError("Advisory bundle recommendations must share one entity_id.")

    selected_actions = select_actions(recommendation_rows)
    matched_rule_ids = _stable_unique(
        str(row["matched_rule_id"])
        for row in recommendation_rows
        if str(row["matched_rule_id"]) != NO_MATCH_RULE_ID
    )
    risk_labels = _stable_unique(str(row["risk_or_opportunity"]) for row in recommendation_rows)
    product_categories = _stable_unique(
        str(row["recommended_product_category"])
        for row in recommendation_rows
        if str(row["recommended_product_category"]) != "None"
    )

    return AdvisoryBundle(
        entity_id=entity_ids.pop(),
        advisory_actions=tuple(action.action_id for action in selected_actions),
        action_categories=_stable_unique(action.action_category for action in selected_actions),
        recommended_product_categories=product_categories,
        confidence_level=_highest_confidence(row["confidence_level"] for row in recommendation_rows),
        matched_rule_ids=matched_rule_ids,
        risk_or_opportunity_labels=risk_labels,
        selected_actions=selected_actions,
    )


def build_advisory_view(recommendation_view: pd.DataFrame) -> pd.DataFrame:
    """Build one advisory bundle row per entity from recommendation records."""

    if "entity_id" not in recommendation_view.columns:
        raise AdvisorySelectionError("Recommendation view is missing required column: entity_id")
    if recommendation_view.empty:
        return recommendation_view.copy()

    rows: list[dict[str, Any]] = []
    for entity_id, group in recommendation_view.groupby("entity_id", sort=True):
        bundle = build_advisory_bundle(group.to_dict(orient="records"))
        context_row = {
            column: group.iloc[0].get(column, "")
            for column in ENTITY_CONTEXT_COLUMNS
            if column in group.columns
        }
        context_row.update(bundle.to_row())
        rows.append(context_row)

    return pd.DataFrame(rows).sort_values("entity_id", kind="mergesort").reset_index(drop=True)


def _recommendation_to_mapping(
    recommendation: RecommendationRecord | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(recommendation, RecommendationRecord):
        return recommendation.to_row()

    required_fields = (
        "entity_id",
        "matched_rule_id",
        "risk_or_opportunity",
        "recommended_actions",
        "recommended_product_category",
        "confidence_level",
    )
    missing_fields = [
        field for field in required_fields if field not in recommendation
    ]
    if missing_fields:
        raise AdvisorySelectionError(
            "Recommendation record is missing required fields: "
            + ", ".join(missing_fields)
        )
    return recommendation


def _highest_confidence(confidence_levels: Sequence[str] | Any) -> str:
    highest_level = "Low"
    highest_rank = CONFIDENCE_RANKS[highest_level]
    for confidence_level in confidence_levels:
        if confidence_level not in CONFIDENCE_RANKS:
            raise AdvisorySelectionError(f"Unsupported confidence_level: {confidence_level}")
        rank = CONFIDENCE_RANKS[confidence_level]
        if rank > highest_rank:
            highest_level = confidence_level
            highest_rank = rank
    return highest_level


def _stable_unique(values: Any) -> tuple[str, ...]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        value = str(value)
        if value in seen:
            continue
        seen.add(value)
        output.append(value)
    return tuple(output)
