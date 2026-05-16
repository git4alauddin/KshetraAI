import unittest

import pandas as pd

from backend.features.agronomic_features import (
    AGRONOMIC_FEATURE_COLUMNS,
    AgronomicFeatureError,
    build_agronomic_feature_view,
    build_crop_stage_features,
    build_ndvi_features,
    build_pest_disease_features,
    build_weather_features,
)


class Build02AgronomicFeaturesTest(unittest.TestCase):
    def test_individual_builders_generate_bounded_canonical_scores(self):
        crop_stage = build_crop_stage_features(
            pd.DataFrame(
                [
                    {"entity_id": "E001", "crop": "wheat", "crop_stage": "flowering"},
                    {"entity_id": "E002", "crop": "wheat", "crop_stage": "harvest"},
                ]
            )
        )
        weather = build_weather_features(
            pd.DataFrame(
                [
                    {
                        "entity_id": "E001",
                        "date": "2026-01-02",
                        "rainfall_deviation_score": 90,
                        "humidity_percent": 88,
                        "temperature_c": 30,
                    }
                ]
            ),
            crop_stage,
        )
        pest = build_pest_disease_features(
            pd.DataFrame(
                [
                    {
                        "entity_id": "E001",
                        "date": "2026-01-02",
                        "pest_alert_active": "true",
                        "alert_severity": "high",
                    },
                    {
                        "entity_id": "E002",
                        "date": "2026-01-02",
                        "pest_alert_active": "false",
                        "alert_severity": "critical",
                    },
                ]
            )
        )
        ndvi = build_ndvi_features(
            pd.DataFrame(
                [{"entity_id": "E001", "date": "2026-01-02", "ndvi_drop_percent": 35}]
            )
        )

        self.assertEqual(crop_stage.loc[0, "crop_stage_risk_score"], 80)
        self.assertIn("weather_risk_score", weather.columns)
        self.assertEqual(pest.loc[0, "pest_disease_risk_score"], 80)
        self.assertEqual(pest.loc[1, "pest_disease_risk_score"], 0)
        self.assertEqual(ndvi.loc[0, "ndvi_stress_score"], 100)

        for frame, score_column in (
            (crop_stage, "crop_stage_risk_score"),
            (weather, "weather_risk_score"),
            (pest, "pest_disease_risk_score"),
            (ndvi, "ndvi_stress_score"),
        ):
            self.assertTrue(frame[score_column].between(0, 100).all())

    def test_agronomic_feature_view_is_entity_level_and_deterministic(self):
        datasets = _sample_agronomic_datasets()

        first = build_agronomic_feature_view(datasets)
        second = build_agronomic_feature_view(datasets)

        self.assertTrue(first.equals(second))
        self.assertEqual(list(first.columns), ["entity_id", *AGRONOMIC_FEATURE_COLUMNS])
        self.assertEqual(first["entity_id"].tolist(), ["E001", "E002"])
        self.assertEqual(first.loc[0, "crop_stage_risk_score"], 80)
        self.assertEqual(first.loc[1, "pest_disease_risk_score"], 0)

    def test_latest_signal_per_entity_is_used_for_entity_level_view(self):
        view = build_agronomic_feature_view(
            {
                "weather_signals": pd.DataFrame(
                    [
                        {"entity_id": "E001", "date": "2026-01-01", "weather_risk_score": 20},
                        {"entity_id": "E001", "date": "2026-01-03", "weather_risk_score": 70},
                    ]
                )
            }
        )

        self.assertEqual(view.loc[0, "weather_risk_score"], 70)

    def test_missing_required_inputs_fail_explicitly(self):
        with self.assertRaises(AgronomicFeatureError):
            build_crop_stage_features(pd.DataFrame([{"entity_id": "E001"}]))

        with self.assertRaises(AgronomicFeatureError):
            build_agronomic_feature_view({})


def _sample_agronomic_datasets():
    return {
        "crop_context": pd.DataFrame(
            [
                {"entity_id": "E002", "crop": "wheat", "crop_stage": "harvest"},
                {"entity_id": "E001", "crop": "wheat", "crop_stage": "flowering"},
            ]
        ),
        "weather_signals": pd.DataFrame(
            [
                {
                    "entity_id": "E001",
                    "date": "2026-01-02",
                    "rainfall_deviation_score": 90,
                    "humidity_percent": 88,
                    "temperature_c": 30,
                },
                {
                    "entity_id": "E002",
                    "date": "2026-01-02",
                    "rainfall_deviation_score": 20,
                    "humidity_percent": 50,
                    "temperature_c": 25,
                },
            ]
        ),
        "pest_signals": pd.DataFrame(
            [
                {
                    "entity_id": "E001",
                    "date": "2026-01-02",
                    "pest_alert_active": "true",
                    "alert_severity": "high",
                },
                {
                    "entity_id": "E002",
                    "date": "2026-01-02",
                    "pest_alert_active": "false",
                    "alert_severity": "critical",
                },
            ]
        ),
        "ndvi_signals": pd.DataFrame(
            [
                {"entity_id": "E001", "date": "2026-01-02", "ndvi_drop_percent": 15},
                {"entity_id": "E002", "date": "2026-01-02", "ndvi_stress_level": "low"},
            ]
        ),
    }


if __name__ == "__main__":
    unittest.main()

