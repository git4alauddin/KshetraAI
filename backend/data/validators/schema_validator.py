"""Schema validation utilities for KshetraAI source datasets.

The validator checks raw loaded DataFrames against schema metadata. It does
not normalize values, join datasets, write outputs, or implement downstream
intelligence behavior.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

from backend.data.loaders.csv_loader import (
    CsvLoaderConfig,
    list_available_source_files,
    list_missing_source_files,
    list_unapproved_csv_files,
)
from backend.data.schemas.dataset_schemas import (
    DatasetSchema,
    ForeignKeySpec,
    SOURCE_DATASET_SCHEMAS,
    get_source_schema,
)


VALIDATION_SAMPLE_LIMIT = 5
BOOLEAN_VALUES = frozenset({"true", "false", "1", "0", "yes", "no"})


@dataclass(frozen=True)
class ValidationIssue:
    """Single operationally understandable validation failure."""

    dataset: str
    check: str
    message: str
    column: str | None = None
    sample_values: tuple[str, ...] = ()


@dataclass(frozen=True)
class DatasetValidationReport:
    """Validation result for one source dataset."""

    dataset: str
    row_count: int
    issues: tuple[ValidationIssue, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.issues


@dataclass(frozen=True)
class SourceFileValidationReport:
    """Validation result for the expected private source file inventory."""

    available_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    unapproved_csv_files: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.missing_files


@dataclass(frozen=True)
class ValidationSummary:
    """Combined validation result across source files and datasets."""

    source_files: SourceFileValidationReport | None = None
    dataset_reports: Mapping[str, DatasetValidationReport] = field(
        default_factory=dict
    )

    @property
    def issues(self) -> tuple[ValidationIssue, ...]:
        collected: list[ValidationIssue] = []
        for report in self.dataset_reports.values():
            collected.extend(report.issues)
        return tuple(collected)

    @property
    def is_valid(self) -> bool:
        files_valid = self.source_files is None or self.source_files.is_valid
        return files_valid and not self.issues


class SchemaValidationError(ValueError):
    """Raised when schema validation fails."""


def validate_source_files(
    config: CsvLoaderConfig | None = None,
) -> SourceFileValidationReport:
    """Validate that required source CSV files are present."""

    return SourceFileValidationReport(
        available_files=list_available_source_files(config),
        missing_files=list_missing_source_files(config),
        unapproved_csv_files=list_unapproved_csv_files(config),
    )


def validate_dataset(
    dataset_name: str,
    dataframe: pd.DataFrame,
    *,
    all_datasets: Mapping[str, pd.DataFrame] | None = None,
) -> DatasetValidationReport:
    """Validate one loaded source dataset against its schema metadata."""

    schema = get_source_schema(dataset_name)
    return validate_dataframe(schema, dataframe, all_datasets=all_datasets)


def validate_dataframe(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
    *,
    all_datasets: Mapping[str, pd.DataFrame] | None = None,
) -> DatasetValidationReport:
    """Validate one DataFrame against a schema."""

    issues: list[ValidationIssue] = []
    columns = set(dataframe.columns)

    issues.extend(_validate_required_columns(schema, columns))
    if issues:
        return DatasetValidationReport(
            dataset=schema.name,
            row_count=len(dataframe),
            issues=tuple(issues),
        )

    issues.extend(_validate_key_presence(schema, dataframe))
    issues.extend(_validate_unique_columns(schema, dataframe))
    issues.extend(_validate_unique_column_groups(schema, dataframe))
    issues.extend(_validate_dates(schema, dataframe))
    issues.extend(_validate_json_columns(schema, dataframe))
    issues.extend(_validate_boolean_columns(schema, dataframe))
    issues.extend(_validate_numeric_columns(schema, dataframe))
    issues.extend(_validate_allowed_values(schema, dataframe))

    if all_datasets is not None:
        issues.extend(_validate_foreign_keys(schema, dataframe, all_datasets))

    return DatasetValidationReport(
        dataset=schema.name,
        row_count=len(dataframe),
        issues=tuple(issues),
    )


def validate_all_datasets(
    datasets: Mapping[str, pd.DataFrame],
    *,
    include_source_files: bool = False,
    source_config: CsvLoaderConfig | None = None,
) -> ValidationSummary:
    """Validate all expected source datasets in stable schema order."""

    reports = {
        schema.name: validate_dataframe(
            schema,
            _require_dataset(schema.name, datasets),
            all_datasets=datasets,
        )
        for schema in SOURCE_DATASET_SCHEMAS
    }

    source_files = validate_source_files(source_config) if include_source_files else None
    return ValidationSummary(
        source_files=source_files,
        dataset_reports=reports,
    )


def assert_valid_dataset(
    dataset_name: str,
    dataframe: pd.DataFrame,
    *,
    all_datasets: Mapping[str, pd.DataFrame] | None = None,
) -> DatasetValidationReport:
    """Validate one dataset and raise an explicit error when invalid."""

    report = validate_dataset(dataset_name, dataframe, all_datasets=all_datasets)
    if not report.is_valid:
        raise SchemaValidationError(format_dataset_report(report))
    return report


def assert_valid_all_datasets(
    datasets: Mapping[str, pd.DataFrame],
    *,
    include_source_files: bool = False,
    source_config: CsvLoaderConfig | None = None,
) -> ValidationSummary:
    """Validate all datasets and raise an explicit error when invalid."""

    summary = validate_all_datasets(
        datasets,
        include_source_files=include_source_files,
        source_config=source_config,
    )
    if not summary.is_valid:
        raise SchemaValidationError(format_validation_summary(summary))
    return summary


def format_dataset_report(report: DatasetValidationReport) -> str:
    """Format one validation report as an operational error message."""

    if report.is_valid:
        return f"{report.dataset}: validation passed ({report.row_count} rows)."

    lines = [f"{report.dataset}: validation failed ({report.row_count} rows)."]
    for issue in report.issues:
        lines.append(_format_issue(issue))
    return "\n".join(lines)


def format_validation_summary(summary: ValidationSummary) -> str:
    """Format a combined validation summary for logs or exceptions."""

    lines: list[str] = []

    if summary.source_files is not None:
        files = summary.source_files
        if files.missing_files:
            lines.append(
                "Missing source files: " + ", ".join(files.missing_files)
            )
        if files.unapproved_csv_files:
            lines.append(
                "Unapproved CSV files ignored: "
                + ", ".join(files.unapproved_csv_files)
            )

    for report in summary.dataset_reports.values():
        if not report.is_valid:
            lines.append(format_dataset_report(report))

    return "\n".join(lines) if lines else "All source dataset validations passed."


def _validate_required_columns(
    schema: DatasetSchema,
    columns: set[str],
) -> tuple[ValidationIssue, ...]:
    missing = tuple(column for column in schema.required_columns if column not in columns)
    if not missing:
        return ()

    return (
        ValidationIssue(
            dataset=schema.name,
            check="required_columns",
            message="Missing required columns: " + ", ".join(missing),
            sample_values=missing,
        ),
    )


def _validate_key_presence(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for column in schema.id_columns:
        blank_count = _blank_mask(dataframe[column]).sum()
        if blank_count:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="key_presence",
                    column=column,
                    message=f"Key column '{column}' has {blank_count} blank values.",
                    sample_values=_sample_values(dataframe.loc[_blank_mask(dataframe[column]), column]),
                )
            )
    return tuple(issues)


def _validate_unique_columns(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for column in schema.unique_columns:
        normalized = _as_clean_string(dataframe[column])
        duplicates = normalized[~_blank_mask(normalized) & normalized.duplicated(keep=False)]
        if not duplicates.empty:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="unique_column",
                    column=column,
                    message=f"Column '{column}' contains duplicate key values.",
                    sample_values=_sample_values(duplicates),
                )
            )
    return tuple(issues)


def _validate_unique_column_groups(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for columns in schema.unique_column_groups:
        duplicate_rows = dataframe[dataframe.duplicated(subset=list(columns), keep=False)]
        if not duplicate_rows.empty:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="unique_column_group",
                    message=(
                        "Column group contains duplicate key values: "
                        + ", ".join(columns)
                    ),
                    sample_values=_sample_group_values(duplicate_rows, columns),
                )
            )
    return tuple(issues)


def _validate_dates(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for column in (*schema.date_columns, *schema.datetime_columns):
        values = dataframe[column]
        blank_values = _blank_mask(values)
        if column not in schema.nullable_columns and blank_values.any():
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="date_presence",
                    column=column,
                    message=f"Date column '{column}' has {blank_values.sum()} blank values.",
                    sample_values=_sample_values(values[blank_values]),
                )
            )

        populated = values[~blank_values]
        invalid = populated[pd.to_datetime(populated, errors="coerce").isna()]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="date_parse",
                    column=column,
                    message=f"Date column '{column}' contains unparsable values.",
                    sample_values=_sample_values(invalid),
                )
            )
    return tuple(issues)


def _validate_json_columns(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for column in schema.json_columns:
        invalid_values: list[str] = []
        for value in dataframe[column]:
            if _is_blank(value):
                if column not in schema.nullable_columns:
                    invalid_values.append(str(value))
                continue
            try:
                json.loads(str(value))
            except json.JSONDecodeError:
                invalid_values.append(str(value))
            if len(invalid_values) >= VALIDATION_SAMPLE_LIMIT:
                break

        if invalid_values:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="json_parse",
                    column=column,
                    message=f"JSON column '{column}' contains invalid JSON values.",
                    sample_values=tuple(invalid_values[:VALIDATION_SAMPLE_LIMIT]),
                )
            )
    return tuple(issues)


def _validate_boolean_columns(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for column in schema.boolean_columns:
        values = _as_clean_string(dataframe[column])
        invalid = values[
            ~_blank_mask(values)
            & ~values.str.casefold().isin(BOOLEAN_VALUES)
        ]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="boolean_values",
                    column=column,
                    message=f"Boolean column '{column}' contains unsupported values.",
                    sample_values=_sample_values(invalid),
                )
            )
    return tuple(issues)


def _validate_numeric_columns(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    constrained_columns = set(schema.numeric_columns).union(
        schema.non_negative_columns,
        schema.positive_columns,
    )

    for column in tuple(constrained_columns):
        values = dataframe[column]
        blank_values = _blank_mask(values)
        populated = values[~blank_values]
        numeric = pd.to_numeric(populated, errors="coerce")
        invalid = populated[numeric.isna()]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="numeric_parse",
                    column=column,
                    message=f"Numeric column '{column}' contains non-numeric values.",
                    sample_values=_sample_values(invalid),
                )
            )
            continue

        if column in schema.non_negative_columns:
            negative = populated[numeric < 0]
            if not negative.empty:
                issues.append(
                    ValidationIssue(
                        dataset=schema.name,
                        check="non_negative",
                        column=column,
                        message=f"Numeric column '{column}' contains negative values.",
                        sample_values=_sample_values(negative),
                    )
                )

        if column in schema.positive_columns:
            non_positive = populated[numeric <= 0]
            if not non_positive.empty:
                issues.append(
                    ValidationIssue(
                        dataset=schema.name,
                        check="positive",
                        column=column,
                        message=f"Numeric column '{column}' contains non-positive values.",
                        sample_values=_sample_values(non_positive),
                    )
                )

    return tuple(issues)


def _validate_allowed_values(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for column, allowed_values in schema.allowed_values.items():
        allowed = {value.strip().casefold() for value in allowed_values}
        values = _as_clean_string(dataframe[column])
        invalid = values[
            ~_blank_mask(values)
            & ~values.str.casefold().isin(allowed)
        ]
        if not invalid.empty:
            issues.append(
                ValidationIssue(
                    dataset=schema.name,
                    check="allowed_values",
                    column=column,
                    message=f"Column '{column}' contains values outside the allowed set.",
                    sample_values=_sample_values(invalid),
                )
            )
    return tuple(issues)


def _validate_foreign_keys(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
    all_datasets: Mapping[str, pd.DataFrame],
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for foreign_key in schema.foreign_keys:
        target_dataframe = all_datasets.get(foreign_key.target_dataset)
        if target_dataframe is None:
            if foreign_key.required:
                issues.append(
                    ValidationIssue(
                        dataset=schema.name,
                        check="foreign_key_target",
                        column=foreign_key.column,
                        message=(
                            "Missing target dataset for foreign key "
                            f"'{schema.name}.{foreign_key.column}' -> "
                            f"'{foreign_key.target_dataset}.{foreign_key.target_column}'."
                        ),
                    )
                )
            continue

        issues.extend(_validate_foreign_key(schema, dataframe, foreign_key, target_dataframe))

    return tuple(issues)


def _validate_foreign_key(
    schema: DatasetSchema,
    dataframe: pd.DataFrame,
    foreign_key: ForeignKeySpec,
    target_dataframe: pd.DataFrame,
) -> tuple[ValidationIssue, ...]:
    if foreign_key.target_column not in target_dataframe.columns:
        return (
            ValidationIssue(
                dataset=schema.name,
                check="foreign_key_target_column",
                column=foreign_key.column,
                message=(
                    "Missing target column for foreign key "
                    f"'{foreign_key.target_dataset}.{foreign_key.target_column}'."
                ),
            ),
        )

    source_values = _as_clean_string(dataframe[foreign_key.column])
    target_values = set(
        _as_clean_string(target_dataframe[foreign_key.target_column])
        .loc[lambda series: ~_blank_mask(series)]
        .tolist()
    )
    missing = source_values[
        ~_blank_mask(source_values) & ~source_values.isin(target_values)
    ]

    if missing.empty:
        return ()

    return (
        ValidationIssue(
            dataset=schema.name,
            check="foreign_key",
            column=foreign_key.column,
            message=(
                f"Column '{foreign_key.column}' contains values missing from "
                f"'{foreign_key.target_dataset}.{foreign_key.target_column}'."
            ),
            sample_values=_sample_values(missing),
        ),
    )


def _require_dataset(
    dataset_name: str,
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    try:
        return datasets[dataset_name]
    except KeyError as exc:
        raise SchemaValidationError(
            f"Missing loaded dataset required for validation: {dataset_name}"
        ) from exc


def _blank_mask(values: pd.Series) -> pd.Series:
    return _as_clean_string(values).eq("")


def _as_clean_string(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()


def _is_blank(value: object) -> bool:
    return pd.isna(value) or str(value).strip() == ""


def _sample_values(values: Iterable[object]) -> tuple[str, ...]:
    samples: list[str] = []
    for value in values:
        text = str(value)
        if text not in samples:
            samples.append(text)
        if len(samples) >= VALIDATION_SAMPLE_LIMIT:
            break
    return tuple(samples)


def _sample_group_values(
    dataframe: pd.DataFrame,
    columns: tuple[str, ...],
) -> tuple[str, ...]:
    samples: list[str] = []
    for _, row in dataframe.loc[:, list(columns)].head(VALIDATION_SAMPLE_LIMIT).iterrows():
        samples.append("|".join(str(row[column]) for column in columns))
    return tuple(samples)


def _format_issue(issue: ValidationIssue) -> str:
    column_text = f" [{issue.column}]" if issue.column else ""
    sample_text = (
        " Samples: " + ", ".join(issue.sample_values)
        if issue.sample_values
        else ""
    )
    return f"- {issue.check}{column_text}: {issue.message}{sample_text}"

