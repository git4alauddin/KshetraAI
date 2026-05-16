"""Configuration registry for Build 06 explainability.

This module loads controlled explanation templates and confidence rules. It
does not generate explanations, score priorities, create recommendations,
detect anomalies, call APIs, or render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_EXPLANATION_TEMPLATES_PATH = Path("backend/config/explanation_templates.yaml")
DEFAULT_CONFIDENCE_RULES_PATH = Path("backend/config/confidence_rules.yaml")


class ExplanationRegistryError(ValueError):
    """Raised when explainability configuration is invalid or incomplete."""


@dataclass(frozen=True)
class ExplanationTypeSpec:
    """Configured explanation type metadata."""

    explanation_type: str
    label: str
    source_output_type: str
    required_trace_fields: tuple[str, ...]
    default_template_id: str


@dataclass(frozen=True)
class ExplanationTemplateSpec:
    """Configured deterministic explanation template metadata."""

    template_id: str
    explanation_type: str
    source_output_type: str
    confidence_rule_id: str
    required_evidence_fields: tuple[str, ...]
    placeholders: tuple[str, ...]
    text_template: str
    safety_notes: tuple[str, ...]


def load_explanation_template_config(
    config_path: Path | str = DEFAULT_EXPLANATION_TEMPLATES_PATH,
) -> dict[str, Any]:
    """Load and validate explanation template configuration."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    _validate_template_config(config)
    return config


def load_confidence_rule_config(
    config_path: Path | str = DEFAULT_CONFIDENCE_RULES_PATH,
) -> dict[str, Any]:
    """Load and validate confidence rule configuration."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    _validate_confidence_config(config)
    return config


def list_explanation_type_specs(
    config: Mapping[str, Any] | None = None,
) -> tuple[ExplanationTypeSpec, ...]:
    """Return explanation type specs in deterministic type order."""

    template_config = config or load_explanation_template_config()
    specs = [
        ExplanationTypeSpec(
            explanation_type=str(explanation_type),
            label=str(type_config["label"]),
            source_output_type=str(type_config["source_output_type"]),
            required_trace_fields=tuple(
                str(field)
                for field in type_config["required_trace_fields"]
            ),
            default_template_id=str(type_config["default_template_id"]),
        )
        for explanation_type, type_config in template_config["explanation_types"].items()
    ]
    return tuple(sorted(specs, key=lambda spec: spec.explanation_type))


def list_template_specs(
    config: Mapping[str, Any] | None = None,
) -> tuple[ExplanationTemplateSpec, ...]:
    """Return explanation template specs in deterministic template order."""

    template_config = config or load_explanation_template_config()
    specs = [
        ExplanationTemplateSpec(
            template_id=str(template_id),
            explanation_type=str(template["explanation_type"]),
            source_output_type=str(template["source_output_type"]),
            confidence_rule_id=str(template["confidence_rule_id"]),
            required_evidence_fields=tuple(
                str(field)
                for field in template["required_evidence_fields"]
            ),
            placeholders=tuple(str(field) for field in template["placeholders"]),
            text_template=str(template["text_template"]),
            safety_notes=tuple(str(note) for note in template["safety_notes"]),
        )
        for template_id, template in template_config["templates"].items()
    ]
    return tuple(sorted(specs, key=lambda spec: spec.template_id))


def get_type_spec(
    explanation_type: str,
    config: Mapping[str, Any] | None = None,
) -> ExplanationTypeSpec:
    """Return the configured spec for one explanation type."""

    for spec in list_explanation_type_specs(config):
        if spec.explanation_type == explanation_type:
            return spec
    raise ExplanationRegistryError(f"Unknown explanation_type: {explanation_type}")


def get_template_spec(
    template_id: str,
    config: Mapping[str, Any] | None = None,
) -> ExplanationTemplateSpec:
    """Return the configured spec for one explanation template."""

    for spec in list_template_specs(config):
        if spec.template_id == template_id:
            return spec
    raise ExplanationRegistryError(f"Unknown explanation template: {template_id}")


def default_template_for_type(
    explanation_type: str,
    config: Mapping[str, Any] | None = None,
) -> ExplanationTemplateSpec:
    """Return the default configured template for an explanation type."""

    template_config = config or load_explanation_template_config()
    type_spec = get_type_spec(explanation_type, template_config)
    return get_template_spec(type_spec.default_template_id, template_config)


def _validate_template_config(config: Mapping[str, Any]) -> None:
    required_sections = (
        "template_policy",
        "output_schema",
        "trace_output_schema",
        "explanation_types",
        "templates",
        "safety_terms",
    )
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise ExplanationRegistryError(
            "Explanation template config is missing required sections: "
            + ", ".join(missing_sections)
        )

    template_ids = set(config["templates"])
    explanation_types = set(config["explanation_types"])
    for explanation_type, type_config in config["explanation_types"].items():
        if type_config["default_template_id"] not in template_ids:
            raise ExplanationRegistryError(
                f"{explanation_type}: default template is not configured."
            )
        if not type_config["required_trace_fields"]:
            raise ExplanationRegistryError(
                f"{explanation_type}: required_trace_fields cannot be empty."
            )

    for template_id, template in config["templates"].items():
        if template["explanation_type"] not in explanation_types:
            raise ExplanationRegistryError(
                f"{template_id}: unsupported explanation_type."
            )
        if not template["required_evidence_fields"]:
            raise ExplanationRegistryError(
                f"{template_id}: required_evidence_fields cannot be empty."
            )
        if not template["placeholders"]:
            raise ExplanationRegistryError(f"{template_id}: placeholders cannot be empty.")
        if not template["safety_notes"]:
            raise ExplanationRegistryError(f"{template_id}: safety_notes cannot be empty.")


def _validate_confidence_config(config: Mapping[str, Any]) -> None:
    required_sections = ("confidence_policy", "confidence_levels", "confidence_rules")
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise ExplanationRegistryError(
            "Confidence rule config is missing required sections: "
            + ", ".join(missing_sections)
        )

    supported_levels = tuple(config["confidence_policy"]["supported_levels"])
    if supported_levels != ("High", "Medium", "Low"):
        raise ExplanationRegistryError("Confidence levels must be High, Medium, Low.")

    for level in supported_levels:
        if level not in config["confidence_levels"]:
            raise ExplanationRegistryError(f"Missing confidence level: {level}")

    for rule_id, rule in config["confidence_rules"].items():
        if rule["rule_id"] != rule_id:
            raise ExplanationRegistryError(f"Confidence rule_id mismatch: {rule_id}")
        if not rule["applies_to"]:
            raise ExplanationRegistryError(f"{rule_id}: applies_to cannot be empty.")
        if not rule["evidence_sources"]:
            raise ExplanationRegistryError(f"{rule_id}: evidence_sources cannot be empty.")
