import unittest

import pandas as pd

from backend.data.normalizers.value_normalizer import (
    normalize_dataset,
    normalize_json_value,
)


class Build01ValueNormalizerTest(unittest.TestCase):
    def test_normalize_dataset_is_deterministic_and_does_not_mutate_raw_input(self):
        raw = pd.DataFrame(
            [
                {
                    "grower_id": " G001 ",
                    "state": " State One ",
                    "district": " District One ",
                    "tehsil": " Tehsil One ",
                    "language": " Hindi ",
                    "device_type": " Smartphone ",
                    "grower_age": "42",
                    "gender": " Male ",
                    "grower_crop_calendar": '{"crop":"wheat","stage":"tillering"}',
                    "product_scan": " YES ",
                    "product_name": " Product A ",
                    "product_scan_datetime": "2026-01-07 10:00:00",
                    "grower_farm_size": "3.5",
                    "offline_campaign_attended": " no ",
                    "campaign_attendance_date": "",
                }
            ]
        )
        raw_before = raw.copy(deep=True)

        first = normalize_dataset("growers", raw)
        second = normalize_dataset("growers", raw)

        self.assertTrue(first.equals(second))
        self.assertTrue(raw.equals(raw_before))
        self.assertEqual(first.loc[0, "grower_id"], "G001")
        self.assertEqual(first.loc[0, "state"], "state one")
        self.assertTrue(first.loc[0, "product_scan"])
        self.assertEqual(first.loc[0, "product_scan_datetime"], "2026-01-07T10:00:00")

    def test_json_normalization_is_compact_and_sorted(self):
        self.assertEqual(
            normalize_json_value('{"stage":"flowering","crop":"wheat"}'),
            '{"crop":"wheat","stage":"flowering"}',
        )


if __name__ == "__main__":
    unittest.main()

