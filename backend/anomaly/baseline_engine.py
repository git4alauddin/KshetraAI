"""Baseline comparison preparation for Build 05.

This module enriches anomaly feature rows with configured baseline values and
trace metadata. It does not detect deviations, classify severity, generate
alerts, create recommendations, modify priority scores, or format explanations.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DEFAULT_BASELINES_PATH = Path("backend/config/baselines.yaml")
BASELINE_GENERATED_AT = "configured_static_baseline"


class BaselineEngineError(ValueError):
    """Raised when baseline preparation input violates the Build 05 contract."""


@dataclass(frozen=True)
class BaselineSpec:
    """Configured baseline signal metadata."""

    baseline_signal: str
    source_signal: str
    default_value: float
    baseline_group: str
    source_view: str
    baseline_window_days: int
    baseline_source: str

    def to_trace(self) -> dict[str, Any]:
        """Return stable baseline metadata for anomaly trace logging."""

        return {
            "baseline_signal": self.baseline_signal,
            "source_signal": self.source_signal,
            "default_value": self.default_value,
            "baseline_group": self.baseline_group,
            "source_view": self.source_view,
            "baseline_window_days": self.baseline_window_days,
            "baseline_source": self.baseline_source,
        }


def load_baseline_config(
    config_path: Path | str = DEFAULT_BASELINES_PATH,
) -> dict[str, Any]:
    """Load and validate baseline configuration from YAML."""

    with Path(config_path).open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    _validate_baseline_config(config)
    return config


def list_baseline_specs(
    config: Mapping[str, Any] | None = None,
) -> tuple[BaselineSpec, ...]:
    """Return configured baseline specs in stable group/signal order."""

    baseline_config = config or load_baseline_config()
    policy = baseline_config["baseline_policy"]
    specs: list[BaselineSpec] = []

    for group_name, group in baseline_config["baseline_groups"].items():
        for baseline_signal, signal_config in group["signals"].items():
            specs.append(
                BaselineSpec(
                    baseline_signal=baseline_signal,
                    source_signal=str(signal_config["source_signal"]),
                    default_value=float(signal_config["default_value"]),
                    baseline_group=str(group_name),
                    source_view=str(group["source_view"]),
                    baseline_window_days=int(group["baseline_window_days"]),
                    baseline_source=str(policy["default_source"]),
                )
            )

    return tuple(sorted(specs, key=lambda spec: (spec.baseline_group, spec.baseline_signal)))


def build_baseline_feature_view(
    anomaly_feature_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Add configured baseline columns and baseline trace metadata."""

    baseline_config = config or load_baseline_config()
    specs = list_baseline_specs(baseline_config)
    output = anomaly_feature_view.copy()
    _validate_required_source_signals(output, specs)

    for spec in specs:
        output[spec.baseline_signal] = spec.default_value

    output["baseline_trace"] = [
        {
            spec.baseline_signal: spec.to_trace()
            for spec in specs
        }
        for _row_index in range(len(output))
    ]

    if "entity_id" in output.columns:
        output = output.sort_values("entity_id", kind="mergesort")
    return output.reset_index(drop=True)


def build_baseline_long_view(
    anomaly_feature_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Return one baseline metadata row per entity and baseline signal."""

    baseline_config = config or load_baseline_config()
    specs = list_baseline_specs(baseline_config)
    policy = baseline_config["baseline_policy"]
    _validate_required_source_signals(anomaly_feature_view, specs)
    _validate_join_keys(anomaly_feature_view, policy["deterministic_join_keys"])

    rows: list[dict[str, Any]] = []
    for source_row in anomaly_feature_view.to_dict(orient="records"):
        for spec in specs:
            rows.append(
                {
                    "entity_id": source_row.get("entity_id", ""),
                    "territory_id": source_row.get("territory_id", ""),
                    "baseline_signal": spec.baseline_signal,
                    "baseline_value": spec.default_value,
                    "baseline_source": spec.baseline_source,
                    "baseline_window_days": spec.baseline_window_days,
                    "baseline_generated_at": BASELINE_GENERATED_AT,
                }
            )

    output = pd.DataFrame(rows, columns=baseline_config["baseline_output_schema"])
    if output.empty:
        return output
    return output.sort_values(
        ["entity_id", "baseline_signal"],
        kind="mergesort",
    ).reset_index(drop=True)


def _validate_baseline_config(config: Mapping[str, Any]) -> None:
    required_sections = ("baseline_policy", "baseline_groups", "baseline_output_schema")
    missing_sections = [section for section in required_sections if section not in config]
    if missing_sections:
        raise BaselineEngineError(
            "Baseline config is missing required sections: "
            + ", ".join(missing_sections)
        )

    score_range = config["baseline_policy"]["baseline_score_range"]
    min_score = float(score_range["min"])
    max_score = float(score_range["max"])
    if min_score >= max_score:
        raise BaselineEngineError("Baseline score range min must be lower than max.")

    for group_name, group in config["baseline_groups"].items():
        if group["source_view"] != "anomaly_feature_view":
            raise BaselineEngineError(f"{group_name}: source_view must be anomaly_feature_view.")
        if int(group["baseline_window_days"]) <= 0:
            raise BaselineEngineError(f"{group_name}: baseline_window_days must be positive.")
        if not group["signals"]:
            raise BaselineEngineError(f"{group_name}: signals cannot be empty.")

        for baseline_signal, signal_config in group["signals"].items():
            if not str(baseline_signal).endswith("_baseline_score"):
                raise BaselineEngineError(f"{baseline_signal}: baseline signal name is invalid.")
            default_value = float(signal_config["default_value"])
            if default_value < min_score or default_value > max_score:
                raise BaselineEngineError(
                    f"{baseline_signal}: default_value must be within {min_score:g}-{max_score:g}."
                )


def _validate_required_source_signals(
    dataframe: pd.DataFrame,
    specs: tuple[BaselineSpec, ...],
) -> None:
    missing_columns = sorted(
        {
            spec.source_signal
            for spec in specs
            if spec.source_signal not in dataframe.columns
        }
    )
    if missing_columns:
        raise BaselineEngineError(
            "Anomaly feature view is missing baseline source signals: "
            + ", ".join(missing_columns)
        )

    invalid_columns: list[str] = []
    for spec in specs:
        values = pd.to_numeric(dataframe[spec.source_signal], errors="coerce")
        if values.isna().any() or not values.between(0, 100).all():
            invalid_columns.append(spec.source_signal)
    if invalid_columns:
        raise BaselineEngineError(
            "Baseline source signals must be numeric and within 0-100: "
            + ", ".join(sorted(set(invalid_columns)))
        )


def _validate_join_keys(
    dataframe: pd.DataFrame,
    join_keys: list[str],
) -> None:
    missing_keys = [key for key in join_keys if key not in dataframe.columns]
    if missing_keys:
        raise BaselineEngineError(
            "Anomaly feature view is missing baseline join keys: "
            + ", ".join(missing_keys)
        )
