"""Confidence reasoning for Build 06 explainability.

This module converts evidence bundles into deterministic confidence metadata.
It does not generate final explanation text, calculate priority scores, create
recommendations, detect anomalies, call APIs, or render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.explainability.evidence_mapper import EvidenceBundle
from backend.explainability.explanation_registry import load_confidence_rule_config


CONFIDENCE_OUTPUT_COLUMNS = [
    "entity_id",
    "explanation_type",
    "source_output_type",
    "source_output_id",
    "confidence_level",
    "confidence_rank",
    "confidence_reasoning",
    "confidence_rule_id",
    "evidence_count",
    "trace_completeness",
    "confidence_trace",
]


class ConfidenceReasoningError(ValueError):
    """Raised when confidence reasoning cannot proceed safely."""


@dataclass(frozen=True)
class ConfidenceAssessment:
    """Stable confidence metadata derived from mapped evidence."""

    entity_id: str
    explanation_type: str
    source_output_type: str
    source_output_id: str
    confidence_level: str
    confidence_rank: int
    confidence_reasoning: str
    confidence_rule_id: str
    evidence_count: int
    trace_completeness: float

    def to_row(self) -> dict[str, Any]:
        """Return a stable confidence output row."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_type": self.source_output_type,
            "source_output_id": self.source_output_id,
            "confidence_level": self.confidence_level,
            "confidence_rank": self.confidence_rank,
            "confidence_reasoning": self.confidence_reasoning,
            "confidence_rule_id": self.confidence_rule_id,
            "evidence_count": self.evidence_count,
            "trace_completeness": self.trace_completeness,
            "confidence_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic confidence trace metadata."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_id": self.source_output_id,
            "confidence_level": self.confidence_level,
            "confidence_rank": self.confidence_rank,
            "confidence_rule_id": self.confidence_rule_id,
            "evidence_count": self.evidence_count,
            "trace_completeness": self.trace_completeness,
        }


def assess_confidence(
    evidence: EvidenceBundle | Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> ConfidenceAssessment:
    """Assess deterministic confidence from one evidence bundle."""

    confidence_config = config or load_confidence_rule_config()
    evidence_row = _evidence_to_mapping(evidence)
    confidence_rule_id = _resolve_confidence_rule_id(evidence_row)
    if confidence_rule_id not in confidence_config["confidence_rules"]:
        raise ConfidenceReasoningError(f"Unknown confidence_rule_id: {confidence_rule_id}")

    rule = confidence_config["confidence_rules"][confidence_rule_id]
    explanation_type = str(evidence_row["explanation_type"])
    if explanation_type not in rule["applies_to"]:
        raise ConfidenceReasoningError(
            f"Confidence rule {confidence_rule_id} does not apply to {explanation_type}."
        )

    evidence_count = _evidence_count(evidence_row)
    if evidence_count <= 0:
        raise ConfidenceReasoningError("Confidence reasoning requires at least one evidence item.")

    trace_completeness = _trace_completeness(evidence_row, rule)
    confidence_level = _select_confidence_level(
        evidence_count=evidence_count,
        trace_completeness=trace_completeness,
        rule=rule,
    )
    level_config = confidence_config["confidence_levels"][confidence_level]

    return ConfidenceAssessment(
        entity_id=str(evidence_row["entity_id"]),
        explanation_type=explanation_type,
        source_output_type=str(evidence_row["source_output_type"]),
        source_output_id=str(evidence_row["source_output_id"]),
        confidence_level=confidence_level,
        confidence_rank=int(level_config["confidence_rank"]),
        confidence_reasoning=str(level_config["reasoning_template"]),
        confidence_rule_id=confidence_rule_id,
        evidence_count=evidence_count,
        trace_completeness=trace_completeness,
    )


def add_confidence_reasoning(
    evidence_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Append confidence metadata to mapped evidence rows."""

    if evidence_view.empty:
        return pd.DataFrame(columns=[*evidence_view.columns, *CONFIDENCE_OUTPUT_COLUMNS])

    confidence_config = config or load_confidence_rule_config()
    assessments = [
        assess_confidence(row, confidence_config)
        for row in evidence_view.to_dict(orient="records")
    ]
    assessment_rows = [assessment.to_row() for assessment in assessments]
    confidence_columns = pd.DataFrame(assessment_rows, columns=CONFIDENCE_OUTPUT_COLUMNS)

    output = evidence_view.copy().reset_index(drop=True)
    for column in CONFIDENCE_OUTPUT_COLUMNS:
        output[column] = confidence_columns[column]

    return output.sort_values(
        ["entity_id", "explanation_type", "source_output_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _evidence_to_mapping(
    evidence: EvidenceBundle | Mapping[str, Any],
) -> Mapping[str, Any]:
    if isinstance(evidence, EvidenceBundle):
        return evidence.to_row()

    required_fields = (
        "entity_id",
        "explanation_type",
        "source_output_type",
        "source_output_id",
        "evidence_items",
        "source_trace_ids",
        "evidence_trace",
    )
    missing_fields = [field for field in required_fields if field not in evidence]
    if missing_fields:
        raise ConfidenceReasoningError(
            "Evidence row is missing confidence fields: "
            + ", ".join(missing_fields)
        )
    return evidence


def _resolve_confidence_rule_id(evidence_row: Mapping[str, Any]) -> str:
    evidence_trace = evidence_row["evidence_trace"]
    if not isinstance(evidence_trace, Mapping):
        raise ConfidenceReasoningError("Evidence row requires evidence_trace metadata.")
    confidence_rule_id = str(evidence_trace.get("confidence_rule_id", "")).strip()
    if not confidence_rule_id:
        raise ConfidenceReasoningError("Evidence trace is missing confidence_rule_id.")
    return confidence_rule_id


def _evidence_count(evidence_row: Mapping[str, Any]) -> int:
    evidence_items = evidence_row["evidence_items"]
    if not isinstance(evidence_items, list):
        raise ConfidenceReasoningError("Evidence items must be a list.")
    return len(evidence_items)


def _trace_completeness(
    evidence_row: Mapping[str, Any],
    rule: Mapping[str, Any],
) -> float:
    source_trace_ids = evidence_row["source_trace_ids"]
    if not isinstance(source_trace_ids, list):
        raise ConfidenceReasoningError("source_trace_ids must be a list.")

    evidence_trace = evidence_row["evidence_trace"]
    required_evidence_fields = evidence_trace.get("required_evidence_fields", [])
    if not isinstance(required_evidence_fields, list):
        raise ConfidenceReasoningError("required_evidence_fields must be a list.")

    expected_count = max(1, len(rule["evidence_sources"]), len(required_evidence_fields))
    present_count = min(expected_count, len(source_trace_ids) + _evidence_count(evidence_row))
    return round(present_count / expected_count, 4)


def _select_confidence_level(
    *,
    evidence_count: int,
    trace_completeness: float,
    rule: Mapping[str, Any],
) -> str:
    for level_name, threshold_key in (
        ("High", "high_when"),
        ("Medium", "medium_when"),
        ("Low", "low_when"),
    ):
        threshold = rule[threshold_key]
        if (
            evidence_count >= int(threshold["minimum_evidence_items"])
            and trace_completeness >= float(threshold["minimum_trace_completeness"])
        ):
            return level_name
    raise ConfidenceReasoningError("Evidence did not satisfy any configured confidence level.")
