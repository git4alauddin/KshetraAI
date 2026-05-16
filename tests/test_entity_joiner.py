import unittest

import pandas as pd

from backend.data.joins.entity_joiner import (
    build_campaign_engagement_clean,
    build_canonical_views,
)


class EntityJoinerTest(unittest.TestCase):
    def test_build_canonical_views_creates_stable_visit_entities(self):
        views = build_canonical_views(_sample_datasets())

        visit_entities = views["visit_entities"]

        self.assertEqual(
            list(views),
            [
                "representatives",
                "territories",
                "retailers",
                "growers",
                "visit_entities",
                "retailer_pos_clean",
                "retailer_inventory_weekly_clean",
                "retailer_visit_log_clean",
                "campaign_engagement_clean",
            ],
        )
        self.assertEqual(visit_entities["entity_id"].tolist(), ["G001", "R001"])
        self.assertEqual(visit_entities["entity_type"].tolist(), ["grower", "retailer"])
        self.assertEqual(visit_entities.loc[0, "territory_id"], "T001")
        self.assertEqual(visit_entities.loc[0, "primary_crop"], "wheat")

    def test_operational_views_attach_retailer_and_visit_context(self):
        views = build_canonical_views(_sample_datasets())

        pos = views["retailer_pos_clean"]
        inventory = views["retailer_inventory_weekly_clean"]
        visits = views["retailer_visit_log_clean"]

        self.assertEqual(pos.loc[0, "territory_id"], "T001")
        self.assertEqual(inventory.loc[0, "district"], "d1")
        self.assertEqual(visits.loc[0, "rep_territory_id"], "T001")
        self.assertEqual(visits.loc[0, "territory_name"], "territory one")

    def test_campaign_engagement_clean_unifies_funnel_and_whatsapp_events(self):
        datasets = _sample_datasets()
        engagement = build_campaign_engagement_clean(
            datasets["digital_funnel_weekly"],
            datasets["whatsapp_campaign"],
        )

        self.assertEqual(
            engagement["event_type"].tolist(),
            ["digital_funnel_weekly", "whatsapp_campaign"],
        )
        self.assertEqual(engagement.loc[0, "event_id"], "CMP001|2026-01-05")
        self.assertEqual(engagement.loc[1, "grower_id"], "G001")


def _sample_datasets():
    return {
        "reps_territory": pd.DataFrame(
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
        "retailers": pd.DataFrame(
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
        "retailer_visit_log": pd.DataFrame(
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
        "retailer_inventory_weekly": pd.DataFrame(
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
        "retailer_pos": pd.DataFrame(
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
        "growers": pd.DataFrame(
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
                    "product_scan": True,
                    "product_name": "product a",
                    "product_scan_datetime": "2026-01-07T10:00:00",
                    "grower_farm_size": 3.5,
                    "offline_campaign_attended": False,
                    "campaign_attendance_date": "",
                }
            ]
        ),
        "digital_funnel_weekly": pd.DataFrame(
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
        "whatsapp_campaign": pd.DataFrame(
            [
                {
                    "id": "WAM001",
                    "campaign_product": "product a",
                    "campaign_crop": "wheat",
                    "grower_id": "G001",
                    "message_sent_date": "2026-01-06",
                    "delivered_status": True,
                    "opened_status": True,
                    "clicked_status": False,
                }
            ]
        ),
    }
