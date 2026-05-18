import unittest
from unittest.mock import patch

import pandas as pd
from fastapi import HTTPException

from backend.api.routes.anomaly_routes import get_alerts
from backend.api.routes.explainability_routes import get_entity_explanations
from backend.api.services.anomaly_service import AnomalyServiceError, get_alerts_response
from backend.api.services.explainability_service import (
    ExplainabilityServiceError,
    get_explanation_response,
)
from backend.main import create_app


ANOMALY_ALERTS = pd.DataFrame(
    [
        {
            "alert_id": "ALERT_ENT002_STOCK",
            "entity_id": "ENT002",
            "territory_id": "TERR002",
            "alert_type": "Demand Spike",
            "severity_score": 72.5,
            "severity_level": "High",
            "severity_rank": 3,
            "confidence_level": "Medium",
        },
        {
            "alert_id": "ALERT_ENT001_STOCK",
            "entity_id": "ENT001",
            "territory_id": "TERR001",
            "alert_type": "Stock-Out Risk",
            "severity_score": 91,
            "severity_level": "Critical",
            "severity_rank": 4,
            "confidence_level": "High",
        },
    ]
)

ANOMALY_ALERTS_WITH_FIVE_ROWS = pd.DataFrame(
    [
        {
            "alert_id": f"ALERT_ENT{index:03d}_STOCK",
            "entity_id": f"ENT{index:03d}",
            "territory_id": "TERR001",
            "alert_type": "Stock-Out Risk",
            "severity_score": 90 - index,
            "severity_level": "High",
            "severity_rank": 3,
            "confidence_level": "High",
        }
        for index in range(1, 6)
    ]
)

EXPLANATION_OUTPUTS = pd.DataFrame(
    [
        {
            "entity_id": "ENT001",
            "explanation_type": "recommendation",
            "source_output_id": "REC_ENT001",
            "summary_text": "Fungicide advisory is recommended.",
            "evidence_items": [
                {"source_field": "crop_stage", "value": "flowering"},
                {"description": "High humidity"},
            ],
            "confidence_level": "High",
        },
        {
            "entity_id": "ENT001",
            "explanation_type": "priority",
            "source_output_id": "PRIORITY_ENT001",
            "summary_text": "Entity is high priority.",
            "evidence_items": "['Priority score: 84.7', 'Inventory need']",
            "confidence_level": "Medium",
        },
    ]
)


class Build08AlertExplainabilityRoutesTest(unittest.TestCase):
    def test_alert_service_filters_and_preserves_response_shape(self):
        response = get_alerts_response(
            territory_id="TERR001",
            severity="Critical",
            anomaly_alerts=ANOMALY_ALERTS,
        )

        self.assertEqual(len(response.alerts), 1)
        self.assertEqual(response.alerts[0].alert_id, "ALERT_ENT001_STOCK")
        self.assertEqual(response.alerts[0].severity_score, 91.0)
        self.assertEqual(response.alerts[0].confidence_level, "High")

    def test_alert_service_defaults_to_first_page_of_three_alerts(self):
        response = get_alerts_response(anomaly_alerts=ANOMALY_ALERTS_WITH_FIVE_ROWS)

        self.assertEqual(response.page, 1)
        self.assertEqual(response.page_size, 3)
        self.assertEqual(response.total_count, 5)
        self.assertEqual(response.total_pages, 2)
        self.assertEqual(len(response.alerts), 3)

    def test_alert_service_allows_explicit_page_and_page_size_override(self):
        response = get_alerts_response(
            page=2,
            page_size=2,
            anomaly_alerts=ANOMALY_ALERTS_WITH_FIVE_ROWS,
        )

        self.assertEqual(response.page, 2)
        self.assertEqual(response.page_size, 2)
        self.assertEqual(response.total_count, 5)
        self.assertEqual(len(response.alerts), 2)

    def test_alert_service_rejects_invalid_pagination(self):
        with self.assertRaisesRegex(AnomalyServiceError, "page"):
            get_alerts_response(page=0, anomaly_alerts=ANOMALY_ALERTS_WITH_FIVE_ROWS)

    def test_alert_service_returns_stable_empty_response_without_processed_file(self):
        response = get_alerts_response(data_path="datasets/processed/missing_anomaly_alerts.csv")

        self.assertEqual(
            response.model_dump(),
            {
                "page": 1,
                "page_size": 3,
                "total_count": 0,
                "total_pages": 0,
                "alerts": [],
            },
        )

    def test_alert_route_returns_empty_response_from_missing_default_data(self):
        response = get_alerts(territory_id=None, severity=None)

        self.assertIsInstance(response.alerts, list)
        if response.alerts:
            self.assertTrue(response.alerts[0].alert_id)
        else:
            self.assertEqual(response.alerts, [])

    def test_alert_service_missing_columns_fails_explicitly(self):
        with self.assertRaisesRegex(AnomalyServiceError, "severity_score"):
            get_alerts_response(anomaly_alerts=ANOMALY_ALERTS.drop(columns=["severity_score"]))

    def test_explanation_service_formats_existing_evidence(self):
        response = get_explanation_response(
            "ENT001",
            explanation_outputs=EXPLANATION_OUTPUTS,
        )

        self.assertEqual(response.entity_id, "ENT001")
        self.assertEqual(
            [item.explanation_type for item in response.explanations],
            ["priority", "recommendation"],
        )
        self.assertEqual(response.explanations[0].evidence_items, ["Priority score: 84.7", "Inventory need"])
        self.assertEqual(response.explanations[1].evidence_items, ["crop_stage: flowering", "High humidity"])

    def test_explanation_service_returns_empty_response_for_missing_entity_or_file(self):
        missing_entity = get_explanation_response(
            "ENT999",
            explanation_outputs=EXPLANATION_OUTPUTS,
        )
        missing_file = get_explanation_response(
            "ENT001",
            data_path="datasets/processed/missing_explanation_outputs.csv",
        )

        self.assertEqual(missing_entity.model_dump(), {"entity_id": "ENT999", "explanations": []})
        self.assertEqual(missing_file.model_dump(), {"entity_id": "ENT001", "explanations": []})

    def test_explanation_route_returns_empty_response_from_missing_default_data(self):
        response = get_entity_explanations("ENT001")

        self.assertEqual(response.entity_id, "ENT001")
        self.assertEqual(response.explanations, [])

    def test_explanation_service_missing_columns_fails_explicitly(self):
        with self.assertRaisesRegex(ExplainabilityServiceError, "summary_text"):
            get_explanation_response(
                "ENT001",
                explanation_outputs=EXPLANATION_OUTPUTS.drop(columns=["summary_text"]),
            )

    def test_routes_map_service_errors_to_structured_400(self):
        with patch(
            "backend.api.routes.anomaly_routes.get_alerts_response",
            side_effect=AnomalyServiceError("bad alerts"),
        ):
            with self.assertRaises(HTTPException) as alert_error:
                get_alerts(territory_id=None, severity=None)

        with patch(
            "backend.api.routes.explainability_routes.get_explanation_response",
            side_effect=ExplainabilityServiceError("bad explanations"),
        ):
            with self.assertRaises(HTTPException) as explanation_error:
                get_entity_explanations("ENT001")

        self.assertEqual(alert_error.exception.status_code, 400)
        self.assertIn("error", alert_error.exception.detail)
        self.assertEqual(explanation_error.exception.status_code, 400)
        self.assertIn("error", explanation_error.exception.detail)

    def test_app_registers_alert_and_explainability_routes(self):
        routes = sorted(route.path for route in create_app().routes)

        self.assertIn("/alerts", routes)
        self.assertIn("/explanations/{entity_id}", routes)


if __name__ == "__main__":
    unittest.main()
