"""Feature registry metadata for KshetraAI Build 02.

The registry defines feature names, source dependencies, valid ranges, and
explainability meaning. It intentionally does not calculate feature values,
priority scores, recommendations, alerts, or explanation text.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


DEFAULT_SCORE_RANGE = (0, 100)


@dataclass(frozen=True)
class FeatureSpec:
    """Declarative metadata for one normalized feature."""

    feature_name: str
    category: str
    source_tables: tuple[str, ...]
    generation_logic: str
    normalization_strategy: str
    valid_range: tuple[int, int] = DEFAULT_SCORE_RANGE
    explainability_category: str = ""
    threshold_config_key: str | None = None
    aliases: tuple[str, ...] = ()


FEATURE_REGISTRY: tuple[FeatureSpec, ...] = (
    FeatureSpec(
        feature_name="weather_risk_score",
        category="agronomic",
        source_tables=("weather_signals", "crop_context"),
        generation_logic=(
            "Estimate weather-driven agronomic risk from recent rainfall, "
            "humidity, temperature, and crop-stage vulnerability signals."
        ),
        normalization_strategy="Clamp deterministic heuristic output to 0-100.",
        explainability_category="Agronomic urgency",
        threshold_config_key="weather_risk_score",
    ),
    FeatureSpec(
        feature_name="pest_disease_risk_score",
        category="agronomic",
        source_tables=("pest_signals", "crop_context"),
        generation_logic=(
            "Represent pest or disease pressure using public or controlled "
            "alert signals and crop vulnerability context."
        ),
        normalization_strategy="Map alert severity and crop vulnerability to 0-100.",
        explainability_category="Agronomic urgency",
        threshold_config_key="pest_disease_risk_score",
        aliases=("pest_risk_score",),
    ),
    FeatureSpec(
        feature_name="crop_stage_risk_score",
        category="agronomic",
        source_tables=("crop_context",),
        generation_logic=(
            "Represent biological stage vulnerability for the active crop "
            "or campaign context."
        ),
        normalization_strategy="Map configured crop-stage risk bands to 0-100.",
        explainability_category="Agronomic urgency",
        threshold_config_key="crop_stage_risk_score",
    ),
    FeatureSpec(
        feature_name="ndvi_stress_score",
        category="agronomic",
        source_tables=("ndvi_signals",),
        generation_logic="Represent crop stress from NDVI deviation signals.",
        normalization_strategy="Scale NDVI drop or stress level into 0-100.",
        explainability_category="Agronomic urgency",
        threshold_config_key="ndvi_stress_score",
    ),
    FeatureSpec(
        feature_name="historical_sales_score",
        category="sales",
        source_tables=("retailer_pos_clean",),
        generation_logic=(
            "Represent historical commercial strength using retailer POS "
            "transaction volume and value."
        ),
        normalization_strategy="Normalize relative sales strength to 0-100.",
        explainability_category="Commercial opportunity",
        threshold_config_key="historical_sales_score",
    ),
    FeatureSpec(
        feature_name="seasonal_product_relevance",
        category="sales",
        source_tables=("retailer_pos_clean", "crop_context", "campaign_engagement_clean"),
        generation_logic=(
            "Represent whether products align with crop, season, and campaign "
            "timing."
        ),
        normalization_strategy="Map product-season fit to 0-100.",
        explainability_category="Commercial opportunity",
        threshold_config_key="seasonal_product_relevance",
    ),
    FeatureSpec(
        feature_name="purchase_history_score",
        category="sales",
        source_tables=("retailer_pos_clean",),
        generation_logic=(
            "Represent likelihood of purchase based on prior retailer SKU "
            "transactions."
        ),
        normalization_strategy="Normalize purchase recency and frequency to 0-100.",
        explainability_category="Commercial opportunity",
        threshold_config_key="purchase_history_score",
    ),
    FeatureSpec(
        feature_name="crop_acreage_score",
        category="sales",
        source_tables=("growers", "crop_context"),
        generation_logic="Represent commercial scale from grower farm-size context.",
        normalization_strategy="Scale acreage or acreage proxy to 0-100.",
        explainability_category="Commercial opportunity",
        threshold_config_key="crop_acreage_score",
    ),
    FeatureSpec(
        feature_name="sales_opportunity_score",
        category="sales",
        source_tables=("retailer_pos_clean", "campaign_engagement_clean"),
        generation_logic=(
            "Represent commercial opportunity using demand momentum, product "
            "fit, purchase history, and campaign signals."
        ),
        normalization_strategy="Combine configured sales feature components into 0-100.",
        explainability_category="Commercial opportunity",
        threshold_config_key="sales_opportunity_score",
    ),
    FeatureSpec(
        feature_name="stock_level_score",
        category="inventory",
        source_tables=("retailer_inventory_weekly_clean",),
        generation_logic="Represent low-stock urgency from current SKU quantity.",
        normalization_strategy="Invert normalized stock quantity into 0-100 urgency.",
        explainability_category="Inventory need",
        threshold_config_key="stock_level_score",
    ),
    FeatureSpec(
        feature_name="sales_velocity_score",
        category="inventory",
        source_tables=("retailer_pos_clean",),
        generation_logic="Represent recent sales movement for retailer SKUs.",
        normalization_strategy="Normalize recent sales velocity to 0-100.",
        explainability_category="Inventory need",
        threshold_config_key="sales_velocity_score",
    ),
    FeatureSpec(
        feature_name="stockout_risk_score",
        category="inventory",
        source_tables=("retailer_inventory_weekly_clean", "retailer_pos_clean"),
        generation_logic=(
            "Represent stockout risk from low inventory and recent sales "
            "velocity."
        ),
        normalization_strategy="Combine stock level and sales velocity into 0-100.",
        explainability_category="Inventory need",
        threshold_config_key="stockout_risk_score",
    ),
    FeatureSpec(
        feature_name="inventory_need_score",
        category="inventory",
        source_tables=("retailer_inventory_weekly_clean", "retailer_pos_clean"),
        generation_logic=(
            "Represent replenishment urgency from stock level, stockout risk, "
            "and sales movement."
        ),
        normalization_strategy="Combine inventory feature components into 0-100.",
        explainability_category="Inventory need",
        threshold_config_key="inventory_need_score",
    ),
    FeatureSpec(
        feature_name="relationship_need_score",
        category="relationship",
        source_tables=("retailer_visit_log_clean", "visit_entities"),
        generation_logic=(
            "Represent engagement need from visit freshness and coverage gaps."
        ),
        normalization_strategy="Scale days since visit and coverage gap to 0-100.",
        explainability_category="Relationship need",
        threshold_config_key="relationship_need_score",
        aliases=("relationship_gap_score",),
    ),
    FeatureSpec(
        feature_name="competitive_pressure_score",
        category="competitive",
        source_tables=("competitor_signals", "retailer_pos_clean"),
        generation_logic=(
            "Represent competitive pressure using public, proxy, or controlled "
            "competitor signals plus sales decline context."
        ),
        normalization_strategy="Map configured competitive pressure signals to 0-100.",
        explainability_category="Competitive pressure",
        threshold_config_key="competitive_pressure_score",
    ),
    FeatureSpec(
        feature_name="account_priority_score",
        category="relationship",
        source_tables=("visit_entities", "retailer_pos_clean", "growers"),
        generation_logic=(
            "Represent strategic account importance from available retailer "
            "and grower context."
        ),
        normalization_strategy="Normalize account importance proxies to 0-100.",
        explainability_category="Account importance",
        threshold_config_key="account_priority_score",
    ),
    FeatureSpec(
        feature_name="campaign_engagement_score",
        category="relationship",
        source_tables=("campaign_engagement_clean",),
        generation_logic=(
            "Represent engagement quality from WhatsApp delivery/open/click "
            "signals and digital funnel responsiveness."
        ),
        normalization_strategy="Normalize campaign engagement outcomes to 0-100.",
        explainability_category="Engagement quality",
        threshold_config_key="campaign_engagement_score",
    ),
    FeatureSpec(
        feature_name="travel_cost_score",
        category="travel",
        source_tables=("travel_signals", "visit_entities"),
        generation_logic=(
            "Represent travel burden using distance, estimated route time, "
            "and visit clustering proxies."
        ),
        normalization_strategy="Map route burden to 0-100 where higher means costlier.",
        explainability_category="Travel feasibility",
        threshold_config_key="travel_cost_score",
        aliases=("travel_feasibility_score",),
    ),
)

FEATURES_BY_NAME: Mapping[str, FeatureSpec] = MappingProxyType(
    {feature.feature_name: feature for feature in FEATURE_REGISTRY}
)

FEATURE_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        alias: feature.feature_name
        for feature in FEATURE_REGISTRY
        for alias in feature.aliases
    }
)


def list_feature_names() -> tuple[str, ...]:
    """Return canonical feature names in stable registry order."""

    return tuple(feature.feature_name for feature in FEATURE_REGISTRY)


def list_feature_categories() -> tuple[str, ...]:
    """Return feature categories in stable alphabetical order."""

    return tuple(sorted({feature.category for feature in FEATURE_REGISTRY}))


def get_feature_spec(feature_name: str) -> FeatureSpec:
    """Return registry metadata for a canonical feature name or known alias."""

    canonical_name = FEATURE_ALIASES.get(feature_name, feature_name)
    try:
        return FEATURES_BY_NAME[canonical_name]
    except KeyError as exc:
        known = ", ".join(sorted(FEATURES_BY_NAME))
        raise KeyError(f"Unknown feature '{feature_name}'. Known: {known}") from exc


def get_features_by_category(category: str) -> tuple[FeatureSpec, ...]:
    """Return all features for a category in stable registry order."""

    return tuple(feature for feature in FEATURE_REGISTRY if feature.category == category)


def feature_registry_rows() -> tuple[dict[str, object], ...]:
    """Return registry metadata as rows for future CSV/DataFrame output."""

    return tuple(
        {
            "feature_name": feature.feature_name,
            "category": feature.category,
            "source_tables": "|".join(feature.source_tables),
            "generation_logic": feature.generation_logic,
            "normalization_strategy": feature.normalization_strategy,
            "valid_range_min": feature.valid_range[0],
            "valid_range_max": feature.valid_range[1],
            "explainability_category": feature.explainability_category,
            "threshold_config_key": feature.threshold_config_key or "",
            "aliases": "|".join(feature.aliases),
        }
        for feature in FEATURE_REGISTRY
    )


def validate_feature_registry() -> tuple[str, ...]:
    """Return registry consistency errors without raising."""

    errors: list[str] = []
    names = list_feature_names()

    if len(names) != len(set(names)):
        errors.append("Feature names must be unique.")

    for feature in FEATURE_REGISTRY:
        min_score, max_score = feature.valid_range
        if min_score != DEFAULT_SCORE_RANGE[0] or max_score != DEFAULT_SCORE_RANGE[1]:
            errors.append(f"{feature.feature_name}: valid range must be 0-100.")
        if not feature.source_tables:
            errors.append(f"{feature.feature_name}: source_tables cannot be empty.")
        if not feature.generation_logic.strip():
            errors.append(f"{feature.feature_name}: generation_logic cannot be empty.")
        if not feature.normalization_strategy.strip():
            errors.append(
                f"{feature.feature_name}: normalization_strategy cannot be empty."
            )
        if not feature.explainability_category.strip():
            errors.append(
                f"{feature.feature_name}: explainability_category cannot be empty."
            )
        if feature.threshold_config_key != feature.feature_name:
            errors.append(
                f"{feature.feature_name}: threshold_config_key should match feature_name."
            )

    return tuple(errors)


def assert_feature_registry_valid() -> None:
    """Raise when feature registry metadata is inconsistent."""

    errors = validate_feature_registry()
    if errors:
        raise ValueError("Invalid feature registry: " + "; ".join(errors))

