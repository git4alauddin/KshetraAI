import unittest
from pathlib import Path

from backend.features.feature_registry import (
    DEFAULT_SCORE_RANGE,
    feature_registry_rows,
    get_feature_spec,
    get_features_by_category,
    list_feature_categories,
    list_feature_names,
    validate_feature_registry,
)


class Build02FeatureRegistryTest(unittest.TestCase):
    def test_registry_is_valid_and_uses_stable_feature_names(self):
        self.assertEqual(validate_feature_registry(), ())
        self.assertEqual(
            list_feature_names(),
            (
                "weather_risk_score",
                "pest_disease_risk_score",
                "crop_stage_risk_score",
                "ndvi_stress_score",
                "historical_sales_score",
                "seasonal_product_relevance",
                "purchase_history_score",
                "crop_acreage_score",
                "sales_opportunity_score",
                "stock_level_score",
                "sales_velocity_score",
                "stockout_risk_score",
                "inventory_need_score",
                "relationship_need_score",
                "competitive_pressure_score",
                "account_priority_score",
                "campaign_engagement_score",
                "travel_cost_score",
            ),
        )

    def test_feature_specs_have_required_contract_metadata(self):
        for row in feature_registry_rows():
            self.assertEqual(row["valid_range_min"], DEFAULT_SCORE_RANGE[0])
            self.assertEqual(row["valid_range_max"], DEFAULT_SCORE_RANGE[1])
            self.assertTrue(row["source_tables"])
            self.assertTrue(row["generation_logic"])
            self.assertTrue(row["normalization_strategy"])
            self.assertTrue(row["explainability_category"])
            self.assertEqual(row["threshold_config_key"], row["feature_name"])

    def test_aliases_resolve_to_architecture_canonical_names(self):
        self.assertEqual(
            get_feature_spec("pest_risk_score").feature_name,
            "pest_disease_risk_score",
        )
        self.assertEqual(
            get_feature_spec("relationship_gap_score").feature_name,
            "relationship_need_score",
        )
        self.assertEqual(
            get_feature_spec("travel_feasibility_score").feature_name,
            "travel_cost_score",
        )

    def test_categories_and_threshold_config_cover_registry(self):
        self.assertEqual(
            list_feature_categories(),
            ("agronomic", "competitive", "inventory", "relationship", "sales", "travel"),
        )
        self.assertEqual(
            tuple(feature.feature_name for feature in get_features_by_category("inventory")),
            ("stock_level_score", "sales_velocity_score", "stockout_risk_score", "inventory_need_score"),
        )

        threshold_text = Path("backend/config/feature_thresholds.yaml").read_text(
            encoding="utf-8"
        )
        for feature_name in list_feature_names():
            self.assertIn(f"  {feature_name}:", threshold_text)


if __name__ == "__main__":
    unittest.main()
