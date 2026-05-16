"""Value normalization utilities for KshetraAI source datasets.

The normalizer converts validated raw DataFrames into stable value formats.
It does not join datasets, create canonical views, write outputs, or generate
any downstream intelligence signals.
"""

from __future__ import annotations

import json
import re
from typing import Mapping

import pandas as pd

from backend.data.schemas.dataset_schemas import (
    DatasetSchema,
    SOURCE_DATASET_SCHEMAS,
    get_source_schema,
)


TRUE_VALUES = frozenset({"true", "1", "yes"})
FALSE_VALUES = frozenset({"false", "0", "no"})
WHITESPACE_PATTERN = re.compile(r"\s+")


class ValueNormalizationError(ValueError):
    """Raised when a value cannot be normalized safely."""


def normalize_dataset(dataset_name: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize one source dataset by schema name."""

    schema = get_source_schema(dataset_name)
    return normalize_dataframe(schema, dataframe)


def normalize_dataframe(schema: DatasetSchema, dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a normalized copy of a source DataFrame."""

    _ensure_required_columns(schema, dataframe)

    normalized = dataframe.loc[:, list(schema.required_columns)].copy()

    for column in schema.id_columns:
        normalized[column] = _normalize_text_series(normalized[column])

    for column in schema.categorical_columns:
        normalized[column] = _normalize_text_series(normalized[column]).str.lower()

    for column in schema.boolean_columns:
        normalized[column] = _normalize_boolean_series(schema, column, normalized[column])

    for column in schema.date_columns:
        normalized[column] = _normalize_date_series(schema, column, normalized[column])

    for column in schema.datetime_columns:
        normalized[column] = _normalize_datetime_series(
            schema,
            column,
            normalized[column],
        )

    for column in schema.json_columns:
        normalized[column] = normalized[column].map(
            lambda value: _normalize_json_value(schema, column, value)
        ).astype("string")

    for column in _numeric_columns(schema):
        normalized[column] = pd.to_numeric(normalized[column], errors="raise")

    return normalized.loc[:, list(schema.required_columns)]


def normalize_all_datasets(
    datasets: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Normalize all expected source datasets in stable schema order."""

    return {
        schema.name: normalize_dataframe(schema, _require_dataset(schema.name, datasets))
        for schema in SOURCE_DATASET_SCHEMAS
    }


def normalize_id_value(value: object) -> str:
    """Normalize an ID-like value as a stripped string."""

    return _normalize_id_value(value)


def normalize_categorical_value(value: object) -> str:
    """Normalize a categorical label as compact lower-case text."""

    return _normalize_categorical_value(value)


def normalize_boolean_value(value: object) -> bool | pd.NA:
    """Normalize a common boolean-like value."""

    return _normalize_boolean_value(None, None, value)


def normalize_date_value(value: object) -> str | pd.NA:
    """Normalize a date-like value to ISO date text."""

    return _normalize_date_value(None, None, value)


def normalize_datetime_value(value: object) -> str | pd.NA:
    """Normalize a datetime-like value to ISO datetime text."""

    return _normalize_datetime_value(None, None, value)


def normalize_json_value(value: object) -> str | pd.NA:
    """Normalize a JSON string to deterministic compact JSON text."""

    return _normalize_json_value(None, None, value)


def _ensure_required_columns(schema: DatasetSchema, dataframe: pd.DataFrame) -> None:
    missing = [column for column in schema.required_columns if column not in dataframe.columns]
    if missing:
        raise ValueNormalizationError(
            f"{schema.name}: missing required columns for normalization: "
            + ", ".join(missing)
        )


def _numeric_columns(schema: DatasetSchema) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            (
                *schema.numeric_columns,
                *schema.non_negative_columns,
                *schema.positive_columns,
            )
        )
    )


def _normalize_id_value(value: object) -> str:
    if _is_blank(value):
        return ""
    return _collapse_whitespace(str(value).strip())


def _normalize_categorical_value(value: object) -> str:
    if _is_blank(value):
        return ""
    return _collapse_whitespace(str(value).strip()).casefold()


def _normalize_text_series(values: pd.Series) -> pd.Series:
    return (
        values.astype("string")
        .fillna("")
        .str.strip()
        .str.replace(WHITESPACE_PATTERN, " ", regex=True)
    )


def _normalize_boolean_series(
    schema: DatasetSchema,
    column: str,
    values: pd.Series,
) -> pd.Series:
    normalized = _normalize_text_series(values).str.lower()
    blank_values = normalized.eq("")

    if blank_values.any() and column not in schema.nullable_columns:
        raise ValueNormalizationError(_blank_error(schema, column, "boolean"))

    unsupported = normalized[
        ~blank_values & ~normalized.isin(TRUE_VALUES.union(FALSE_VALUES))
    ]
    if not unsupported.empty:
        raise ValueNormalizationError(
            _value_error(
                schema,
                column,
                unsupported.iloc[0],
                "unsupported boolean value",
            )
        )

    mapped = normalized.map(
        {**{value: True for value in TRUE_VALUES}, **{value: False for value in FALSE_VALUES}}
    )
    mapped = mapped.mask(blank_values, pd.NA)
    return mapped.astype("boolean")


def _normalize_date_series(
    schema: DatasetSchema,
    column: str,
    values: pd.Series,
) -> pd.Series:
    text_values = _normalize_text_series(values)
    blank_values = text_values.eq("")

    if blank_values.any() and column not in schema.nullable_columns:
        raise ValueNormalizationError(_blank_error(schema, column, "date"))

    parsed = pd.to_datetime(text_values.mask(blank_values, pd.NA), errors="coerce")
    invalid = text_values[~blank_values & parsed.isna()]
    if not invalid.empty:
        raise ValueNormalizationError(
            _value_error(schema, column, invalid.iloc[0], "invalid date")
        )

    normalized = parsed.dt.strftime("%Y-%m-%d").astype("string")
    return normalized.mask(blank_values, pd.NA)


def _normalize_datetime_series(
    schema: DatasetSchema,
    column: str,
    values: pd.Series,
) -> pd.Series:
    text_values = _normalize_text_series(values)
    blank_values = text_values.eq("")

    if blank_values.any() and column not in schema.nullable_columns:
        raise ValueNormalizationError(_blank_error(schema, column, "datetime"))

    parsed = pd.to_datetime(text_values.mask(blank_values, pd.NA), errors="coerce")
    invalid = text_values[~blank_values & parsed.isna()]
    if not invalid.empty:
        raise ValueNormalizationError(
            _value_error(schema, column, invalid.iloc[0], "invalid datetime")
        )

    normalized = parsed.dt.strftime("%Y-%m-%dT%H:%M:%S").astype("string")
    return normalized.mask(blank_values, pd.NA)


def _normalize_boolean_value(
    schema: DatasetSchema | None,
    column: str | None,
    value: object,
) -> bool | pd.NA:
    if _is_blank(value):
        if _is_nullable(schema, column):
            return pd.NA
        raise ValueNormalizationError(_blank_error(schema, column, "boolean"))

    normalized = str(value).strip().casefold()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False

    raise ValueNormalizationError(
        _value_error(schema, column, value, "unsupported boolean value")
    )


def _normalize_date_value(
    schema: DatasetSchema | None,
    column: str | None,
    value: object,
) -> str | pd.NA:
    if _is_blank(value):
        if _is_nullable(schema, column):
            return pd.NA
        raise ValueNormalizationError(_blank_error(schema, column, "date"))

    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise ValueNormalizationError(_value_error(schema, column, value, "invalid date"))
    return parsed.date().isoformat()


def _normalize_datetime_value(
    schema: DatasetSchema | None,
    column: str | None,
    value: object,
) -> str | pd.NA:
    if _is_blank(value):
        if _is_nullable(schema, column):
            return pd.NA
        raise ValueNormalizationError(_blank_error(schema, column, "datetime"))

    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise ValueNormalizationError(
            _value_error(schema, column, value, "invalid datetime")
        )
    return parsed.isoformat()


def _normalize_json_value(
    schema: DatasetSchema | None,
    column: str | None,
    value: object,
) -> str | pd.NA:
    if _is_blank(value):
        if _is_nullable(schema, column):
            return pd.NA
        raise ValueNormalizationError(_blank_error(schema, column, "JSON"))

    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError as exc:
        raise ValueNormalizationError(
            _value_error(schema, column, value, "invalid JSON")
        ) from exc

    return json.dumps(parsed, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _require_dataset(
    dataset_name: str,
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    try:
        return datasets[dataset_name]
    except KeyError as exc:
        raise ValueNormalizationError(
            f"Missing loaded dataset required for normalization: {dataset_name}"
        ) from exc


def _is_nullable(schema: DatasetSchema | None, column: str | None) -> bool:
    return bool(schema is not None and column in schema.nullable_columns)


def _is_blank(value: object) -> bool:
    return pd.isna(value) or str(value).strip() == ""


def _collapse_whitespace(value: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", value)


def _blank_error(
    schema: DatasetSchema | None,
    column: str | None,
    value_type: str,
) -> str:
    return _value_error(schema, column, "", f"blank {value_type} value")


def _value_error(
    schema: DatasetSchema | None,
    column: str | None,
    value: object,
    reason: str,
) -> str:
    location = ""
    if schema is not None and column is not None:
        location = f"{schema.name}.{column}: "
    elif column is not None:
        location = f"{column}: "
    return f"{location}{reason}: {value}"
