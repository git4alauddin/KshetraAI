"""Verify Build 10 demo workflow readiness without changing core logic.

The verifier checks integration wiring and deterministic demo data readiness.
Missing processed demo outputs are reported as warnings so the script can be
used early in Build 10 before sample outputs are captured.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.routing import APIRoute

from backend.main import create_app


SCENARIO_ID = "AMRITSAR_CROP_PROTECTION_001"
REP_ID = "REP_0164"
TERRITORY_ID = "TER_0164"
PLAN_DATE = "2026-05-17"

EXPECTED_ROUTES = (
    "/health",
    "/daily-plan",
    "/recommendations/{entity_id}",
    "/alerts",
    "/explanations/{entity_id}",
    "/outcomes",
)

REQUIRED_DEMO_DOCS = (
    "demo/scenarios/amritsar_crop_protection_scenario.md",
    "demo/judging_flow/amritsar_crop_protection_judging_flow.md",
    "demo/runbook.md",
)

REQUIRED_FRONTEND_FILES = (
    "frontend/App.tsx",
    "frontend/pages/Dashboard.tsx",
    "frontend/pages/VisitPlan.tsx",
    "frontend/pages/RecommendationView.tsx",
    "frontend/pages/AlertsView.tsx",
    "frontend/pages/OutcomeSubmission.tsx",
    "frontend/services/apiClient.ts",
)

REQUIRED_PROCESSED_OUTPUTS = {
    "ranked_visit_list": Path("datasets/processed/ranked_visit_list.csv"),
    "recommendation_outputs": Path("datasets/processed/recommendation_outputs.csv"),
    "anomaly_alerts": Path("datasets/processed/anomaly_alerts.csv"),
    "explanation_outputs": Path("datasets/processed/explanation_outputs.csv"),
}


@dataclass(frozen=True)
class DemoCheck:
    name: str
    status: str
    detail: str


def verify_demo_workflow(repo_root: Path | None = None) -> list[DemoCheck]:
    root = repo_root or Path(__file__).resolve().parents[2]
    checks: list[DemoCheck] = []
    checks.extend(_check_required_files(root, REQUIRED_DEMO_DOCS, "demo docs"))
    checks.extend(_check_required_files(root, REQUIRED_FRONTEND_FILES, "frontend workflow"))
    checks.append(_check_api_routes())
    checks.extend(_check_processed_outputs(root))
    checks.extend(_check_fixed_scenario_rows(root))
    return checks


def has_blocking_failures(checks: list[DemoCheck]) -> bool:
    return any(check.status == "FAIL" for check in checks)


def checks_to_dicts(checks: list[DemoCheck]) -> list[dict[str, str]]:
    return [asdict(check) for check in checks]


def print_text_report(checks: list[DemoCheck]) -> None:
    print(f"Build 10 demo workflow verification: {SCENARIO_ID}")
    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")


def _check_required_files(
    repo_root: Path,
    relative_paths: tuple[str, ...],
    label: str,
) -> list[DemoCheck]:
    checks = []
    for relative_path in relative_paths:
        path = repo_root / relative_path
        status = "PASS" if path.exists() else "FAIL"
        detail = "present" if path.exists() else "missing"
        checks.append(DemoCheck(name=f"{label}: {relative_path}", status=status, detail=detail))
    return checks


def _check_api_routes() -> DemoCheck:
    route_paths = tuple(
        route.path
        for route in create_app().routes
        if isinstance(route, APIRoute)
    )
    if route_paths == EXPECTED_ROUTES:
        return DemoCheck(
            name="backend API route contract",
            status="PASS",
            detail="all Build 08 routes are registered in demo order",
        )
    return DemoCheck(
        name="backend API route contract",
        status="FAIL",
        detail=f"expected {EXPECTED_ROUTES}, found {route_paths}",
    )


def _check_processed_outputs(repo_root: Path) -> list[DemoCheck]:
    checks = []
    for name, relative_path in REQUIRED_PROCESSED_OUTPUTS.items():
        path = repo_root / relative_path
        if path.exists():
            checks.append(
                DemoCheck(
                    name=f"processed output: {name}",
                    status="PASS",
                    detail=str(relative_path),
                )
            )
        else:
            checks.append(
                DemoCheck(
                    name=f"processed output: {name}",
                    status="WARN",
                    detail=f"{relative_path} is not available yet",
                )
            )
    return checks


def _check_fixed_scenario_rows(repo_root: Path) -> list[DemoCheck]:
    checks: list[DemoCheck] = []
    ranked_path = repo_root / REQUIRED_PROCESSED_OUTPUTS["ranked_visit_list"]
    if not ranked_path.exists():
        return [
            DemoCheck(
                name="fixed scenario daily plan rows",
                status="WARN",
                detail="cannot verify rows until ranked_visit_list.csv exists",
            )
        ]

    ranked_rows = _read_csv_rows(ranked_path)
    matching_rows = [
        row
        for row in ranked_rows
        if row.get("rep_id") == REP_ID
        and row.get("territory_id") == TERRITORY_ID
        and row.get("date") == PLAN_DATE
    ]
    if not matching_rows:
        return [
            DemoCheck(
                name="fixed scenario daily plan rows",
                status="WARN",
                detail=f"no rows found for {REP_ID}, {TERRITORY_ID}, {PLAN_DATE}",
            )
        ]

    top_entity_id = _top_entity_id(matching_rows)
    checks.append(
        DemoCheck(
            name="fixed scenario daily plan rows",
            status="PASS",
            detail=f"{len(matching_rows)} row(s), top entity {top_entity_id}",
        )
    )
    checks.append(
        _check_entity_rows(
            repo_root / REQUIRED_PROCESSED_OUTPUTS["recommendation_outputs"],
            "recommendation rows for top entity",
            top_entity_id,
        )
    )
    checks.append(
        _check_entity_rows(
            repo_root / REQUIRED_PROCESSED_OUTPUTS["explanation_outputs"],
            "explanation rows for top entity",
            top_entity_id,
        )
    )
    checks.append(_check_alert_rows(repo_root / REQUIRED_PROCESSED_OUTPUTS["anomaly_alerts"]))
    return checks


def _check_entity_rows(path: Path, name: str, entity_id: str) -> DemoCheck:
    if not path.exists():
        return DemoCheck(name=name, status="WARN", detail=f"{path.name} is not available yet")
    rows = _read_csv_rows(path)
    matching_rows = [row for row in rows if row.get("entity_id") == entity_id]
    if matching_rows:
        return DemoCheck(name=name, status="PASS", detail=f"{len(matching_rows)} row(s)")
    return DemoCheck(name=name, status="WARN", detail=f"no rows found for {entity_id}")


def _check_alert_rows(path: Path) -> DemoCheck:
    if not path.exists():
        return DemoCheck(
            name="alert rows for fixed territory",
            status="WARN",
            detail=f"{path.name} is not available yet",
        )
    rows = _read_csv_rows(path)
    matching_rows = [row for row in rows if row.get("territory_id") == TERRITORY_ID]
    if matching_rows:
        return DemoCheck(name="alert rows for fixed territory", status="PASS", detail=f"{len(matching_rows)} row(s)")
    return DemoCheck(
        name="alert rows for fixed territory",
        status="WARN",
        detail=f"no rows found for {TERRITORY_ID}",
    )


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _top_entity_id(rows: list[dict[str, str]]) -> str:
    def sort_key(row: dict[str, str]) -> tuple[int, float, str]:
        rank = _int_or_default(row.get("rank"), 999999)
        priority_score = _float_or_default(row.get("priority_score"), 0.0)
        return (rank, -priority_score, row.get("entity_id", ""))

    sorted_rows = sorted(rows, key=sort_key)
    return sorted_rows[0].get("entity_id", "")


def _int_or_default(value: str | None, default: int) -> int:
    try:
        return int(float(value or ""))
    except ValueError:
        return default


def _float_or_default(value: str | None, default: float) -> float:
    try:
        return float(value or "")
    except ValueError:
        return default


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify KshetraAI demo workflow readiness.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args()

    checks = verify_demo_workflow()
    if args.json:
        print(json.dumps(checks_to_dicts(checks), indent=2))
    else:
        print_text_report(checks)
    return 1 if has_blocking_failures(checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
