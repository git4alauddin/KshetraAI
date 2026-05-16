"""Build 01 foundation views for future contextual decision generation.

This module intentionally does not create recommendations or advisory logic.
It only exposes canonical data views that later builds can consume.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from backend.data.joins.entity_joiner import build_canonical_views


CONTEXT_FOUNDATION_VIEW_NAMES = (
    "representatives",
    "territories",
    "growers",
    "visit_entities",
    "retailer_visit_log_clean",
    "campaign_engagement_clean",
)


def build_context_foundation_views(
    normalized_datasets: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Return canonical views needed by future contextual decision work."""

    canonical_views = build_canonical_views(normalized_datasets)
    return {
        view_name: canonical_views[view_name]
        for view_name in CONTEXT_FOUNDATION_VIEW_NAMES
    }

