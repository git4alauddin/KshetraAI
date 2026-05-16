import unittest

import pandas as pd

from backend.features.competitor_features import (
    COMPETITOR_FEATURE_COLUMNS,
    CompetitorFeatureError,
    build_competitor_feature_view,
)
from backend.features.relationship_features import (
    RELATIONSHIP_FEATURE_COLUMNS,
    RelationshipFeatureError,
    build_relationship_feature_view,
)
from backend.features.travel_features import (
    TRAVEL_FEATURE_COLUMNS,
    TravelFeatureError,
    build_travel_feature_view,
)


class Build02RelationshipCompetitorTravelFeaturesTest(unittest.TestCase):
    def test_relationship_feature_view_is_bounded_deterministic_and_canonical(self):
        datasets = {
            "retailer_visit_log_clean": _sample_visits(),
            "visit_entities": _sample_visit_entities(),
            "campaign_engagement_clean": _sample_campaign_engagement(),
        }

        first = build_relationship_feature_view(datasets)
        second = build_relationship_feature_view(datasets)

        self.assertTrue(first.equals(second))
        self.assertEqual(list(first.columns), ["entity_id", *RELATIONSHIP_FEATURE_COLUMNS])
        self.assertIn("R001", first["entity_id"].tolist())
        self.assertIn("G001", first["entity_id"].tolist())
        self.assertGreater(
            first.loc[first["entity_id"].eq("R002"), "relationship_need_score"].iloc[0],
            first.loc[first["entity_id"].eq("R001"), "relationship_need_score"].iloc[0],
        )
        for column in RELATIONSHIP_FEATURE_COLUMNS:
            self.assertTrue(first[column].between(0, 100).all())

    def test_competitor_feature_view_is_bounded_deterministic_and_canonical(self):
        datasets = {
            "competitor_signals": _sample_competitor_signals(),
            "retailer_pos_clean": _sample_pos(),
        }

        first = build_competitor_feature_view(datasets)
        second = build_competitor_feature_view(datasets)

        self.assertTrue(first.equals(second))
        self.assertEqual(list(first.columns), ["entity_id", *COMPETITOR_FEATURE_COLUMNS])
        self.assertEqual(first["entity_id"].tolist(), ["R001", "R002"])
        self.assertGreater(
            first.loc[first["entity_id"].eq("R001"), "competitive_pressure_score"].iloc[0],
            first.loc[first["entity_id"].eq("R002"), "competitive_pressure_score"].iloc[0],
        )
        self.assertTrue(first["competitive_pressure_score"].between(0, 100).all())

    def test_travel_feature_view_is_bounded_deterministic_and_canonical(self):
        datasets = {"travel_signals": _sample_travel_signals()}

        first = build_travel_feature_view(datasets)
        second = build_travel_feature_view(datasets)

        self.assertTrue(first.equals(second))
        self.assertEqual(list(first.columns), ["entity_id", *TRAVEL_FEATURE_COLUMNS])
        self.assertEqual(first["entity_id"].tolist(), ["R001", "R002"])
        self.assertGreater(
            first.loc[first["entity_id"].eq("R002"), "travel_cost_score"].iloc[0],
            first.loc[first["entity_id"].eq("R001"), "travel_cost_score"].iloc[0],
        )
        self.assertTrue(first["travel_cost_score"].between(0, 100).all())

    def test_missing_required_inputs_fail_explicitly(self):
        with self.assertRaises(RelationshipFeatureError):
            build_relationship_feature_view({})

        with self.assertRaises(CompetitorFeatureError):
            build_competitor_feature_view({})

        with self.assertRaises(TravelFeatureError):
            build_travel_feature_view({})

        with self.assertRaises(TravelFeatureError):
            build_travel_feature_view({"travel_signals": pd.DataFrame([{"entity_id": "R001"}])})


def _sample_visits():
    return pd.DataFrame(
        [
            {"entity_id": "R001", "territory_id": "T001", "visit_date": "2026-01-12"},
            {"entity_id": "R001", "territory_id": "T001", "visit_date": "2026-01-10"},
            {"entity_id": "R002", "territory_id": "T001", "visit_date": "2026-01-01"},
        ]
    )


def _sample_visit_entities():
    return pd.DataFrame(
        [
            {"entity_id": "R001", "entity_type": "retailer"},
            {"entity_id": "R002", "entity_type": "retailer"},
            {"entity_id": "G001", "entity_type": "grower"},
        ]
    )


def _sample_campaign_engagement():
    return pd.DataFrame(
        [
            {
                "event_id": "WAM001",
                "event_type": "whatsapp_campaign",
                "grower_id": "G001",
                "delivered_status": "true",
                "opened_status": "true",
                "clicked_status": "false",
            },
            {
                "event_id": "CMP001|2026-01-05",
                "event_type": "digital_funnel_weekly",
                "social_post_impression": 100,
                "landing_page_visits": 20,
                "lead_form_submission": 4,
            },
        ]
    )


def _sample_competitor_signals():
    return pd.DataFrame(
        [
            {
                "entity_id": "R001",
                "competitor_promotion_active": "true",
                "competitor_discount_level": "high",
                "competitor_availability_score": 80,
                "regional_sales_drop_score": 70,
            },
            {
                "entity_id": "R002",
                "competitor_promotion_active": "false",
                "competitor_discount_level": "low",
                "competitor_availability_score": 30,
                "regional_sales_drop_score": 5,
            },
        ]
    )


def _sample_pos():
    return pd.DataFrame(
        [
            {"retailer_id": "R001", "sku_qty": 1, "transaction_date": "2026-01-12"},
            {"retailer_id": "R001", "sku_qty": 20, "transaction_date": "2025-11-01"},
            {"retailer_id": "R002", "sku_qty": 10, "transaction_date": "2026-01-12"},
            {"retailer_id": "R002", "sku_qty": 10, "transaction_date": "2025-11-01"},
        ]
    )


def _sample_travel_signals():
    return pd.DataFrame(
        [
            {
                "entity_id": "R001",
                "distance_km": 5,
                "estimated_route_time_min": 15,
                "nearby_cluster_count": 5,
                "route_efficiency_score": 85,
            },
            {
                "entity_id": "R002",
                "distance_km": 35,
                "estimated_route_time_min": 80,
                "nearby_cluster_count": 1,
                "route_efficiency_score": 20,
            },
        ]
    )


if __name__ == "__main__":
    unittest.main()

