import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.pipelines.pipeline_runner import (
    Build01PipelineConfig,
    run_build01_pipeline,
)


class Build01PipelineRunnerTest(unittest.TestCase):
    def test_run_build01_pipeline_writes_canonical_outputs_and_metadata(self):
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as output_dir:
            _write_sample_sources(Path(source_dir))

            result = run_build01_pipeline(
                Build01PipelineConfig(source_dir=source_dir, output_dir=output_dir)
            )

            self.assertTrue(result.is_valid)
            self.assertEqual(result.canonical_views["visit_entities"].shape[0], 2)
            self.assertEqual(
                sorted(path.name for path in result.output_paths.values()),
                [
                    "campaign_engagement_clean.csv",
                    "growers.csv",
                    "representatives.csv",
                    "retailer_inventory_weekly_clean.csv",
                    "retailer_pos_clean.csv",
                    "retailer_visit_log_clean.csv",
                    "retailers.csv",
                    "territories.csv",
                    "visit_entities.csv",
                ],
            )
            self.assertIn("validation_report", result.metadata_paths)
            self.assertIn("source_to_canonical_mapping", result.metadata_paths)

            mapping = json.loads(
                result.metadata_paths["source_to_canonical_mapping"].read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                mapping["canonical_views"]["visit_entities"]["source_datasets"],
                ["retailers", "growers"],
            )

    def test_run_build01_pipeline_can_run_without_writing_outputs(self):
        with tempfile.TemporaryDirectory() as source_dir:
            _write_sample_sources(Path(source_dir))

            result = run_build01_pipeline(
                Build01PipelineConfig(source_dir=source_dir, write_outputs=False)
            )

            self.assertTrue(result.is_valid)
            self.assertEqual(result.output_paths, {})
            self.assertEqual(result.metadata_paths, {})


def _write_sample_sources(source_dir: Path):
    for filename, dataframe in _sample_source_frames().items():
        dataframe.to_csv(source_dir / filename, index=False, lineterminator="\n")


def _sample_source_frames():
    return {
        "reps_territory.csv": pd.DataFrame(
            [
                {
                    "rep_id": "REP001",
                    "territory_id": "T001",
                    "territory_name": "territory one",
                    "state": "s1",
                    "district": "d1",
                    "tehsil_list": '["tehsil one"]',
                }
            ]
        ),
        "retailers.csv": pd.DataFrame(
            [
                {
                    "retailer_id": "R001",
                    "territory_id": "T001",
                    "state": "s1",
                    "district": "d1",
                    "tehsil": "tehsil one",
                }
            ]
        ),
        "retailer_visit_log.csv": pd.DataFrame(
            [
                {
                    "rep_id": "REP001",
                    "visit_date": "2026-01-08",
                    "territory_id": "T001",
                    "visit_tehsil": "tehsil one",
                    "visit_type": "retailer meeting",
                    "product_recommended": "product a",
                }
            ]
        ),
        "retailer_inventory_weekly.csv": pd.DataFrame(
            [
                {
                    "retailer_id": "R001",
                    "sku_id": "SKU001",
                    "sku_name": "sku one",
                    "sku_qty": 4,
                    "week_end_date": "2026-01-11",
                }
            ]
        ),
        "retailer_pos.csv": pd.DataFrame(
            [
                {
                    "retailer_id": "R001",
                    "transaction_id": "TX001",
                    "sku_id": "SKU001",
                    "sku_name": "sku one",
                    "sku_qty": 1,
                    "sku_price": 10.5,
                    "transaction_date": "2026-01-09",
                }
            ]
        ),
        "growers.csv": pd.DataFrame(
            [
                {
                    "grower_id": "G001",
                    "state": "s1",
                    "district": "d1",
                    "tehsil": "tehsil one",
                    "language": "hindi",
                    "device_type": "smartphone",
                    "grower_age": 42,
                    "gender": "male",
                    "grower_crop_calendar": '{"crop":"wheat"}',
                    "product_scan": "true",
                    "product_name": "product a",
                    "product_scan_datetime": "2026-01-07T10:00:00",
                    "grower_farm_size": 3.5,
                    "offline_campaign_attended": "false",
                    "campaign_attendance_date": "",
                }
            ]
        ),
        "digital_funnel_weekly.csv": pd.DataFrame(
            [
                {
                    "campaign_id": "CMP001",
                    "week_start_date": "2026-01-05",
                    "social_post_impression": 100,
                    "landing_page_visits": 40,
                    "lead_form_submission": 8,
                    "campaign_crop": "wheat",
                    "campaign_product": "product a",
                }
            ]
        ),
        "whatsapp_campaign.csv": pd.DataFrame(
            [
                {
                    "id": "WAM001",
                    "campaign_product": "product a",
                    "campaign_crop": "wheat",
                    "grower_id": "G001",
                    "message_sent_date": "2026-01-06",
                    "delivered_status": "true",
                    "opened_status": "true",
                    "clicked_status": "false",
                }
            ]
        ),
    }

