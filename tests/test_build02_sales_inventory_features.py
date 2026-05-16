import unittest

import pandas as pd

from backend.features.inventory_features import (
    INVENTORY_FEATURE_COLUMNS,
    InventoryFeatureError,
    build_inventory_feature_view,
)
from backend.features.sales_features import (
    SALES_FEATURE_COLUMNS,
    SalesFeatureError,
    build_sales_feature_view,
)


class Build02SalesInventoryFeaturesTest(unittest.TestCase):
    def test_sales_feature_view_is_bounded_deterministic_and_canonical(self):
        datasets = {
            "retailer_pos_clean": _sample_pos(),
            "campaign_engagement_clean": _sample_campaigns(),
            "growers": _sample_growers(),
        }

        first = build_sales_feature_view(datasets)
        second = build_sales_feature_view(datasets)

        self.assertTrue(first.equals(second))
        self.assertEqual(list(first.columns), ["entity_id", *SALES_FEATURE_COLUMNS])
        self.assertEqual(first["entity_id"].tolist(), ["G001", "G002", "R001", "R002"])
        self.assertGreater(
            first.loc[first["entity_id"].eq("R001"), "sales_opportunity_score"].iloc[0],
            first.loc[first["entity_id"].eq("R002"), "sales_opportunity_score"].iloc[0],
        )
        for column in SALES_FEATURE_COLUMNS:
            self.assertTrue(first[column].between(0, 100).all())

    def test_inventory_feature_view_is_bounded_deterministic_and_canonical(self):
        datasets = {
            "retailer_inventory_weekly_clean": _sample_inventory(),
            "retailer_pos_clean": _sample_pos(),
        }

        first = build_inventory_feature_view(datasets)
        second = build_inventory_feature_view(datasets)

        self.assertTrue(first.equals(second))
        self.assertEqual(list(first.columns), ["entity_id", *INVENTORY_FEATURE_COLUMNS])
        self.assertEqual(first["entity_id"].tolist(), ["R001", "R002"])
        self.assertGreater(
            first.loc[first["entity_id"].eq("R001"), "inventory_need_score"].iloc[0],
            first.loc[first["entity_id"].eq("R002"), "inventory_need_score"].iloc[0],
        )
        for column in INVENTORY_FEATURE_COLUMNS:
            self.assertTrue(first[column].between(0, 100).all())

    def test_missing_required_inputs_fail_explicitly(self):
        with self.assertRaises(SalesFeatureError):
            build_sales_feature_view({})

        with self.assertRaises(InventoryFeatureError):
            build_inventory_feature_view({})

        with self.assertRaises(SalesFeatureError):
            build_sales_feature_view({"retailer_pos_clean": pd.DataFrame([{"retailer_id": "R001"}])})

        with self.assertRaises(InventoryFeatureError):
            build_inventory_feature_view(
                {"retailer_inventory_weekly_clean": pd.DataFrame([{"retailer_id": "R001"}])}
            )


def _sample_pos():
    return pd.DataFrame(
        [
            {
                "retailer_id": "R001",
                "transaction_id": "TX001",
                "sku_id": "SKU001",
                "sku_name": "product a",
                "sku_qty": 10,
                "sku_price": 10,
                "transaction_date": "2026-01-09",
            },
            {
                "retailer_id": "R001",
                "transaction_id": "TX002",
                "sku_id": "SKU001",
                "sku_name": "product a",
                "sku_qty": 8,
                "sku_price": 10,
                "transaction_date": "2026-01-12",
            },
            {
                "retailer_id": "R002",
                "transaction_id": "TX003",
                "sku_id": "SKU002",
                "sku_name": "other product",
                "sku_qty": 2,
                "sku_price": 8,
                "transaction_date": "2025-12-01",
            },
        ]
    )


def _sample_inventory():
    return pd.DataFrame(
        [
            {
                "retailer_id": "R001",
                "sku_id": "SKU001",
                "sku_name": "product a",
                "sku_qty": 2,
                "week_end_date": "2026-01-11",
            },
            {
                "retailer_id": "R002",
                "sku_id": "SKU002",
                "sku_name": "other product",
                "sku_qty": 25,
                "week_end_date": "2026-01-11",
            },
            {
                "retailer_id": "R001",
                "sku_id": "SKU001",
                "sku_name": "product a",
                "sku_qty": 20,
                "week_end_date": "2026-01-04",
            },
        ]
    )


def _sample_campaigns():
    return pd.DataFrame(
        [
            {
                "event_id": "CMP001|2026-01-05",
                "event_type": "digital_funnel_weekly",
                "campaign_product": "product a",
            }
        ]
    )


def _sample_growers():
    return pd.DataFrame(
        [
            {"grower_id": "G001", "grower_farm_size": 5},
            {"grower_id": "G002", "grower_farm_size": 1},
        ]
    )


if __name__ == "__main__":
    unittest.main()

