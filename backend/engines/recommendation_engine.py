"""Structured recommendation generation for Build 04.

This module converts matched contextual rules into recommendation records. It
does not perform priority scoring, anomaly detection, explanation generation,
API formatting, frontend rendering, or free-form reasoning.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.engines.contextual_decision_engine import (
    ContextualRule,
    ENTITY_CONTEXT_COLUMNS,
    RuleMatchResult,
    load_contextual_rules,
    match_contextual_rules,
)


NO_MATCH_RULE_ID = "NO_CONTEXTUAL_RULE_MATCH"
NO_MATCH_ACTION = "record_no_contextual_recommendation"


class RecommendationGenerationError(ValueError):
    """Raised when structured recommendation generation cannot proceed."""


@dataclass(frozen=True)
class RecommendationRecord:
    """Structured next-best-action recommendation record."""

    entity_id: str
    rule_id: str
    rule_type: str
    risk_or_opportunity: str
    recommended_actions: tuple[str, ...]
    recommended_product_category: str
    confidence_level: str
    evidence_signals: dict[str, Any]

    def to_row(self) -> dict[str, Any]:
        """Return a stable row payload for recommendation outputs."""

        return {
            "entity_id": self.entity_id,
            "matched_rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "risk_or_opportunity": self.risk_or_opportunity,
            "recommended_actions": list(self.recommended_actions),
            "recommended_product_category": self.recommended_product_category,
            "confidence_level": self.confidence_level,
            "evidence_signals": self.evidence_signals,
            "recommendation_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic trace metadata for downstream explainability."""

        return {
            "entity_id": self.entity_id,
            "matched_rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "risk_or_opportunity": self.risk_or_opportunity,
            "recommended_actions": list(self.recommended_actions),
            "recommended_product_category": self.recommended_product_category,
            "confidence_level": self.confidence_level,
            "evidence_signals": self.evidence_signals,
        }


def generate_recommendations(
    entity_row: Mapping[str, Any],
    match_result: RuleMatchResult | None = None,
    rules: Sequence[ContextualRule] | None = None,
) -> tuple[RecommendationRecord, ...]:
    """Generate structured recommendation records for one contextual entity."""

    entity_id = str(entity_row.get("entity_id", "")).strip()
    if not entity_id:
        raise RecommendationGenerationError("Recommendation generation requires entity_id.")

    resolved_match = match_result or match_contextual_rules(entity_row, rules=rules)
    if resolved_match.entity_id != entity_id:
        raise RecommendationGenerationError(
            "Recommendation entity_id does not match rule match entity_id."
        )

    if not resolved_match.has_match:
        return (
            RecommendationRecord(
                entity_id=entity_id,
                rule_id=NO_MATCH_RULE_ID,
                rule_type="none",
                risk_or_opportunity="No contextual rule matched",
                recommended_actions=(NO_MATCH_ACTION,),
                recommended_product_category="None",
                confidence_level="Low",
                evidence_signals={},
            ),
        )

    return tuple(
        _record_from_rule(entity_row, rule)
        for rule in resolved_match.matched_rules
    )


def build_recommendation_view(
    contextual_view: pd.DataFrame,
    rules: Sequence[ContextualRule] | None = None,
) -> pd.DataFrame:
    """Build stable structured recommendation rows from contextual inputs."""

    loaded_rules = tuple(rules) if rules is not None else load_contextual_rules()
    rows: list[dict[str, Any]] = []

    for entity_row in contextual_view.to_dict(orient="records"):
        match_result = match_contextual_rules(entity_row, loaded_rules)
        for recommendation in generate_recommendations(entity_row, match_result):
            output_row = {
                column: entity_row.get(column, "")
                for column in ENTITY_CONTEXT_COLUMNS
                if column in contextual_view.columns
            }
            output_row.update(recommendation.to_row())
            rows.append(output_row)

    output = pd.DataFrame(rows)
    if output.empty:
        return output

    sort_columns = [
        column
        for column in ("entity_id", "matched_rule_id")
        if column in output.columns
    ]
    if sort_columns:
        output = output.sort_values(sort_columns, kind="mergesort")
    return output.reset_index(drop=True)


def _record_from_rule(
    entity_row: Mapping[str, Any],
    rule: ContextualRule,
) -> RecommendationRecord:
    return RecommendationRecord(
        entity_id=str(entity_row["entity_id"]),
        rule_id=rule.rule_id,
        rule_type=rule.rule_type,
        risk_or_opportunity=rule.risk_or_opportunity,
        recommended_actions=rule.recommended_actions,
        recommended_product_category=rule.recommended_product_category,
        confidence_level=rule.confidence_level,
        evidence_signals={
            field: _to_builtin_value(entity_row[field])
            for field in rule.evidence_fields
            if field in entity_row
        },
    )


def _to_builtin_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
