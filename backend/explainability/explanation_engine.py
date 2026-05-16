"""Deterministic explanation generation for Build 06.

This module converts mapped evidence plus confidence metadata into structured
explanation records. It does not calculate priority scores, create
recommendations, detect anomalies, call APIs, render frontend content, or use
uncontrolled LLM generation.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.explainability.confidence_engine import assess_confidence
from backend.explainability.explanation_registry import load_explanation_template_config
from backend.explainability.template_generator import render_explanation_text


EXPLANATION_OUTPUT_COLUMNS = [
    "entity_id",
    "explanation_type",
    "source_output_type",
    "source_output_id",
    "summary_text",
    "evidence_items",
    "confidence_level",
    "confidence_reasoning",
    "source_trace_ids",
    "template_used",
    "safety_validation_status",
]

EXPLANATION_TRACE_COLUMNS = [
    "entity_id",
    "explanation_type",
    "source_output_type",
    "source_output_id",
    "evidence_used",
    "template_used",
    "confidence_rule_used",
    "safety_validation_status",
]


class ExplanationGenerationError(ValueError):
    """Raised when explanation generation cannot proceed safely."""


@dataclass(frozen=True)
class ExplanationRecord:
    """Structured deterministic explanation record."""

    entity_id: str
    explanation_type: str
    source_output_type: str
    source_output_id: str
    summary_text: str
    evidence_items: list[dict[str, Any]]
    confidence_level: str
    confidence_reasoning: str
    source_trace_ids: list[str]
    template_used: str
    safety_validation_status: str
    confidence_rule_used: str

    def to_row(self) -> dict[str, Any]:
        """Return the stable explanation output row."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_type": self.source_output_type,
            "source_output_id": self.source_output_id,
            "summary_text": self.summary_text,
            "evidence_items": self.evidence_items,
            "confidence_level": self.confidence_level,
            "confidence_reasoning": self.confidence_reasoning,
            "source_trace_ids": self.source_trace_ids,
            "template_used": self.template_used,
            "safety_validation_status": self.safety_validation_status,
        }

    def to_trace_row(self) -> dict[str, Any]:
        """Return stable explanation trace metadata."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_type": self.source_output_type,
            "source_output_id": self.source_output_id,
            "evidence_used": self.evidence_items,
            "template_used": self.template_used,
            "confidence_rule_used": self.confidence_rule_used,
            "safety_validation_status": self.safety_validation_status,
        }


def generate_explanation(
    evidence_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> ExplanationRecord:
    """Generate one deterministic explanation from a confidence-enriched evidence row."""

    template_config = config or load_explanation_template_config()
    _validate_explanation_row(evidence_row)

    confidence_assessment = assess_confidence(evidence_row)
    render_row = dict(evidence_row)
    render_row.update(
        {
            "confidence_level": confidence_assessment.confidence_level,
            "confidence_reasoning": confidence_assessment.confidence_reasoning,
        }
    )
    summary_text = render_explanation_text(render_row, template_config)

    return ExplanationRecord(
        entity_id=str(evidence_row["entity_id"]),
        explanation_type=str(evidence_row["explanation_type"]),
        source_output_type=str(evidence_row["source_output_type"]),
        source_output_id=str(evidence_row["source_output_id"]),
        summary_text=summary_text,
        evidence_items=list(evidence_row["evidence_items"]),
        confidence_level=confidence_assessment.confidence_level,
        confidence_reasoning=confidence_assessment.confidence_reasoning,
        source_trace_ids=list(evidence_row["source_trace_ids"]),
        template_used=str(evidence_row["template_id"]),
        safety_validation_status="Safe",
        confidence_rule_used=confidence_assessment.confidence_rule_id,
    )


def build_explanation_view(
    evidence_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build stable explanation output rows from mapped evidence."""

    if evidence_view.empty:
        return pd.DataFrame(columns=EXPLANATION_OUTPUT_COLUMNS)

    template_config = config or load_explanation_template_config()
    records = [
        generate_explanation(row, template_config)
        for row in evidence_view.to_dict(orient="records")
    ]
    output = pd.DataFrame(
        [record.to_row() for record in records],
        columns=EXPLANATION_OUTPUT_COLUMNS,
    )
    return _sort_explanations(output)


def build_explanation_trace_view(
    evidence_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build stable explanation trace rows from mapped evidence."""

    if evidence_view.empty:
        return pd.DataFrame(columns=EXPLANATION_TRACE_COLUMNS)

    template_config = config or load_explanation_template_config()
    records = [
        generate_explanation(row, template_config)
        for row in evidence_view.to_dict(orient="records")
    ]
    output = pd.DataFrame(
        [record.to_trace_row() for record in records],
        columns=EXPLANATION_TRACE_COLUMNS,
    )
    return output.sort_values(
        ["entity_id", "explanation_type", "source_output_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _validate_explanation_row(evidence_row: Mapping[str, Any]) -> None:
    required_fields = (
        "entity_id",
        "explanation_type",
        "source_output_type",
        "source_output_id",
        "evidence_items",
        "source_trace_ids",
        "template_id",
        "evidence_trace",
    )
    missing_fields = [field for field in required_fields if field not in evidence_row]
    if missing_fields:
        raise ExplanationGenerationError(
            "Evidence row is missing explanation fields: "
            + ", ".join(missing_fields)
        )
    if not isinstance(evidence_row["evidence_items"], list) or not evidence_row["evidence_items"]:
        raise ExplanationGenerationError("Explanation generation requires evidence_items.")
    if not isinstance(evidence_row["source_trace_ids"], list) or not evidence_row["source_trace_ids"]:
        raise ExplanationGenerationError("Explanation generation requires source_trace_ids.")


def _sort_explanations(explanation_view: pd.DataFrame) -> pd.DataFrame:
    return explanation_view.sort_values(
        ["entity_id", "explanation_type", "source_output_id"],
        kind="mergesort",
    ).reset_index(drop=True)
