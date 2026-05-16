"""Contextual rule matching for Build 04.

This module loads controlled decision rules and matches them against contextual
entity rows. It does not generate final recommendation records, explanation
text, priority scores, anomaly alerts, API responses, or frontend behavior.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_RULE_DIR = Path("backend/rules")
DEFAULT_DECISION_THRESHOLDS_PATH = Path("backend/config/decision_thresholds.yaml")
RULE_FILE_ORDER = (
    "agronomic_rules.yaml",
    "inventory_rules.yaml",
    "sales_rules.yaml",
    "relationship_rules.yaml",
    "competitor_rules.yaml",
)
CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER = (
    "rule_match_trace_log",
    "recommendation_outputs",
    "recommendation_trace_log",
    "advisory_outputs",
)
ENTITY_CONTEXT_COLUMNS = (
    "entity_id",
    "territory_id",
    "entity_type",
    "primary_crop",
    "priority_score",
    "priority_level",
)


class ContextualRuleMatchingError(ValueError):
    """Raised when contextual rule matching input is invalid."""


@dataclass(frozen=True)
class ContextualRule:
    """Controlled contextual decision rule loaded from YAML."""

    rule_id: str
    rule_type: str
    priority_order: int
    conditions: tuple[dict[str, Any], ...]
    risk_or_opportunity: str
    recommended_actions: tuple[str, ...]
    recommended_product_category: str
    confidence_level: str
    evidence_fields: tuple[str, ...]

    @classmethod
    def from_mapping(cls, rule: Mapping[str, Any]) -> "ContextualRule":
        """Build a contextual rule from a validated YAML mapping."""

        return cls(
            rule_id=str(rule["rule_id"]),
            rule_type=str(rule["rule_type"]),
            priority_order=int(rule["priority_order"]),
            conditions=tuple(dict(condition) for condition in rule["conditions"]["all"]),
            risk_or_opportunity=str(rule["risk_or_opportunity"]),
            recommended_actions=tuple(str(action) for action in rule["recommended_actions"]),
            recommended_product_category=str(rule["recommended_product_category"]),
            confidence_level=str(rule["confidence_level"]),
            evidence_fields=tuple(str(field) for field in rule["evidence_fields"]),
        )

    def to_trace(self, entity_row: Mapping[str, Any]) -> dict[str, Any]:
        """Return matched-rule trace metadata with evidence values."""

        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "risk_or_opportunity": self.risk_or_opportunity,
            "recommended_actions": list(self.recommended_actions),
            "recommended_product_category": self.recommended_product_category,
            "confidence_level": self.confidence_level,
            "evidence_signals": {
                field: _to_builtin_value(entity_row[field])
                for field in self.evidence_fields
                if field in entity_row
            },
        }


@dataclass(frozen=True)
class RuleMatchResult:
    """Traceable contextual rule-matching result for one entity."""

    entity_id: str
    matched_rules: tuple[ContextualRule, ...]

    @property
    def matched_rule_ids(self) -> tuple[str, ...]:
        return tuple(rule.rule_id for rule in self.matched_rules)

    @property
    def has_match(self) -> bool:
        return bool(self.matched_rules)

    def to_trace(self, entity_row: Mapping[str, Any]) -> dict[str, Any]:
        """Return stable matched-rule trace metadata."""

        return {
            "entity_id": self.entity_id,
            "has_match": self.has_match,
            "matched_rule_ids": list(self.matched_rule_ids),
            "matched_rules": [
                rule.to_trace(entity_row)
                for rule in self.matched_rules
            ],
        }


def load_contextual_decision_config(
    config_path: Path | str = DEFAULT_DECISION_THRESHOLDS_PATH,
) -> dict[str, Any]:
    """Load contextual decision controls from the shared decision config."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if "contextual_decision" not in config:
        raise ContextualRuleMatchingError(
            "Decision threshold config is missing contextual_decision section."
        )
    return config["contextual_decision"]


def load_contextual_rules(
    rule_dir: Path | str = DEFAULT_RULE_DIR,
    config: Mapping[str, Any] | None = None,
) -> tuple[ContextualRule, ...]:
    """Load and validate contextual decision rules in deterministic order."""

    contextual_config = config or load_contextual_decision_config()
    rules: list[ContextualRule] = []

    for file_name in RULE_FILE_ORDER:
        path = Path(rule_dir) / file_name
        with path.open(encoding="utf-8") as rule_file:
            rule_config = yaml.safe_load(rule_file)
        for rule in rule_config["rules"]:
            _validate_rule_mapping(rule, contextual_config)
            rules.append(ContextualRule.from_mapping(rule))

    return tuple(
        sorted(
            rules,
            key=lambda rule: (rule.priority_order, rule.rule_id),
        )
    )


def match_contextual_rules(
    entity_row: Mapping[str, Any],
    rules: Sequence[ContextualRule] | None = None,
    config: Mapping[str, Any] | None = None,
) -> RuleMatchResult:
    """Match one entity row to eligible contextual rules."""

    contextual_config = config or load_contextual_decision_config()
    loaded_rules = tuple(rules) if rules is not None else load_contextual_rules(config=contextual_config)
    entity_id = str(entity_row.get("entity_id", "")).strip()
    if not entity_id:
        raise ContextualRuleMatchingError("Contextual rule matching requires entity_id.")

    _validate_required_condition_fields(entity_row, loaded_rules)

    matched_rules = [
        rule
        for rule in loaded_rules
        if _rule_matches(entity_row, rule, contextual_config)
    ]
    max_rules = int(contextual_config["rule_selection"]["max_rules_per_entity"])
    return RuleMatchResult(
        entity_id=entity_id,
        matched_rules=tuple(matched_rules[:max_rules]),
    )


def build_rule_match_view(
    contextual_view: pd.DataFrame,
    rules: Sequence[ContextualRule] | None = None,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build deterministic matched-rule metadata for contextual entity rows."""

    contextual_config = config or load_contextual_decision_config()
    loaded_rules = tuple(rules) if rules is not None else load_contextual_rules(config=contextual_config)
    rows: list[dict[str, Any]] = []

    for row in contextual_view.to_dict(orient="records"):
        match_result = match_contextual_rules(row, loaded_rules, contextual_config)
        output_row = {
            column: row.get(column, "")
            for column in ENTITY_CONTEXT_COLUMNS
            if column in contextual_view.columns
        }
        output_row.update(
            {
                "has_rule_match": match_result.has_match,
                "matched_rule_ids": list(match_result.matched_rule_ids),
                "matched_rule_count": len(match_result.matched_rules),
                "rule_match_trace": match_result.to_trace(row),
            }
        )
        rows.append(output_row)

    output = pd.DataFrame(rows)
    if output.empty:
        return output

    if "entity_id" in output.columns:
        output = output.sort_values("entity_id", kind="mergesort")
    return output.reset_index(drop=True)


def build_contextual_decision_output_views(
    contextual_view: pd.DataFrame,
    rules: Sequence[ContextualRule] | None = None,
) -> dict[str, pd.DataFrame]:
    """Build stable Build 04 recommendation and trace output views."""

    from backend.engines.advisory_engine import build_advisory_view
    from backend.engines.recommendation_engine import build_recommendation_view

    loaded_rules = tuple(rules) if rules is not None else load_contextual_rules()
    rule_match_view = build_rule_match_view(contextual_view, loaded_rules)
    recommendation_outputs = build_recommendation_view(contextual_view, loaded_rules)
    recommendation_trace_log = _select_existing_columns(
        recommendation_outputs,
        (
            "entity_id",
            "matched_rule_id",
            "rule_type",
            "confidence_level",
            "evidence_signals",
            "recommendation_trace",
        ),
    )
    advisory_outputs = build_advisory_view(recommendation_outputs)

    return {
        "rule_match_trace_log": rule_match_view,
        "recommendation_outputs": recommendation_outputs,
        "recommendation_trace_log": recommendation_trace_log,
        "advisory_outputs": advisory_outputs,
    }


def write_contextual_decision_output_views(
    output_views: Mapping[str, pd.DataFrame],
    output_dir: Path | str,
) -> dict[str, Path]:
    """Write Build 04 output views as deterministic CSV files."""

    resolved_output_dir = Path(output_dir).expanduser().resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    output_paths: dict[str, Path] = {}
    for view_name in CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER:
        output_path = resolved_output_dir / f"{view_name}.csv"
        _serialize_complex_columns(output_views[view_name]).to_csv(
            output_path,
            index=False,
            lineterminator="\n",
        )
        output_paths[view_name] = output_path
    return output_paths


def _validate_rule_mapping(
    rule: Mapping[str, Any],
    config: Mapping[str, Any],
) -> None:
    supported_operators = set(config["supported_operators"])
    allowed_rule_types = set(config["allowed_rule_types"])
    allowed_confidence_levels = set(config["confidence_levels"])
    allowed_product_categories = set(config["allowed_product_categories"])

    rule_id = str(rule.get("rule_id", "")).strip()
    if not rule_id:
        raise ContextualRuleMatchingError("Contextual rule is missing rule_id.")
    if rule["rule_type"] not in allowed_rule_types:
        raise ContextualRuleMatchingError(f"Unsupported rule_type for {rule_id}: {rule['rule_type']}")
    if rule["confidence_level"] not in allowed_confidence_levels:
        raise ContextualRuleMatchingError(
            f"Unsupported confidence_level for {rule_id}: {rule['confidence_level']}"
        )
    if rule["recommended_product_category"] not in allowed_product_categories:
        raise ContextualRuleMatchingError(
            "Unsupported recommended_product_category for "
            f"{rule_id}: {rule['recommended_product_category']}"
        )

    if "all" not in rule["conditions"] or not rule["conditions"]["all"]:
        raise ContextualRuleMatchingError(f"Rule {rule_id} must define non-empty all conditions.")

    evidence_fields = set(rule["evidence_fields"])
    for condition in rule["conditions"]["all"]:
        if condition["operator"] not in supported_operators:
            raise ContextualRuleMatchingError(
                f"Unsupported operator for {rule_id}: {condition['operator']}"
            )
        if condition["field"] not in evidence_fields:
            raise ContextualRuleMatchingError(
                f"Condition field {condition['field']} is missing from evidence_fields for {rule_id}."
            )


def _select_existing_columns(
    dataframe: pd.DataFrame,
    columns: Sequence[str],
) -> pd.DataFrame:
    return dataframe.loc[:, [column for column in columns if column in dataframe.columns]].copy()


def _serialize_complex_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    output = dataframe.copy()
    for column in output.columns:
        if output[column].map(lambda value: isinstance(value, (dict, list, tuple))).any():
            output[column] = output[column].map(_stable_json)
    return output


def _stable_json(value: Any) -> str:
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value


def _validate_required_condition_fields(
    entity_row: Mapping[str, Any],
    rules: Sequence[ContextualRule],
) -> None:
    required_fields = {
        condition["field"]
        for rule in rules
        for condition in rule.conditions
    }
    missing_fields = sorted(field for field in required_fields if field not in entity_row)
    if missing_fields:
        raise ContextualRuleMatchingError(
            "Contextual input row is missing required rule fields: "
            + ", ".join(missing_fields)
        )


def _rule_matches(
    entity_row: Mapping[str, Any],
    rule: ContextualRule,
    config: Mapping[str, Any],
) -> bool:
    return all(
        _condition_matches(entity_row, condition, config)
        for condition in rule.conditions
    )


def _condition_matches(
    entity_row: Mapping[str, Any],
    condition: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    field = str(condition["field"])
    operator = str(condition["operator"])
    expected_value = condition["value"]
    actual_value = entity_row[field]

    if operator not in set(config["supported_operators"]):
        raise ContextualRuleMatchingError(f"Unsupported condition operator: {operator}")
    if operator == "gte":
        return _numeric_value(actual_value, field) >= _numeric_value(expected_value, field)
    if operator == "lte":
        return _numeric_value(actual_value, field) <= _numeric_value(expected_value, field)
    if operator == "eq":
        return str(actual_value).strip().lower() == str(expected_value).strip().lower()

    raise ContextualRuleMatchingError(f"Unsupported condition operator: {operator}")


def _numeric_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise ContextualRuleMatchingError(f"Contextual rule field must be numeric: {field}")
    return float(numeric_value)


def _to_builtin_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
