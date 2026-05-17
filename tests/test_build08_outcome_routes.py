import unittest
from unittest.mock import patch

from fastapi import HTTPException

from backend.api.routes.outcome_routes import submit_outcome
from backend.api.schemas.outcome_schema import OutcomeSubmissionRequest
from backend.api.services.outcome_service import OutcomeServiceError, submit_outcome_response
from backend.main import create_app


VALID_OUTCOME_REQUEST = OutcomeSubmissionRequest(
    recommendation_id="AGRONOMIC_PEST_DISEASE_RISK_HIGH",
    alert_id="ALERT_RET001_PEST_RISK",
    entity_id="RET001",
    rep_id="REP001",
    visit_completed=True,
    recommendation_followed=True,
    sale_made=True,
    order_placed=True,
    order_value=18500,
    alert_validated=True,
    feedback_category="useful",
    rep_feedback="Retailer accepted advisory and placed order.",
)


class Build08OutcomeRoutesTest(unittest.TestCase):
    def test_outcome_service_delegates_to_existing_outcome_logger(self):
        response = submit_outcome_response(VALID_OUTCOME_REQUEST)

        self.assertEqual(response.status, "success")
        self.assertEqual(response.message, "Outcome recorded successfully.")
        self.assertEqual(
            response.outcome_id,
            "OUTCOME_RET001_AGRONOMIC_PEST_DISEASE_RISK_HIGH",
        )

    def test_outcome_route_returns_stable_success_response(self):
        response = submit_outcome(VALID_OUTCOME_REQUEST)

        self.assertEqual(
            response.model_dump(),
            {
                "status": "success",
                "message": "Outcome recorded successfully.",
                "outcome_id": "OUTCOME_RET001_AGRONOMIC_PEST_DISEASE_RISK_HIGH",
            },
        )

    def test_outcome_service_maps_logger_errors(self):
        invalid_request = VALID_OUTCOME_REQUEST.model_copy(
            update={"feedback_category": "maybe_useful"}
        )

        with self.assertRaisesRegex(OutcomeServiceError, "feedback_category"):
            submit_outcome_response(invalid_request)

    def test_outcome_route_maps_service_errors_to_structured_400(self):
        with patch(
            "backend.api.routes.outcome_routes.submit_outcome_response",
            side_effect=OutcomeServiceError("bad outcome"),
        ):
            with self.assertRaises(HTTPException) as raised:
                submit_outcome(VALID_OUTCOME_REQUEST)

        self.assertEqual(raised.exception.status_code, 400)
        self.assertEqual(raised.exception.detail, {"error": "bad outcome"})

    def test_app_registers_outcome_route(self):
        routes = sorted(route.path for route in create_app().routes)

        self.assertIn("/outcomes", routes)


if __name__ == "__main__":
    unittest.main()
