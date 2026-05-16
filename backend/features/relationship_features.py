"""Deterministic relationship feature builders for Build 02.

These builders convert visit, entity, and campaign engagement context into
relationship-oriented feature scores. They do not rank entities, create
recommendations, detect anomalies, or generate explanation text.
"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd


RELATIONSHIP_FEATURE_COLUMNS = (
    "relationship_need_score",
    "account_priority_score",
    "campaign_engagement_score",
)


class RelationshipFeatureError(ValueError):
    """Raised when relationship feature generation cannot proceed safely."""


def build_relationship_need_features(
    retailer_visit_log_clean: pd.DataFrame,
) -> pd.DataFrame:
    """Generate engagement-gap features from latest visit activity."""

    _ensure_columns(
        "retailer_visit_log_clean",
        retailer_visit_log_clean,
        ("territory_id", "visit_date"),
    )
    visits = retailer_visit_log_clean.copy()
    visits["entity_id"] = _entity_from_visit_rows(visits)
    visits["visit_date"] = pd.to_datetime(visits["visit_date"], errors="coerce")

    grouped = (
        visits.groupby("entity_id", as_index=False)
        .agg(last_visit_date=("visit_date", "max"), visit_count=("visit_date", "count"))
        .sort_values("entity_id", kind="mergesort")
        .reset_index(drop=True)
    )
    max_date = grouped["last_visit_date"].max()
    days_since_last = (max_date - grouped["last_visit_date"]).dt.days.fillna(999)
    recency_gap_score = _clamp_score(days_since_last * 5)
    low_coverage_score = _clamp_score(100 - _relative_score(grouped["visit_count"]))
    grouped["relationship_need_score"] = _clamp_score(
        recency_gap_score * 0.70 + low_coverage_score * 0.30
    )

    return grouped.loc[:, ["entity_id", "relationship_need_score"]]


def build_account_priority_features(visit_entities: pd.DataFrame) -> pd.DataFrame:
    """Generate account importance features from entity context."""

    _ensure_columns("visit_entities", visit_entities, ("entity_id", "entity_type"))
    entities = visit_entities.copy()
    output = pd.DataFrame({"entity_id": _clean_text_series(entities["entity_id"])})

    if "account_importance" in entities.columns:
        output["account_priority_score"] = _clamp_score(_numeric_series(entities["account_importance"]))
    else:
        entity_type = _clean_text_series(entities["entity_type"]).str.lower()
        output["account_priority_score"] = entity_type.map(
            {"retailer": 70, "grower": 55, "distributor": 75}
        ).fillna(50).astype("Int64")

    return _stable_frame(output, sort_by=("entity_id",))


def build_campaign_engagement_features(
    campaign_engagement_clean: pd.DataFrame,
) -> pd.DataFrame:
    """Generate campaign engagement quality features."""

    _ensure_columns("campaign_engagement_clean", campaign_engagement_clean, ("event_type",))
    engagement = campaign_engagement_clean.copy()

    whatsapp = engagement[
        _clean_text_series(engagement["event_type"]).str.lower().eq("whatsapp_campaign")
    ].copy()
    funnel = engagement[
        _clean_text_series(engagement["event_type"]).str.lower().eq("digital_funnel_weekly")
    ].copy()

    frames: list[pd.DataFrame] = []
    if not whatsapp.empty:
        _ensure_columns(
            "campaign_engagement_clean",
            whatsapp,
            ("grower_id", "delivered_status", "opened_status", "clicked_status"),
        )
        whatsapp["entity_id"] = _clean_text_series(whatsapp["grower_id"])
        whatsapp["engagement_points"] = (
            _boolean_series(whatsapp["delivered_status"]).astype(int) * 25
            + _boolean_series(whatsapp["opened_status"]).astype(int) * 35
            + _boolean_series(whatsapp["clicked_status"]).astype(int) * 40
        )
        frames.append(
            whatsapp.groupby("entity_id", as_index=False)
            .agg(campaign_engagement_score=("engagement_points", "mean"))
        )

    if not funnel.empty:
        _ensure_columns(
            "campaign_engagement_clean",
            funnel,
            ("event_id", "social_post_impression", "landing_page_visits", "lead_form_submission"),
        )
        funnel["entity_id"] = _clean_text_series(funnel["event_id"])
        impressions = _numeric_series(funnel["social_post_impression"])
        visits = _numeric_series(funnel["landing_page_visits"])
        leads = _numeric_series(funnel["lead_form_submission"])
        visit_rate = (visits / impressions.replace(0, pd.NA)).fillna(0)
        lead_rate = (leads / visits.replace(0, pd.NA)).fillna(0)
        funnel["campaign_engagement_score"] = _clamp_score(visit_rate * 50 + lead_rate * 50)
        frames.append(funnel.loc[:, ["entity_id", "campaign_engagement_score"]])

    if not frames:
        return pd.DataFrame(columns=["entity_id", "campaign_engagement_score"])

    combined = pd.concat(frames, ignore_index=True)
    grouped = (
        combined.groupby("entity_id", as_index=False)
        .agg(campaign_engagement_score=("campaign_engagement_score", "mean"))
        .sort_values("entity_id", kind="mergesort")
        .reset_index(drop=True)
    )
    grouped["campaign_engagement_score"] = _clamp_score(grouped["campaign_engagement_score"])
    return grouped


def build_relationship_feature_view(
    datasets: Mapping[str, pd.DataFrame],
) -> pd.DataFrame:
    """Build one entity-level relationship feature view."""

    if not any(
        key in datasets
        for key in ("retailer_visit_log_clean", "visit_entities", "campaign_engagement_clean")
    ):
        raise RelationshipFeatureError(
            "At least one relationship input is required: retailer_visit_log_clean, "
            "visit_entities, or campaign_engagement_clean."
        )

    feature_frames: list[pd.DataFrame] = []
    if "retailer_visit_log_clean" in datasets:
        feature_frames.append(build_relationship_need_features(datasets["retailer_visit_log_clean"]))
    if "visit_entities" in datasets:
        feature_frames.append(build_account_priority_features(datasets["visit_entities"]))
    if "campaign_engagement_clean" in datasets:
        feature_frames.append(build_campaign_engagement_features(datasets["campaign_engagement_clean"]))

    output = feature_frames[0]
    for frame in feature_frames[1:]:
        output = output.merge(frame, on="entity_id", how="outer")

    for column in RELATIONSHIP_FEATURE_COLUMNS:
        if column in output.columns:
            output[column] = output[column].fillna(0).astype("Int64")
        else:
            output[column] = pd.Series([0] * len(output), dtype="Int64")

    return _stable_frame(
        output.loc[:, ("entity_id", *RELATIONSHIP_FEATURE_COLUMNS)],
        sort_by=("entity_id",),
    )


def _entity_from_visit_rows(visits: pd.DataFrame) -> pd.Series:
    if "entity_id" in visits.columns:
        return _clean_text_series(visits["entity_id"])
    if "retailer_id" in visits.columns:
        return _clean_text_series(visits["retailer_id"])
    return _clean_text_series(visits["territory_id"])


def _relative_score(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    max_value = numeric.max()
    if pd.isna(max_value) or max_value <= 0:
        return pd.Series([0] * len(numeric), index=numeric.index, dtype="Int64")
    return _clamp_score((numeric / max_value) * 100)


def _boolean_series(values: pd.Series) -> pd.Series:
    return _clean_text_series(values).str.lower().isin(("true", "1", "yes"))


def _numeric_series(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0)


def _clamp_score(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").fillna(0).clip(0, 100).round().astype("Int64")


def _stable_frame(dataframe: pd.DataFrame, *, sort_by: tuple[str, ...]) -> pd.DataFrame:
    return dataframe.sort_values(list(sort_by), kind="mergesort").reset_index(drop=True)


def _ensure_columns(
    dataset_name: str,
    dataframe: pd.DataFrame,
    required_columns: tuple[str, ...],
) -> None:
    missing = tuple(column for column in required_columns if column not in dataframe.columns)
    if missing:
        raise RelationshipFeatureError(
            f"{dataset_name}: missing required columns: " + ", ".join(missing)
        )


def _clean_text_series(values: pd.Series) -> pd.Series:
    return values.astype("string").fillna("").str.strip()

