import ast
import inspect
import unittest

from fastapi.routing import APIRoute

from backend.api.routes import (
    anomaly_routes,
    explainability_routes,
    health_routes,
    outcome_routes,
    planning_routes,
    recommendation_routes,
)
from backend.api.schemas.anomaly_schema import AlertsResponse
from backend.api.schemas.explainability_schema import ExplanationResponse
from backend.api.schemas.outcome_schema import OutcomeSubmissionResponse
from backend.api.schemas.planning_schema import DailyPlanResponse
from backend.api.schemas.recommendation_schema import RecommendationResponse
from backend.main import create_app


EXPECTED_API_CONTRACT = {
    "/health": {
        "methods": {"GET"},
        "response_model": dict[str, str],
    },
    "/daily-plan": {
        "methods": {"GET"},
        "response_model": DailyPlanResponse,
    },
    "/recommendations/{entity_id}": {
        "methods": {"GET"},
        "response_model": RecommendationResponse,
    },
    "/alerts": {
        "methods": {"GET"},
        "response_model": AlertsResponse,
    },
    "/explanations/{entity_id}": {
        "methods": {"GET"},
        "response_model": ExplanationResponse,
    },
    "/outcomes": {
        "methods": {"POST"},
        "response_model": OutcomeSubmissionResponse,
    },
}

ROUTE_MODULES = (
    anomaly_routes,
    explainability_routes,
    health_routes,
    outcome_routes,
    planning_routes,
    recommendation_routes,
)

FORBIDDEN_ROUTE_IMPORT_PREFIXES = (
    "backend.engines",
    "backend.anomaly",
    "backend.explainability",
    "backend.learning",
    "backend.features",
)


class Build08APIContractTest(unittest.TestCase):
    def test_registered_routes_match_build08_contract(self):
        api_routes = {
            route.path: route
            for route in create_app().routes
            if isinstance(route, APIRoute)
        }

        self.assertEqual(set(api_routes), set(EXPECTED_API_CONTRACT))
        for path, expected in EXPECTED_API_CONTRACT.items():
            with self.subTest(path=path):
                route = api_routes[path]
                self.assertEqual(route.methods, expected["methods"])
                self.assertEqual(route.response_model, expected["response_model"])

    def test_route_names_are_stable_and_frontend_friendly(self):
        route_paths = [
            route.path
            for route in create_app().routes
            if isinstance(route, APIRoute)
        ]

        self.assertEqual(
            route_paths,
            [
                "/health",
                "/daily-plan",
                "/recommendations/{entity_id}",
                "/alerts",
                "/explanations/{entity_id}",
                "/outcomes",
            ],
        )

    def test_route_modules_delegate_to_services_without_core_engine_imports(self):
        for module in ROUTE_MODULES:
            with self.subTest(module=module.__name__):
                imported_modules = _imported_modules(module)
                forbidden_imports = [
                    imported_module
                    for imported_module in imported_modules
                    if imported_module.startswith(FORBIDDEN_ROUTE_IMPORT_PREFIXES)
                ]

                self.assertEqual(forbidden_imports, [])

    def test_route_error_responses_use_structured_error_detail(self):
        for module in (
            anomaly_routes,
            explainability_routes,
            outcome_routes,
            planning_routes,
            recommendation_routes,
        ):
            with self.subTest(module=module.__name__):
                source = inspect.getsource(module)

                self.assertIn('detail={"error": str(exc)}', source)
                self.assertNotIn("traceback", source.lower())


def _imported_modules(module) -> list[str]:
    parsed_module = ast.parse(inspect.getsource(module))
    imported_modules = []
    for node in ast.walk(parsed_module):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.append(node.module)
    return imported_modules


if __name__ == "__main__":
    unittest.main()
