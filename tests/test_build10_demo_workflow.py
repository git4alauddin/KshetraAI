import csv
import tempfile
import unittest
from pathlib import Path

from demo.scripts.verify_demo_workflow import (
    PLAN_DATE,
    REP_ID,
    TERRITORY_ID,
    has_blocking_failures,
    verify_demo_workflow,
)


class Build10DemoWorkflowVerificationTest(unittest.TestCase):
    def test_current_repo_demo_wiring_has_no_blocking_failures(self):
        checks = verify_demo_workflow()

        self.assertFalse(has_blocking_failures(checks))
        self.assertTrue(any(check.name == "backend API route contract" for check in checks))
        self.assertTrue(all(check.status in {"PASS", "WARN"} for check in checks))

    def test_verifier_marks_complete_fixed_scenario_outputs_as_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _write_required_demo_docs(repo_root)
            _write_required_frontend_files(repo_root)
            processed_dir = repo_root / "datasets" / "processed"
            processed_dir.mkdir(parents=True)
            _write_csv(
                processed_dir / "ranked_visit_list.csv",
                [
                    {
                        "rank": "1",
                        "entity_id": "ENT_AMRITSAR_001",
                        "entity_name": "Amritsar Agro Center",
                        "rep_id": REP_ID,
                        "territory_id": TERRITORY_ID,
                        "date": PLAN_DATE,
                        "priority_score": "91.5",
                        "priority_level": "Critical",
                        "main_reason": "Low fungicide stock and crop stress",
                    }
                ],
            )
            _write_csv(
                processed_dir / "recommendation_outputs.csv",
                [
                    {
                        "entity_id": "ENT_AMRITSAR_001",
                        "recommended_actions": "['Discuss fungicide restocking']",
                        "confidence_level": "High",
                    }
                ],
            )
            _write_csv(
                processed_dir / "explanation_outputs.csv",
                [
                    {
                        "entity_id": "ENT_AMRITSAR_001",
                        "explanation_type": "recommendation",
                        "summary_text": "Fungicide advisory is supported.",
                        "evidence_items": "['low stock', 'demand increase']",
                        "confidence_level": "High",
                    }
                ],
            )
            _write_csv(
                processed_dir / "anomaly_alerts.csv",
                [
                    {
                        "alert_id": "ALERT_AMRITSAR_001",
                        "entity_id": "ENT_AMRITSAR_001",
                        "territory_id": TERRITORY_ID,
                        "alert_type": "Stock-Out Risk",
                        "severity_score": "88",
                        "severity_level": "High",
                        "confidence_level": "High",
                    }
                ],
            )

            checks = verify_demo_workflow(repo_root)

        warning_checks = [check for check in checks if check.status == "WARN"]
        self.assertEqual(warning_checks, [])
        self.assertFalse(has_blocking_failures(checks))


def _write_required_demo_docs(repo_root: Path) -> None:
    for relative_path in (
        "demo/scenarios/amritsar_crop_protection_scenario.md",
        "demo/judging_flow/amritsar_crop_protection_judging_flow.md",
        "demo/runbook.md",
    ):
        path = repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ready", encoding="utf-8")


def _write_required_frontend_files(repo_root: Path) -> None:
    for relative_path in (
        "frontend/App.tsx",
        "frontend/pages/Dashboard.tsx",
        "frontend/pages/VisitPlan.tsx",
        "frontend/pages/RecommendationView.tsx",
        "frontend/pages/AlertsView.tsx",
        "frontend/pages/OutcomeSubmission.tsx",
        "frontend/services/apiClient.ts",
    ):
        path = repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("ready", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    unittest.main()
