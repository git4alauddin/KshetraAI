"""Shared data-path utilities for the KshetraAI data pipeline."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT_MARKERS = (".git", "README.md")
DEFAULT_PRIVATE_DATA_DIR = "private-data"


def find_project_root(start_path: Path | None = None) -> Path:
    """Return the nearest parent directory that looks like the project root."""

    current = (start_path or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in PROJECT_ROOT_MARKERS):
            return candidate

    raise FileNotFoundError(
        f"Could not find project root from '{current}'. "
        f"Expected markers: {', '.join(PROJECT_ROOT_MARKERS)}"
    )


def resolve_private_data_dir(source_dir: str | Path | None = None) -> Path:
    """Resolve the private source data directory without creating it."""

    if source_dir is not None:
        return Path(source_dir).expanduser().resolve()

    return (find_project_root() / DEFAULT_PRIVATE_DATA_DIR).resolve()


def ensure_existing_directory(path: str | Path, label: str = "directory") -> Path:
    """Resolve a path and ensure it exists as a directory."""

    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Missing {label}: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Expected {label} to be a directory: {resolved}")
    return resolved


def ensure_child_path(parent: str | Path, child: str | Path) -> Path:
    """Resolve a child path and ensure it stays under the parent directory."""

    resolved_parent = Path(parent).expanduser().resolve()
    resolved_child = (resolved_parent / child).resolve()

    if resolved_child != resolved_parent and resolved_parent not in resolved_child.parents:
        raise ValueError(
            f"Resolved child path escapes parent directory: {resolved_child}"
        )

    return resolved_child

