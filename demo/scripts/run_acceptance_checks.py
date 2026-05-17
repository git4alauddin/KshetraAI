"""Run Build 10 demo acceptance checks.

The checks validate committed, sanitized demo artifacts and the current
integration wiring. They do not read raw private data and do not mutate any
backend, frontend, or dataset files.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from demo.scripts.verify_demo_workflow import (
    PLAN_DATE,
    REP_ID,
    TERRITORY_ID,
    checks_to_dicts,
    has_blocking_failures,
    verify_demo_workflow,
)


SAMPLE_OUTPUT_DIR = Path("demo/sample_outputs")
SCENARIO_DOC = Path("demo/scenarios/amritsar_crop_protection_scenario.md")
PRESENTATION_SCRIPT = Path("demo/presentation_notes/demo_script.md")
PRESENTATION_CHECKLIST = Path("demo/presentation_notes/demo_checklist.md")
EXPECTED_ENTITY_ID = "RTL_01300"

REQUIRED_SAMPLE_OUTPUTS = (
    "daily_plan_response.json",
    "recommendation_response.json",
    "alerts_response.json",
    "explanation_response.json",
    "outcome_submission_response.json",
)

FORBIDDEN_SAMPLE_FIELDS = {
    "phone",
    "mobile",
    "address",
    "latitude",
    "longitude",
    "tehsil_list",
    "grower_crop_calendar",
}


@dataclass(frozen=True)
class AcceptanceCheck:
    name: str
    status: str
    detail: str


def run_acceptance_checks(repo_root: Path | None = None) -> list[AcceptanceCheck]:
    root = repo_root or REPO_ROOT
    checks: list[AcceptanceCheck] = []
    checks.extend(_workflow_checks(root))
    checks.extend(_sample_output_file_checks(root))
    checks.extend(_sample_payload_shape_checks(root))
    checks.extend(_presentation_doc_checks(root))
    checks.append(_sample_sanitization_check(root))
    return checks


def has_acceptance_failures(checks: list[AcceptanceCheck]) -> bool:
    return any(check.status == "FAIL" for check in checks)


def acceptance_checks_to_dicts(checks: list[AcceptanceCheck]) -> list[dict[str, str]]:
    return [asdict(check) for check in checks]


def print_acceptance_report(checks: list[AcceptanceCheck]) -> None:
    print("Build 10 acceptance checks")
    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")


def _workflow_checks(repo_root: Path) -> list[AcceptanceCheck]:
    workflow_checks = verify_demo_workflow(repo_root)
    status = "FAIL" if has_blocking_failures(workflow_checks) else "PASS"
    detail = "workflow verifier has no blocking failures"
    if status == "FAIL":
        failing = [check for check in workflow_checks if check.status == "FAIL"]
        detail = "; ".join(f"{check.name}: {check.detail}" for check in failing)
    return [
        AcceptanceCheck(
            name="demo workflow verifier",
            status=status,
            detail=detail,
        )
    ]


def _sample_output_file_checks(repo_root: Path) -> list[AcceptanceCheck]:
    checks = []
    for file_name in REQUIRED_SAMPLE_OUTPUTS:
        path = repo_root / SAMPLE_OUTPUT_DIR / file_name
        checks.append(
            AcceptanceCheck(
                name=f"sample output: {file_name}",
                status="PASS" if path.exists() else "FAIL",
                detail="present" if path.exists() else "missing",
            )
        )
    return checks


def _sample_payload_shape_checks(repo_root: Path) -> list[AcceptanceCheck]:
    sample_dir = repo_root / SAMPLE_OUTPUT_DIR
    checks = [
        _daily_plan_shape(sample_dir / "daily_plan_response.json"),
        _recommendation_shape(sample_dir / "recommendation_response.json"),
        _alerts_shape(sample_dir / "alerts_response.json"),
        _explanation_shape(sample_dir / "explanation_response.json"),
        _outcome_shape(sample_dir / "outcome_submission_response.json"),
    ]
    return checks


def _daily_plan_shape(path: Path) -> AcceptanceCheck:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        return AcceptanceCheck("daily plan payload", "FAIL", "not a JSON object")
    ranked_entities = payload.get("ranked_entities")
    if (
        payload.get("rep_id") == REP_ID
        and payload.get("territory_id") == TERRITORY_ID
        and payload.get("date") == PLAN_DATE
        and isinstance(ranked_entities, list)
        and ranked_entities
        and ranked_entities[0].get("entity_id") == EXPECTED_ENTITY_ID
    ):
        return AcceptanceCheck("daily plan payload", "PASS", "fixed scenario top entity is stable")
    return AcceptanceCheck("daily plan payload", "FAIL", "fixed scenario response is not stable")


def _recommendation_shape(path: Path) -> AcceptanceCheck:
    payload = _load_json(path)
    if (
        isinstance(payload, dict)
        and payload.get("entity_id") == EXPECTED_ENTITY_ID
        and payload.get("risk_or_opportunity")
        and isinstance(payload.get("recommended_actions"), list)
        and payload.get("recommended_actions")
        and payload.get("confidence_level")
    ):
        return AcceptanceCheck("recommendation payload", "PASS", "recommendation is actionable")
    return AcceptanceCheck("recommendation payload", "FAIL", "recommendation response is incomplete")


def _alerts_shape(path: Path) -> AcceptanceCheck:
    payload = _load_json(path)
    alerts = payload.get("alerts") if isinstance(payload, dict) else None
    if isinstance(alerts, list) and any(alert.get("entity_id") == EXPECTED_ENTITY_ID for alert in alerts):
        return AcceptanceCheck("alerts payload", "PASS", "scenario entity has alert evidence")
    return AcceptanceCheck("alerts payload", "FAIL", "scenario entity alert is missing")


def _explanation_shape(path: Path) -> AcceptanceCheck:
    payload = _load_json(path)
    explanations = payload.get("explanations") if isinstance(payload, dict) else None
    explanation_types = {
        explanation.get("explanation_type")
        for explanation in explanations or []
        if isinstance(explanation, dict)
    }
    if payload.get("entity_id") == EXPECTED_ENTITY_ID and {"priority", "recommendation", "anomaly"}.issubset(explanation_types):
        return AcceptanceCheck("explanation payload", "PASS", "priority, recommendation, and anomaly explanations exist")
    return AcceptanceCheck("explanation payload", "FAIL", "required explanation types are missing")


def _outcome_shape(path: Path) -> AcceptanceCheck:
    payload = _load_json(path)
    if (
        isinstance(payload, dict)
        and payload.get("status") == "success"
        and payload.get("outcome_id")
        and payload.get("message")
    ):
        return AcceptanceCheck("outcome payload", "PASS", "outcome confirmation is available")
    return AcceptanceCheck("outcome payload", "FAIL", "outcome confirmation is incomplete")


def _presentation_doc_checks(repo_root: Path) -> list[AcceptanceCheck]:
    checks = []
    required_docs = (SCENARIO_DOC, PRESENTATION_SCRIPT, PRESENTATION_CHECKLIST)
    required_terms = (REP_ID, TERRITORY_ID, PLAN_DATE, EXPECTED_ENTITY_ID)
    for relative_path in required_docs:
        path = repo_root / relative_path
        if not path.exists():
            checks.append(AcceptanceCheck(f"presentation doc: {relative_path}", "FAIL", "missing"))
            continue
        text = path.read_text(encoding="utf-8")
        missing_terms = [term for term in required_terms if term not in text]
        checks.append(
            AcceptanceCheck(
                name=f"presentation doc: {relative_path}",
                status="PASS" if not missing_terms else "FAIL",
                detail="scenario references present" if not missing_terms else "missing " + ", ".join(missing_terms),
            )
        )
    return checks


def _sample_sanitization_check(repo_root: Path) -> AcceptanceCheck:
    sample_dir = repo_root / SAMPLE_OUTPUT_DIR
    combined_payload = ""
    for file_name in REQUIRED_SAMPLE_OUTPUTS:
        path = sample_dir / file_name
        if path.exists():
            combined_payload += path.read_text(encoding="utf-8").lower()
    forbidden_hits = sorted(field for field in FORBIDDEN_SAMPLE_FIELDS if field in combined_payload)
    if forbidden_hits:
        return AcceptanceCheck(
            name="sample output sanitization",
            status="FAIL",
            detail="forbidden raw fields found: " + ", ".join(forbidden_hits),
        )
    return AcceptanceCheck("sample output sanitization", "PASS", "no forbidden raw fields found")


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    checks = run_acceptance_checks()
    print_acceptance_report(checks)
    return 1 if has_acceptance_failures(checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
