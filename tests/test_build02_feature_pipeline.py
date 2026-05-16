import tempfile
import unittest
from pathlib import Path

from backend.features.feature_pipeline import (
    FEATURE_OUTPUT_VIEW_ORDER,
    FeaturePipelineError,
    build_feature_output_views,
    write_feature_output_views,
)
from backend.features.feature_registry import list_feature_names
from backend.pipelines.build_context_view import build_contextual_feature_view
from backend.pipelines.build_priority_view import build_priority_feature_view

from tests.test_build02_agronomic_features import _sample_agronomic_datasets
from tests.test_build02_relationship_competitor_travel_features import (
    _sample_competitor_signals,
    _sample_travel_signals,
)
from tests.test_build02_sales_inventory_features import (
    _sample_growers,
    _sample_inventory,
    _sample_pos,
)


class Build02FeaturePipelineTest(unittest.TestCase):
    def test_feature_output_views_are_stable_bounded_and_canonical(self):
        datasets = _sample_pipeline_datasets()

        first = build_feature_output_views(datasets)
        second = build_feature_output_views(datasets)

        self.assertEqual(tuple(first), FEATURE_OUTPUT_VIEW_ORDER)
        self.assertTrue(first["priority_feature_view"].equals(second["priority_feature_view"]))
        self.assertTrue(first["contextual_feature_view"].equals(second["contextual_feature_view"]))
        self.assertTrue(first["anomaly_feature_view"].equals(second["anomaly_feature_view"]))
        self.assertIn("feature_name", first["feature_registry"].columns)

        priority = first["priority_feature_view"]
        self.assertEqual(priority["entity_id"].tolist(), ["E001", "E002", "G001", "G002", "R001", "R002"])
        self.assertIn("weather_risk_score", priority.columns)
        self.assertIn("inventory_need_score", priority.columns)
        self.assertIn("competitive_pressure_score", priority.columns)
        self.assertIn("travel_cost_score", priority.columns)
        for feature_name in list_feature_names():
            self.assertFalse(priority[feature_name].isna().any())
            self.assertTrue(priority[feature_name].between(0, 100).all())
        self.assertEqual(len(first["contextual_feature_view"]), len(priority))
        self.assertEqual(len(first["anomaly_feature_view"]), len(priority))

    def test_priority_and_context_pipeline_wrappers_return_expected_views(self):
        datasets = _sample_pipeline_datasets()

        priority = build_priority_feature_view(datasets)
        contextual = build_contextual_feature_view(datasets)

        self.assertIn("sales_opportunity_score", priority.columns)
        self.assertIn("inventory_need_score", contextual.columns)
        self.assertNotIn("stockout_risk_score", contextual.columns)

    def test_feature_outputs_can_be_written_to_temp_directory(self):
        with tempfile.TemporaryDirectory() as output_dir:
            feature_views = build_feature_output_views(_sample_pipeline_datasets())
            output_paths = write_feature_output_views(feature_views, output_dir)

            self.assertEqual(tuple(output_paths), FEATURE_OUTPUT_VIEW_ORDER)
            for view_name, output_path in output_paths.items():
                self.assertEqual(output_path, Path(output_dir).resolve() / f"{view_name}.csv")
                self.assertTrue(output_path.exists())

    def test_missing_feature_inputs_fail_explicitly(self):
        with self.assertRaises(FeaturePipelineError):
            build_feature_output_views({})


def _sample_pipeline_datasets():
    datasets = {}
    datasets.update(_sample_agronomic_datasets())
    datasets.update(
        {
            "retailer_pos_clean": _sample_pos(),
            "retailer_inventory_weekly_clean": _sample_inventory(),
            "campaign_engagement_clean": _sample_campaign_engagement(),
            "growers": _sample_growers(),
            "visit_entities": _sample_visit_entities(),
            "retailer_visit_log_clean": _sample_visit_log(),
            "competitor_signals": _sample_competitor_signals(),
            "travel_signals": _sample_travel_signals(),
        }
    )
    return datasets


def _sample_visit_entities():
    import pandas as pd

    return pd.DataFrame(
        [
            {"entity_id": "E001", "territory_id": "T001", "entity_type": "grower", "primary_crop": "wheat"},
            {"entity_id": "E002", "territory_id": "T001", "entity_type": "grower", "primary_crop": "wheat"},
            {"entity_id": "G001", "territory_id": "T001", "entity_type": "grower", "primary_crop": "wheat"},
            {"entity_id": "G002", "territory_id": "T002", "entity_type": "grower", "primary_crop": "mustard"},
            {"entity_id": "R001", "territory_id": "T001", "entity_type": "retailer", "primary_crop": ""},
            {"entity_id": "R002", "territory_id": "T002", "entity_type": "retailer", "primary_crop": ""},
        ]
    )


def _sample_visit_log():
    import pandas as pd

    return pd.DataFrame(
        [
            {"entity_id": "R001", "territory_id": "T001", "visit_date": "2026-01-12"},
            {"entity_id": "R002", "territory_id": "T002", "visit_date": "2026-01-01"},
        ]
    )


def _sample_campaign_engagement():
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "event_id": "WAM001",
                "event_type": "whatsapp_campaign",
                "campaign_product": "product a",
                "grower_id": "G001",
                "delivered_status": "true",
                "opened_status": "true",
                "clicked_status": "false",
            },
            {
                "event_id": "CMP001|2026-01-05",
                "event_type": "digital_funnel_weekly",
                "campaign_product": "product a",
                "social_post_impression": 100,
                "landing_page_visits": 20,
                "lead_form_submission": 4,
            },
        ]
    )


if __name__ == "__main__":
    unittest.main()
