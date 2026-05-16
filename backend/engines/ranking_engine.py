"""Deterministic ranking utilities for Build 03.

This module ranks already-scored priority rows. It does not calculate feature
scores, classify priority levels, generate recommendations, detect anomalies,
or create human-readable explanation text.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


DEFAULT_RANKING_RULES = (
    ("priority_score", False),
    ("agronomic_urgency", False),
    ("inventory_need", False),
    ("sales_opportunity", False),
    ("account_priority_score", False),
    ("travel_cost", True),
    ("entity_id", True),
)

REQUIRED_RANKING_COLUMNS = (
    "entity_id",
    "priority_score",
    "agronomic_urgency",
    "inventory_need",
    "sales_opportunity",
    "travel_cost",
)


class RankingEngineError(ValueError):
    """Raised when ranked visit list generation is invalid."""


def rank_priority_scores(
    priority_scores: pd.DataFrame,
    ranking_rules: Sequence[tuple[str, bool]] = DEFAULT_RANKING_RULES,
) -> pd.DataFrame:
    """Rank priority score rows using stable deterministic tie-breaking.

    The boolean in each ranking rule follows pandas sort semantics:
    ``True`` means ascending, ``False`` means descending.
    """

    _validate_rank_input(priority_scores, ranking_rules)
    if priority_scores.empty:
        return priority_scores.copy()

    ranked = priority_scores.copy()
    ranked = ranked.sort_values(
        by=[column for column, _ascending in ranking_rules if column in ranked.columns],
        ascending=[ascending for column, ascending in ranking_rules if column in ranked.columns],
        kind="mergesort",
    ).reset_index(drop=True)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    return ranked


def _validate_rank_input(
    priority_scores: pd.DataFrame,
    ranking_rules: Sequence[tuple[str, bool]],
) -> None:
    missing_required_columns = [
        column for column in REQUIRED_RANKING_COLUMNS if column not in priority_scores.columns
    ]
    if missing_required_columns:
        raise RankingEngineError(
            "Priority score view is missing required ranking columns: "
            + ", ".join(missing_required_columns)
        )

    missing_rule_columns = [
        column
        for column, _ascending in ranking_rules
        if column not in priority_scores.columns and column != "account_priority_score"
    ]
    if missing_rule_columns:
        raise RankingEngineError(
            "Priority score view is missing ranking rule columns: "
            + ", ".join(missing_rule_columns)
        )

    _validate_numeric_columns(
        priority_scores,
        [column for column in REQUIRED_RANKING_COLUMNS if column != "entity_id"],
    )

    if priority_scores["entity_id"].astype("string").fillna("").str.strip().eq("").any():
        raise RankingEngineError("Priority score view contains blank entity_id values.")


def _validate_numeric_columns(
    dataframe: pd.DataFrame,
    columns: Sequence[str],
) -> None:
    invalid_columns: list[str] = []
    for column in columns:
        values = pd.to_numeric(dataframe[column], errors="coerce")
        if values.isna().any():
            invalid_columns.append(column)

    if invalid_columns:
        raise RankingEngineError(
            "Ranking columns must be numeric: "
            + ", ".join(invalid_columns)
        )
