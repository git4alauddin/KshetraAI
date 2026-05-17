import unittest

from backend.api.routes.health_routes import get_health
from backend.main import API_TITLE, API_VERSION, create_app


class Build08FastAPIEntrypointTest(unittest.TestCase):
    def test_health_endpoint_returns_stable_response(self):
        self.assertEqual(
            get_health(),
            {
                "status": "ok",
                "service": "kshetraai-backend",
            },
        )

    def test_app_metadata_and_route_registration_are_stable(self):
        app = create_app()
        routes = sorted(route.path for route in app.routes)

        self.assertEqual(app.title, API_TITLE)
        self.assertEqual(app.version, API_VERSION)
        self.assertIn("/health", routes)
        self.assertNotIn("/daily-plan", routes)
        self.assertNotIn("/recommendations/{entity_id}", routes)


if __name__ == "__main__":
    unittest.main()
