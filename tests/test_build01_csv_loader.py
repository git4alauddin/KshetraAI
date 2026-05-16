import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.data.loaders.csv_loader import (
    CsvLoaderConfig,
    list_available_source_files,
    list_missing_source_files,
    list_unapproved_csv_files,
    load_source_dataset,
)


class Build01CsvLoaderTest(unittest.TestCase):
    def test_loader_only_lists_approved_schema_files(self):
        with tempfile.TemporaryDirectory() as source_dir:
            source_path = Path(source_dir)
            pd.DataFrame([{"rep_id": "REP001"}]).to_csv(
                source_path / "reps_territory.csv",
                index=False,
            )
            pd.DataFrame([{"x": 1}]).to_csv(
                source_path / "unexpected.csv",
                index=False,
            )
            (source_path / "__MACOSX").mkdir()

            config = CsvLoaderConfig(source_dir=source_path)

            self.assertEqual(list_available_source_files(config), ("reps_territory.csv",))
            self.assertIn("retailers.csv", list_missing_source_files(config))
            self.assertEqual(list_unapproved_csv_files(config), ("unexpected.csv",))

    def test_load_source_dataset_uses_schema_name_and_preserves_raw_columns(self):
        with tempfile.TemporaryDirectory() as source_dir:
            source_path = Path(source_dir)
            pd.DataFrame(
                [
                    {
                        "rep_id": " REP001 ",
                        "territory_id": "T001",
                        "territory_name": "Territory One",
                        "state": "State One",
                        "district": "District One",
                        "tehsil_list": '["Tehsil One"]',
                    }
                ]
            ).to_csv(source_path / "reps_territory.csv", index=False)

            dataframe = load_source_dataset(
                "reps_territory",
                CsvLoaderConfig(source_dir=source_path),
            )

            self.assertEqual(
                list(dataframe.columns),
                [
                    "rep_id",
                    "territory_id",
                    "territory_name",
                    "state",
                    "district",
                    "tehsil_list",
                ],
            )
            self.assertEqual(dataframe.loc[0, "rep_id"], " REP001 ")


if __name__ == "__main__":
    unittest.main()

