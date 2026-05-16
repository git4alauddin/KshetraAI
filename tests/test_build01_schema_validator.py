import unittest

import pandas as pd

from backend.data.validators.schema_validator import (
    format_dataset_report,
    validate_dataset,
)


class Build01SchemaValidatorTest(unittest.TestCase):
    def test_missing_required_column_is_reported_explicitly(self):
        report = validate_dataset(
            "retailers",
            pd.DataFrame(
                [
                    {
                        "retailer_id": "R001",
                        "state": "s1",
                        "district": "d1",
                        "tehsil": "t1",
                    }
                ]
            ),
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.issues[0].check, "required_columns")
        self.assertIn("territory_id", format_dataset_report(report))

    def test_duplicate_key_and_numeric_constraints_are_reported(self):
        report = validate_dataset(
            "retailer_pos",
            pd.DataFrame(
                [
                    {
                        "retailer_id": "R001",
                        "transaction_id": "TX001",
                        "sku_id": "SKU001",
                        "sku_name": "sku one",
                        "sku_qty": "0",
                        "sku_price": "10.5",
                        "transaction_date": "2026-01-09",
                    },
                    {
                        "retailer_id": "R001",
                        "transaction_id": "TX001",
                        "sku_id": "SKU001",
                        "sku_name": "sku one",
                        "sku_qty": "1",
                        "sku_price": "-4",
                        "transaction_date": "2026-01-10",
                    },
                ]
            ),
        )

        checks = {issue.check for issue in report.issues}
        self.assertIn("unique_column", checks)
        self.assertIn("positive", checks)

    def test_foreign_key_mismatch_is_reported(self):
        retailers = pd.DataFrame(
            [
                {
                    "retailer_id": "R001",
                    "territory_id": "UNKNOWN",
                    "state": "s1",
                    "district": "d1",
                    "tehsil": "t1",
                }
            ]
        )
        territories = pd.DataFrame(
            [
                {
                    "rep_id": "REP001",
                    "territory_id": "T001",
                    "territory_name": "territory one",
                    "state": "s1",
                    "district": "d1",
                    "tehsil_list": '["t1"]',
                }
            ]
        )

        report = validate_dataset(
            "retailers",
            retailers,
            all_datasets={"reps_territory": territories},
        )

        self.assertFalse(report.is_valid)
        self.assertEqual(report.issues[0].check, "foreign_key")


if __name__ == "__main__":
    unittest.main()

