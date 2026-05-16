"""Build 01 pipeline runner for canonical processed views.

The runner orchestrates source loading, schema validation, value normalization,
canonical view construction, and optional writing to `datasets/processed/`.
It does not compute features, scores, recommendations, alerts, explanations,
or learning signals.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import pandas as pd

from backend.data.joins.entity_joiner import CANONICAL_VIEW_ORDER, build_canonical_views
from backend.data.loaders.csv_loader import CsvLoaderConfig, load_all_source_datasets
from backend.data.normalizers.value_normalizer import normalize_all_datasets
from backend.data.schemas.dataset_schemas import CANONICAL_VIEW_SOURCES
from backend.data.validators.schema_validator import (
    ValidationSummary,
    assert_valid_all_datasets,
    format_validation_summary,
)
from backend.utils.data_utils import find_project_root


DEFAULT_PROCESSED_DATA_DIR = Path("datasets") / "processed"
VALIDATION_REPORT_FILENAME = "build01_validation_report.json"
SOURCE_MAPPING_FILENAME = "build01_source_to_canonical_mapping.json"


@dataclass(frozen=True)
class Build01PipelineConfig:
    """Configuration for the Build 01 data foundation pipeline."""

    source_dir: Path | str | None = None
    output_dir: Path | str | None = None
    write_outputs: bool = True


@dataclass(frozen=True)
class Build01PipelineResult:
    """Result of a Build 01 pipeline run."""

    raw_datasets: Mapping[str, pd.DataFrame] = field(repr=False)
    normalized_datasets: Mapping[str, pd.DataFrame] = field(repr=False)
    canonical_views: Mapping[str, pd.DataFrame] = field(repr=False)
    validation_summary: ValidationSummary
    output_paths: Mapping[str, Path] = field(default_factory=dict)
    metadata_paths: Mapping[str, Path] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.validation_summary.is_valid


def run_build01_pipeline(
    config: Build01PipelineConfig | None = None,
) -> Build01PipelineResult:
    """Run the complete Build 01 canonical processed-view pipeline."""

    pipeline_config = config or Build01PipelineConfig()
    loader_config = CsvLoaderConfig(source_dir=pipeline_config.source_dir)

    raw_datasets = load_all_source_datasets(loader_config)
    raw_validation = assert_valid_all_datasets(
        raw_datasets,
        include_source_files=True,
        source_config=loader_config,
    )
    normalized_datasets = normalize_all_datasets(raw_datasets)
    normalized_validation = assert_valid_all_datasets(normalized_datasets)
    canonical_views = build_canonical_views(normalized_datasets)

    output_paths: dict[str, Path] = {}
    metadata_paths: dict[str, Path] = {}
    if pipeline_config.write_outputs:
        output_dir = resolve_output_dir(pipeline_config.output_dir)
        output_paths = write_canonical_views(canonical_views, output_dir)
        metadata_paths = write_pipeline_metadata(
            output_dir,
            validation_summary=normalized_validation,
            canonical_views=canonical_views,
        )

    return Build01PipelineResult(
        raw_datasets=raw_datasets,
        normalized_datasets=normalized_datasets,
        canonical_views=canonical_views,
        validation_summary=raw_validation,
        output_paths=output_paths,
        metadata_paths=metadata_paths,
    )


def resolve_output_dir(output_dir: Path | str | None = None) -> Path:
    """Resolve and create the processed output directory."""

    if output_dir is not None:
        resolved = Path(output_dir).expanduser().resolve()
    else:
        resolved = (find_project_root() / DEFAULT_PROCESSED_DATA_DIR).resolve()

    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def write_canonical_views(
    canonical_views: Mapping[str, pd.DataFrame],
    output_dir: Path | str,
) -> dict[str, Path]:
    """Write canonical views as deterministic CSV files."""

    resolved_output_dir = Path(output_dir).expanduser().resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    output_paths: dict[str, Path] = {}
    for view_name in CANONICAL_VIEW_ORDER:
        dataframe = canonical_views[view_name]
        output_path = resolved_output_dir / f"{view_name}.csv"
        dataframe.to_csv(output_path, index=False, lineterminator="\n")
        output_paths[view_name] = output_path

    return output_paths


def write_pipeline_metadata(
    output_dir: Path | str,
    *,
    validation_summary: ValidationSummary,
    canonical_views: Mapping[str, pd.DataFrame],
) -> dict[str, Path]:
    """Write non-row-level metadata for auditability and traceability."""

    resolved_output_dir = Path(output_dir).expanduser().resolve()
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    validation_report_path = resolved_output_dir / VALIDATION_REPORT_FILENAME
    source_mapping_path = resolved_output_dir / SOURCE_MAPPING_FILENAME

    _write_json(
        validation_report_path,
        _validation_summary_to_dict(validation_summary),
    )
    _write_json(
        source_mapping_path,
        _canonical_mapping_to_dict(canonical_views),
    )

    return {
        "validation_report": validation_report_path,
        "source_to_canonical_mapping": source_mapping_path,
    }


def format_pipeline_result(result: Build01PipelineResult) -> str:
    """Return a concise human-readable pipeline summary."""

    lines = [
        "Build 01 pipeline completed.",
        format_validation_summary(result.validation_summary),
        "Canonical views: "
        + ", ".join(
            f"{view_name}={len(result.canonical_views[view_name])}"
            for view_name in CANONICAL_VIEW_ORDER
        ),
    ]
    if result.output_paths:
        lines.append("Outputs written: " + ", ".join(sorted(result.output_paths)))
    return "\n".join(lines)


def _validation_summary_to_dict(summary: ValidationSummary) -> dict[str, object]:
    source_files = None
    if summary.source_files is not None:
        source_files = {
            "available_files": list(summary.source_files.available_files),
            "missing_files": list(summary.source_files.missing_files),
            "unapproved_csv_files": list(summary.source_files.unapproved_csv_files),
            "is_valid": summary.source_files.is_valid,
        }

    return {
        "is_valid": summary.is_valid,
        "source_files": source_files,
        "datasets": {
            dataset_name: {
                "row_count": report.row_count,
                "is_valid": report.is_valid,
                "issues": [
                    {
                        "check": issue.check,
                        "column": issue.column,
                        "message": issue.message,
                        "sample_values": list(issue.sample_values),
                    }
                    for issue in report.issues
                ],
            }
            for dataset_name, report in summary.dataset_reports.items()
        },
    }


def _canonical_mapping_to_dict(
    canonical_views: Mapping[str, pd.DataFrame],
) -> dict[str, object]:
    return {
        "canonical_views": {
            view_name: {
                "source_datasets": list(CANONICAL_VIEW_SOURCES.get(view_name, ())),
                "row_count": len(canonical_views[view_name]),
                "columns": list(canonical_views[view_name].columns),
            }
            for view_name in CANONICAL_VIEW_ORDER
        }
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    print(format_pipeline_result(run_build01_pipeline()))

