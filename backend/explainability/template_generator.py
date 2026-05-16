"""Template rendering for Build 06 explainability.

This module renders configured explanation templates from mapped evidence and
confidence metadata. It does not calculate scores, create recommendations,
detect anomalies, call APIs, render frontend content, or use uncontrolled LLM
generation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from backend.explainability.explanation_registry import (
    ExplanationTemplateSpec,
    get_template_spec,
    load_explanation_template_config,
)


class TemplateGenerationError(ValueError):
    """Raised when deterministic template rendering cannot proceed safely."""


def render_explanation_text(
    explanation_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> str:
    """Render one configured explanation template from evidence and confidence data."""

    template_config = config or load_explanation_template_config()
    template_id = str(explanation_row.get("template_id", "")).strip()
    if not template_id:
        raise TemplateGenerationError("Explanation row is missing template_id.")

    template = get_template_spec(template_id, template_config)
    placeholders = _build_placeholders(explanation_row, template)
    try:
        rendered_text = template.text_template.format(**placeholders)
    except KeyError as error:
        raise TemplateGenerationError(f"Missing explanation placeholder: {error}") from error

    _validate_safe_text(rendered_text, template_config)
    return rendered_text


def summarize_evidence_items(
    evidence_items: Sequence[Mapping[str, Any]],
    limit: int = 3,
) -> str:
    """Return a stable short evidence summary for template placeholders."""

    if not evidence_items:
        raise TemplateGenerationError("Explanation generation requires evidence items.")

    summaries = [
        _format_evidence_item(item)
        for item in evidence_items[:limit]
    ]
    return "; ".join(summaries)


def _build_placeholders(
    explanation_row: Mapping[str, Any],
    template: ExplanationTemplateSpec,
) -> dict[str, Any]:
    evidence_items = _evidence_items(explanation_row)
    evidence_by_field = {
        str(item["source_field"]): item.get("value")
        for item in evidence_items
        if isinstance(item, Mapping) and "source_field" in item
    }
    source_output_id = str(explanation_row["source_output_id"])

    return {
        "entity_label": str(explanation_row["entity_id"]),
        "priority_level": _placeholder_value(explanation_row, "priority_level", "current"),
        "priority_score": _placeholder_value(
            evidence_by_field,
            "priority_score",
            _placeholder_value(explanation_row, "priority_score", "available"),
        ),
        "top_evidence_summary": summarize_evidence_items(evidence_items),
        "recommended_action_summary": _recommended_action_summary(explanation_row),
        "matched_rule_id": source_output_id,
        "alert_type": _alert_type_summary(explanation_row),
        "severity_level": _placeholder_value(explanation_row, "severity_level", "current"),
        "confidence_level": str(explanation_row.get("confidence_level", "Low")),
        "confidence_reasoning": str(explanation_row.get("confidence_reasoning", "available evidence is limited")),
    }


def _evidence_items(explanation_row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    evidence_items = explanation_row.get("evidence_items")
    if not isinstance(evidence_items, list) or not evidence_items:
        raise TemplateGenerationError("Explanation generation requires evidence_items.")
    invalid_items = [
        item for item in evidence_items
        if not isinstance(item, Mapping) or "source_field" not in item
    ]
    if invalid_items:
        raise TemplateGenerationError("Evidence items must include source_field metadata.")
    return evidence_items


def _format_evidence_item(item: Mapping[str, Any]) -> str:
    source_field = str(item["source_field"]).replace("_", " ")
    value = item.get("value")
    if _is_missing(value):
        return source_field
    return f"{source_field}={value}"


def _recommended_action_summary(explanation_row: Mapping[str, Any]) -> str:
    source_output_id = str(explanation_row.get("source_output_id", "recommendation"))
    if source_output_id and source_output_id != "nan":
        return "The existing recommendation"
    return "The recommendation"


def _alert_type_summary(explanation_row: Mapping[str, Any]) -> str:
    source_output_id = str(explanation_row.get("source_output_id", "anomaly alert"))
    if source_output_id.startswith("ALERT_"):
        return "This anomaly alert"
    return source_output_id.replace("_", " ").title()


def _placeholder_value(
    values: Mapping[str, Any],
    key: str,
    default: Any,
) -> Any:
    value = values.get(key, default)
    if _is_missing(value):
        return default
    return value


def _validate_safe_text(
    rendered_text: str,
    config: Mapping[str, Any],
) -> None:
    forbidden_phrases = config["safety_terms"]["forbidden_phrases"]
    lowered_text = rendered_text.lower()
    unsafe_phrases = [
        phrase for phrase in forbidden_phrases
        if str(phrase).lower() in lowered_text
    ]
    if unsafe_phrases:
        raise TemplateGenerationError(
            "Rendered explanation contains unsafe certainty language: "
            + ", ".join(unsafe_phrases)
        )


def _is_missing(value: Any) -> bool:
    if isinstance(value, (list, tuple, dict)):
        return False
    return bool(pd.isna(value))
