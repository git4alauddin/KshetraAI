"""Build 01 foundation views for future priority feature generation.

This module intentionally does not compute priority features or scores. It
only exposes canonical data views that later builds can consume.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from backend.data.joins.entity_joiner import build_canonical_views
from backend.features.feature_pipeline import build_feature_output_views


PRIORITY_FOUNDATION_VIEW_NAMES = (
    "representatives",
    "territories",
    "retailers",
    "growers",
    "visit_entities",
    "retailer_pos_clean",
    "retailer_inventory_weekly_clean",
    "retailer_visit_log_clean",
)


def build_priority_foundation_views(
    normalized_datasets: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Return canonical views needed by future prioritization work."""

    canonical_views = build_canonical_views(normalized_datasets)
    return {
        view_name: canonical_views[view_name]
        for view_name in PRIORITY_FOUNDATION_VIEW_NAMES
    }


def build_priority_feature_view(
    processed_datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Return the Build 02 prioritization-ready feature view."""

    return build_feature_output_views(processed_datasets)["priority_feature_view"]
