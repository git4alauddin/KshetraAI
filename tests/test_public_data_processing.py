import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.process_public_data import process_public_data


class PublicDataProcessingTests(unittest.TestCase):
    def test_process_public_data_writes_public_signal_views(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            public_data_dir = root / "public-data"
            processed_dir = root / "datasets" / "processed"
            output_dir = processed_dir / "public"
            self._write_public_inputs(public_data_dir)
            self._write_visit_entities(processed_dir)

            written = process_public_data(
                public_data_dir=public_data_dir,
                processed_dir=processed_dir,
                output_dir=output_dir,
            )

            expected_outputs = {
                "weather_signals",
                "crop_context",
                "ndvi_scene_inventory",
                "ndvi_signals",
                "pest_source_references",
                "pest_signals",
            }
            self.assertEqual(expected_outputs, set(written))

            weather = pd.read_csv(written["weather_signals"])
            self.assertEqual(2, len(weather))
            self.assertEqual("open_meteo", weather.loc[0, "source"])
            self.assertEqual("usable", weather.loc[0, "public_signal_status"])
            self.assertEqual(70, int(weather.loc[0, "rainfall_deviation_score"]))

            ndvi = pd.read_csv(written["ndvi_signals"])
            self.assertEqual("metadata_only", ndvi.loc[0, "public_signal_status"])
            self.assertEqual(0, int(ndvi.loc[0, "ndvi_stress_score"]))

            pest = pd.read_csv(written["pest_signals"])
            self.assertEqual("reference_only", pest.loc[0, "public_signal_status"])
            self.assertFalse(bool(pest.loc[0, "pest_alert_active"]))

    def _write_visit_entities(self, processed_dir: Path) -> None:
        processed_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [
                {
                    "entity_id": "RTL_001",
                    "territory_id": "TER_0164",
                    "primary_crop": "cotton",
                },
                {
                    "entity_id": "RTL_002",
                    "territory_id": "TER_0164",
                    "primary_crop": "cotton",
                },
                {
                    "entity_id": "RTL_999",
                    "territory_id": "OTHER",
                    "primary_crop": "cotton",
                },
            ]
        ).to_csv(processed_dir / "visit_entities.csv", index=False)

    def _write_public_inputs(self, public_data_dir: Path) -> None:
        open_meteo_path = (
            public_data_dir
            / "weather"
            / "open_meteo"
            / "amritsar_2026-05-17_2026-05-19.json"
        )
        open_meteo_path.parent.mkdir(parents=True, exist_ok=True)
        open_meteo_path.write_text(
            json.dumps(
                {
                    "daily": {
                        "time": ["2026-05-17"],
                        "temperature_2m_max": [38.8],
                        "temperature_2m_min": [25.9],
                        "relative_humidity_2m_mean": [37],
                        "precipitation_sum": [0],
                        "wind_speed_10m_max": [14.3],
                    }
                }
            ),
            encoding="utf-8",
        )

        stac_path = (
            public_data_dir
            / "ndvi"
            / "sentinel2_earth_search"
            / "amritsar_sentinel2_l2a_2026-05-01_2026-05-19.json"
        )
        stac_path.parent.mkdir(parents=True, exist_ok=True)
        stac_path.write_text(
            json.dumps(
                {
                    "features": [
                        {
                            "id": "S2_TEST",
                            "properties": {
                                "datetime": "2026-05-18T05:50:36.197000Z",
                                "eo:cloud_cover": 0.1,
                            },
                            "assets": {
                                "red": {},
                                "nir": {},
                                "scl": {},
                                "visual": {},
                            },
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        for reference_path in (
            public_data_dir / "pest_advisories" / "npss" / "aboutproject.pdf",
            public_data_dir
            / "pest_advisories"
            / "ppqs"
            / "sop_on_national_system_for_pest_monitoring_response_mechanism.pdf",
        ):
            reference_path.parent.mkdir(parents=True, exist_ok=True)
            reference_path.write_text("reference", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
