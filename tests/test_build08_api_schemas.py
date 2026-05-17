import unittest

from pydantic import ValidationError

from backend.api.schemas.anomaly_schema import AlertResponse, AlertsResponse
from backend.api.schemas.explainability_schema import (
    ExplanationItemResponse,
    ExplanationResponse,
)
from backend.api.schemas.outcome_schema import (
    OutcomeSubmissionRequest,
    OutcomeSubmissionResponse,
)
from backend.api.schemas.planning_schema import (
    DailyPlanQuery,
    DailyPlanResponse,
    RankedEntityResponse,
)
from backend.api.schemas.recommendation_schema import RecommendationResponse


class Build08APISchemasTest(unittest.TestCase):
    def test_daily_plan_schema_matches_documented_shape(self):
        response = DailyPlanResponse(
            rep_id="REP001",
            territory_id="TERR_WARDHA_01",
            date="2026-05-17",
            ranked_entities=[
                RankedEntityResponse(
                    rank=1,
                    entity_id="ENT001",
                    entity_name="Ramesh Agro Center",
                    priority_score=84.7,
                    priority_level="Critical",
                    main_reason="High agronomic urgency and inventory need",
                )
            ],
        )

        self.assertEqual(
            response.model_dump(),
            {
                "rep_id": "REP001",
                "territory_id": "TERR_WARDHA_01",
                "date": "2026-05-17",
                "ranked_entities": [
                    {
                        "rank": 1,
                        "entity_id": "ENT001",
                        "entity_name": "Ramesh Agro Center",
                        "priority_score": 84.7,
                        "priority_level": "Critical",
                        "main_reason": "High agronomic urgency and inventory need",
                    }
                ],
            },
        )

    def test_recommendation_schema_matches_documented_shape(self):
        response = RecommendationResponse(
            entity_id="ENT001",
            risk_or_opportunity="Possible fungal disease risk",
            recommended_actions=["Inspect crop symptoms", "Discuss fungicide advisory"],
            recommended_product_category="Fungicide",
            confidence_level="High",
        )

        self.assertEqual(response.entity_id, "ENT001")
        self.assertEqual(response.confidence_level, "High")
        self.assertEqual(len(response.recommended_actions), 2)

    def test_alert_schema_matches_documented_shape(self):
        response = AlertsResponse(
            alerts=[
                AlertResponse(
                    alert_id="ALERT001",
                    entity_id="ENT001",
                    alert_type="Stock-Out Risk",
                    severity_score=91,
                    severity_level="Critical",
                    confidence_level="High",
                )
            ]
        )

        self.assertEqual(response.model_dump()["alerts"][0]["alert_type"], "Stock-Out Risk")
        self.assertEqual(response.model_dump()["alerts"][0]["severity_score"], 91.0)

    def test_explanation_schema_matches_documented_shape(self):
        response = ExplanationResponse(
            entity_id="ENT001",
            explanations=[
                ExplanationItemResponse(
                    explanation_type="recommendation",
                    summary_text="Fungicide advisory is recommended.",
                    evidence_items=["Cotton flowering stage", "High humidity"],
                    confidence_level="High",
                )
            ],
        )

        self.assertEqual(response.explanations[0].explanation_type, "recommendation")
        self.assertEqual(response.explanations[0].evidence_items[1], "High humidity")

    def test_outcome_submission_schema_validates_payload(self):
        request = OutcomeSubmissionRequest(
            recommendation_id="REC001",
            entity_id="ENT001",
            rep_id="REP001",
            visit_completed=True,
            recommendation_followed=True,
            sale_made=True,
            order_placed=True,
            order_value=18500,
            alert_validated="unknown",
            rep_feedback="Recommendation was useful.",
        )
        response = OutcomeSubmissionResponse(
            status="success",
            message="Outcome recorded successfully.",
            outcome_id="OUTCOME_ENT001_REC001",
        )

        self.assertEqual(request.feedback_category, "no_feedback")
        self.assertEqual(request.order_value, 18500.0)
        self.assertEqual(response.status, "success")

    def test_schema_defaults_are_stable_empty_collections(self):
        self.assertEqual(DailyPlanQuery().model_dump(), {"rep_id": None, "territory_id": None, "date": None})
        self.assertEqual(DailyPlanResponse().ranked_entities, [])
        self.assertEqual(AlertsResponse().alerts, [])
        self.assertEqual(ExplanationResponse(entity_id="ENT001").explanations, [])

    def test_invalid_scores_and_order_values_fail_validation(self):
        with self.assertRaises(ValidationError):
            RankedEntityResponse(
                rank=0,
                entity_id="ENT001",
                priority_score=50,
                priority_level="Medium",
            )

        with self.assertRaises(ValidationError):
            AlertResponse(
                alert_id="ALERT001",
                entity_id="ENT001",
                alert_type="Stock-Out Risk",
                severity_score=101,
                severity_level="Critical",
                confidence_level="High",
            )

        with self.assertRaises(ValidationError):
            OutcomeSubmissionRequest(
                recommendation_id="REC001",
                entity_id="ENT001",
                rep_id="REP001",
                visit_completed=True,
                recommendation_followed=True,
                sale_made=True,
                order_placed=True,
                order_value=-1,
                alert_validated=True,
            )


if __name__ == "__main__":
    unittest.main()
