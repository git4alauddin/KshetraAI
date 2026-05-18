import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = REPO_ROOT / "frontend"


class Build09FrontendWorkflowTests(unittest.TestCase):
    def read_frontend_file(self, relative_path: str) -> str:
        return (FRONTEND_ROOT / relative_path).read_text(encoding="utf-8")

    def test_frontend_build_script_is_available(self):
        package_json = json.loads((FRONTEND_ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertIn("build", package_json["scripts"])
        self.assertIn("tsc -b", package_json["scripts"]["build"])
        self.assertIn("vite build", package_json["scripts"]["build"])

    def test_api_client_preserves_build08_endpoint_contracts(self):
        api_client = self.read_frontend_file("services/apiClient.ts")

        expected_contracts = [
            '"/health"',
            "`/daily-plan",
            '`/recommendations/${encodeURIComponent(entityId)}`',
            "`/alerts",
            '`/explanations/${encodeURIComponent(entityId)}`',
            '"/outcomes"',
            "method: \"POST\"",
            "\"Content-Type\": \"application/json\""
        ]
        for contract in expected_contracts:
            with self.subTest(contract=contract):
                self.assertIn(contract, api_client)

    def test_workflow_pages_use_frontend_hooks_for_api_access(self):
        page_hook_pairs = {
            "pages/VisitPlan.tsx": ["useDailyPlan("],
            "pages/RecommendationView.tsx": ["useRecommendation(", "useExplanation("],
            "pages/AlertsView.tsx": ["useAlerts("],
            "pages/OutcomeSubmission.tsx": ["useSubmitOutcome("]
        }

        for page_path, required_hooks in page_hook_pairs.items():
            source = self.read_frontend_file(page_path)
            for hook in required_hooks:
                with self.subTest(page=page_path, hook=hook):
                    self.assertIn(hook, source)
            self.assertNotIn("fetch(", source)

    def test_frontend_views_cover_loading_error_empty_and_success_states(self):
        expected_state_markers = {
            "pages/VisitPlan.tsx": [
                "Loading daily plan from backend API",
                "Unable to load daily plan",
                "No ranked visits returned"
            ],
            "pages/RecommendationView.tsx": [
                "Loading recommendation and explanation from backend API",
                "Unable to load recommendation",
                "Unable to load explanation",
                "No recommendation loaded",
                "No explanation loaded"
            ],
            "pages/AlertsView.tsx": [
                "Loading alerts from backend API",
                "Unable to load alerts",
                "No active alerts returned"
            ],
            "pages/OutcomeSubmission.tsx": [
                "Unable to submit outcome",
                "outcomeSubmission.data"
            ]
        }

        for page_path, markers in expected_state_markers.items():
            source = self.read_frontend_file(page_path)
            for marker in markers:
                with self.subTest(page=page_path, marker=marker):
                    self.assertIn(marker, source)

    def test_outcome_form_captures_required_build09_payload_fields(self):
        outcome_form = self.read_frontend_file("components/OutcomeForm.tsx")

        required_payload_fields = [
            "recommendation_id",
            "entity_id",
            "rep_id",
            "visit_completed",
            "recommendation_followed",
            "sale_made",
            "order_placed",
            "order_value",
            "alert_validated",
            "feedback_category",
            "rep_feedback",
            "alert_id"
        ]
        for field in required_payload_fields:
            with self.subTest(field=field):
                self.assertIn(field, outcome_form)
        self.assertIn("Recommendation ID, entity ID, and rep ID are required.", outcome_form)
        self.assertIn("Order value must be zero or a positive number.", outcome_form)

    def test_explanation_panel_groups_trace_rows_for_readability(self):
        explanation_panel = self.read_frontend_file("components/ExplanationPanel.tsx")

        expected_markers = [
            "Primary reason",
            "Key evidence",
            "Supporting signals",
            "Trace details",
            "Recommendation rules matched",
            "Operational alerts",
            "canonicalEvidenceKey",
            "sales_opportunity_score",
            "inventory_need_score"
        ]
        for marker in expected_markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, explanation_panel)

    def test_frontend_does_not_recreate_backend_intelligence_logic(self):
        searched_paths = [
            path
            for path in FRONTEND_ROOT.rglob("*.tsx")
            if "node_modules" not in path.parts and "dist" not in path.parts
        ]
        disallowed_fragments = [
            "priority_score =",
            "priorityScore =",
            "severity_score =",
            "severityScore =",
            "recommended_actions =",
            "recommendedActions =",
            "calculatePriority",
            "generateRecommendation",
            "detectAnomaly",
            "scoreWeights"
        ]

        for path in searched_paths:
            source = path.read_text(encoding="utf-8")
            for fragment in disallowed_fragments:
                with self.subTest(path=path.relative_to(REPO_ROOT), fragment=fragment):
                    self.assertNotIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
