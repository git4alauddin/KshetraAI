import unittest

import pandas as pd
from fastapi import HTTPException

from backend.api.routes.planning_routes import get_daily_plan
from backend.api.routes.recommendation_routes import get_entity_recommendation
from backend.api.services.planning_service import (
    PlanningServiceError,
    get_daily_plan_response,
)
from backend.api.services.recommendation_service import (
    RecommendationNotFoundError,
    RecommendationServiceError,
    get_recommendation_response,
)
from backend.main import create_app


RANKED_VISIT_LIST = pd.DataFrame(
    [
        {
            "rank": 2,
            "entity_id": "ENT002",
            "entity_name": "Wardha Agro",
            "rep_id": "REP002",
            "territory_id": "TERR002",
            "date": "2026-05-17",
            "priority_score": 72.5,
            "priority_level": "High",
            "main_reason": "Inventory need",
        },
        {
            "rank": 1,
            "entity_id": "ENT001",
            "entity_name": "Ramesh Agro Center",
            "rep_id": "REP001",
            "territory_id": "TERR001",
            "date": "2026-05-17",
            "priority_score": 84.7,
            "priority_level": "Critical",
            "main_reason": "High agronomic urgency",
        },
    ]
)

RANKED_VISIT_LIST_WITH_SEVEN_ROWS = pd.DataFrame(
    [
        {
            "rank": rank,
            "entity_id": f"ENT{rank:03d}",
            "entity_name": f"Entity {rank}",
            "priority_score": 90 - rank,
            "priority_level": "High",
        }
        for rank in range(1, 8)
    ]
)

RECOMMENDATION_OUTPUTS = pd.DataFrame(
    [
        {
            "entity_id": "ENT001",
            "matched_rule_id": "AGRONOMIC_RISK_HIGH",
            "priority_order": 2,
            "recommended_actions": "['Inspect crop symptoms']",
            "recommended_product_category": "Fungicide",
            "confidence_level": "Medium",
        },
        {
            "entity_id": "ENT001",
            "matched_rule_id": "INVENTORY_NEED_HIGH",
            "priority_order": 1,
            "recommended_actions": ["Review stock position", "Plan replenishment"],
            "recommended_product_category": "Crop Protection",
            "confidence_level": "High",
        },
    ]
)


class Build08PlanningRecommendationRoutesTest(unittest.TestCase):
    def test_daily_plan_service_filters_and_preserves_ranked_shape(self):
        response = get_daily_plan_response(
            rep_id="REP001",
            territory_id="TERR001",
            date="2026-05-17",
            ranked_visit_list=RANKED_VISIT_LIST,
        )

        self.assertEqual(response.rep_id, "REP001")
        self.assertEqual(len(response.ranked_entities), 1)
        self.assertEqual(response.ranked_entities[0].entity_id, "ENT001")
        self.assertEqual(response.ranked_entities[0].priority_score, 84.7)
        self.assertEqual(response.ranked_entities[0].main_reason, "High agronomic urgency")

    def test_daily_plan_service_defaults_to_first_page_of_three_ranked_entities(self):
        response = get_daily_plan_response(ranked_visit_list=RANKED_VISIT_LIST_WITH_SEVEN_ROWS)

        self.assertEqual(response.page, 1)
        self.assertEqual(response.page_size, 3)
        self.assertEqual(response.total_count, 7)
        self.assertEqual(response.total_pages, 3)
        self.assertEqual(len(response.ranked_entities), 3)
        self.assertEqual([entity.rank for entity in response.ranked_entities], [1, 2, 3])

    def test_daily_plan_service_allows_explicit_page_and_page_size_override(self):
        response = get_daily_plan_response(
            page=2,
            page_size=3,
            ranked_visit_list=RANKED_VISIT_LIST_WITH_SEVEN_ROWS,
        )

        self.assertEqual(len(response.ranked_entities), 3)
        self.assertEqual([entity.rank for entity in response.ranked_entities], [4, 5, 6])
        self.assertEqual(response.ranked_entities[-1].entity_id, "ENT006")

    def test_daily_plan_service_ranks_filtered_view_by_priority_score(self):
        response = get_daily_plan_response(ranked_visit_list=RANKED_VISIT_LIST)

        self.assertEqual([entity.entity_id for entity in response.ranked_entities], ["ENT001", "ENT002"])
        self.assertEqual([entity.rank for entity in response.ranked_entities], [1, 2])

    def test_daily_plan_service_rejects_invalid_pagination(self):
        with self.assertRaisesRegex(PlanningServiceError, "page"):
            get_daily_plan_response(
                page=0,
                ranked_visit_list=RANKED_VISIT_LIST_WITH_SEVEN_ROWS,
            )

    def test_daily_plan_service_returns_stable_empty_response_without_processed_file(self):
        response = get_daily_plan_response(data_path="datasets/processed/missing_ranked_visit_list.csv")

        self.assertEqual(
            response.model_dump(),
            {
                "rep_id": None,
                "territory_id": None,
                "date": None,
                "page": 1,
                "page_size": 3,
                "total_count": 0,
                "total_pages": 0,
                "ranked_entities": [],
            },
        )

    def test_daily_plan_route_returns_empty_response_from_missing_default_data(self):
        response = get_daily_plan(rep_id="REP001", territory_id=None, date=None)

        self.assertEqual(response.rep_id, "REP001")
        self.assertEqual(response.ranked_entities, [])

    def test_daily_plan_service_missing_columns_fails_explicitly(self):
        with self.assertRaisesRegex(PlanningServiceError, "priority_score"):
            get_daily_plan_response(ranked_visit_list=RANKED_VISIT_LIST.drop(columns=["priority_score"]))

    def test_recommendation_service_returns_first_existing_recommendation(self):
        response = get_recommendation_response(
            "ENT001",
            recommendation_outputs=RECOMMENDATION_OUTPUTS,
        )

        self.assertEqual(response.entity_id, "ENT001")
        self.assertEqual(response.risk_or_opportunity, "INVENTORY_NEED_HIGH")
        self.assertEqual(response.recommended_actions, ["Review stock position", "Plan replenishment"])
        self.assertEqual(response.confidence_level, "High")

    def test_recommendation_service_raises_not_found_for_missing_entity(self):
        with self.assertRaisesRegex(RecommendationNotFoundError, "ENT999"):
            get_recommendation_response("ENT999", recommendation_outputs=RECOMMENDATION_OUTPUTS)

    def test_recommendation_route_maps_missing_default_data_to_404(self):
        with self.assertRaises(HTTPException) as raised:
            get_entity_recommendation("ENT001")

        self.assertEqual(raised.exception.status_code, 404)
        self.assertIn("error", raised.exception.detail)

    def test_recommendation_service_missing_columns_fails_explicitly(self):
        with self.assertRaisesRegex(RecommendationServiceError, "confidence_level"):
            get_recommendation_response(
                "ENT001",
                recommendation_outputs=RECOMMENDATION_OUTPUTS.drop(columns=["confidence_level"]),
            )

    def test_app_registers_planning_and_recommendation_routes(self):
        routes = sorted(route.path for route in create_app().routes)

        self.assertIn("/daily-plan", routes)
        self.assertIn("/recommendations/{entity_id}", routes)


if __name__ == "__main__":
    unittest.main()
