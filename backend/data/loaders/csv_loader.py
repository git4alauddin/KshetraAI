"""Schema-aware CSV loading for company-provided source datasets.

This module only loads approved source CSV files into raw pandas DataFrames.
It does not validate columns, normalize values, join tables, or write outputs.
Those responsibilities belong to later Build 01 tasks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import pandas as pd

from backend.data.schemas.dataset_schemas import (
    DatasetSchema,
    SOURCE_DATASET_SCHEMAS,
    SOURCE_DATASETS_BY_FILENAME,
    get_source_schema,
)
from backend.utils.data_utils import (
    ensure_child_path,
    ensure_existing_directory,
    resolve_private_data_dir,
)


class CsvLoaderError(RuntimeError):
    """Raised when source CSV loading cannot proceed safely."""


@dataclass(frozen=True)
class CsvLoaderConfig:
    """Configuration for reading approved source CSV files."""

    source_dir: Path | str | None = None
    encoding: str = "utf-8"
    dtype: str = "string"
    keep_default_na: bool = False


@dataclass(frozen=True)
class LoadedSourceDataset:
    """Loaded raw DataFrame with the schema and source path used."""

    schema: DatasetSchema
    path: Path
    dataframe: pd.DataFrame


def get_source_directory(config: CsvLoaderConfig | None = None) -> Path:
    """Return the resolved, existing private source directory."""

    loader_config = config or CsvLoaderConfig()
    source_dir = resolve_private_data_dir(loader_config.source_dir)
    return ensure_existing_directory(source_dir, "private data directory")


def list_available_source_files(
    config: CsvLoaderConfig | None = None,
) -> tuple[str, ...]:
    """List approved source CSV files present in the source directory."""

    source_dir = get_source_directory(config)
    available_files = {
        path.name
        for path in source_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".csv"
        and path.name in SOURCE_DATASETS_BY_FILENAME
    }
    return tuple(
        schema.filename
        for schema in SOURCE_DATASET_SCHEMAS
        if schema.filename in available_files
    )


def list_missing_source_files(
    config: CsvLoaderConfig | None = None,
) -> tuple[str, ...]:
    """List approved source CSV files expected by the schema but not present."""

    available_files = set(list_available_source_files(config))
    return tuple(
        schema.filename
        for schema in SOURCE_DATASET_SCHEMAS
        if schema.filename not in available_files
    )


def list_unapproved_csv_files(
    config: CsvLoaderConfig | None = None,
) -> tuple[str, ...]:
    """List CSV files in the source directory that are not in schema metadata."""

    source_dir = get_source_directory(config)
    return tuple(
        sorted(
            path.name
            for path in source_dir.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".csv"
            and path.name not in SOURCE_DATASETS_BY_FILENAME
        )
    )


def load_source_dataset(
    dataset_name: str,
    config: CsvLoaderConfig | None = None,
    *,
    nrows: int | None = None,
) -> pd.DataFrame:
    """Load one approved source dataset by schema name."""

    return load_source_dataset_with_metadata(
        dataset_name,
        config=config,
        nrows=nrows,
    ).dataframe


def load_source_dataset_with_metadata(
    dataset_name: str,
    config: CsvLoaderConfig | None = None,
    *,
    nrows: int | None = None,
) -> LoadedSourceDataset:
    """Load one approved source dataset and return source metadata with it."""

    schema = get_source_schema(dataset_name)
    loader_config = config or CsvLoaderConfig()
    source_dir = get_source_directory(loader_config)
    source_path = _resolve_schema_source_path(source_dir, schema)

    dataframe = pd.read_csv(
        source_path,
        encoding=loader_config.encoding,
        dtype=loader_config.dtype,
        keep_default_na=loader_config.keep_default_na,
        nrows=nrows,
    )

    return LoadedSourceDataset(
        schema=schema,
        path=source_path,
        dataframe=dataframe,
    )


def load_all_source_datasets(
    config: CsvLoaderConfig | None = None,
    *,
    nrows: int | None = None,
) -> dict[str, pd.DataFrame]:
    """Load all approved source datasets in stable schema order."""

    return {
        schema.name: load_source_dataset(schema.name, config=config, nrows=nrows)
        for schema in SOURCE_DATASET_SCHEMAS
    }


def load_all_source_datasets_with_metadata(
    config: CsvLoaderConfig | None = None,
    *,
    nrows: int | None = None,
) -> Mapping[str, LoadedSourceDataset]:
    """Load all approved source datasets with schema and path metadata."""

    return {
        schema.name: load_source_dataset_with_metadata(
            schema.name,
            config=config,
            nrows=nrows,
        )
        for schema in SOURCE_DATASET_SCHEMAS
    }


def _resolve_schema_source_path(source_dir: Path, schema: DatasetSchema) -> Path:
    source_path = ensure_child_path(source_dir, schema.filename)
    if not source_path.exists():
        raise FileNotFoundError(
            f"Missing source file for dataset '{schema.name}': {source_path}"
        )
    if not source_path.is_file():
        raise CsvLoaderError(
            f"Expected source path for dataset '{schema.name}' to be a file: "
            f"{source_path}"
        )
    if source_path.name not in SOURCE_DATASETS_BY_FILENAME:
        raise CsvLoaderError(f"Source file is not approved: {source_path.name}")
    return source_path

