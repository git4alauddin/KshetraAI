"""Priority scoring orchestration for Build 03.

This module connects Build 02 feature rows to weighted priority scores. It does
not classify levels, rank entities, generate recommendations, detect anomalies,
or implement API/frontend behavior.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from backend.engines.component_scorers import (
    ENTITY_CONTEXT_COLUMNS,
    load_priority_weight_config,
    score_all_components,
)
from backend.engines.priority_classifier import add_priority_classification
from backend.engines.ranking_engine import rank_priority_scores
from backend.engines.scoring_engine import (
    PriorityScore,
    calculate_priority_score,
    priority_score_as_row,
)


def score_priority_row(
    feature_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> PriorityScore:
    """Generate a final priority score for one normalized feature row."""

    weight_config = config or load_priority_weight_config()
    component_scores = score_all_components(feature_row, weight_config)
    return calculate_priority_score(component_scores, weight_config)


def build_priority_score_view(
    feature_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build stable entity-level final priority scores from feature view rows."""

    weight_config = config or load_priority_weight_config()
    rows: list[dict[str, Any]] = []

    for row in feature_view.to_dict(orient="records"):
        priority_score = score_priority_row(row, weight_config)
        output_row = {
            column: row.get(column, "")
            for column in ENTITY_CONTEXT_COLUMNS
            if column in feature_view.columns
        }
        output_row.update(priority_score.component_scores)
        output_row.update(priority_score_as_row(priority_score))
        rows.append(output_row)

    output = pd.DataFrame(rows)
    if output.empty:
        return output

    if "entity_id" in output.columns:
        output = output.sort_values("entity_id", kind="mergesort")
    return output.reset_index(drop=True)


def build_ranked_priority_view(
    feature_view: pd.DataFrame,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build scored, classified, and ranked priority outputs."""

    priority_scores = build_priority_score_view(feature_view, config)
    classified_scores = add_priority_classification(priority_scores)
    return rank_priority_scores(classified_scores)
