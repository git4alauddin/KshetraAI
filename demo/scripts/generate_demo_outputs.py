"""Generate deterministic Build 10 demo outputs from local private data.

This script reads ignored company-provided source CSV files from `private-data/`
and writes derived outputs only:

- ignored processed CSVs under `datasets/processed/`
- sanitized API-level sample JSON files under `demo/sample_outputs/`

It does not edit raw private data or change core intelligence logic.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.anomaly.anomaly_engine import build_anomaly_outputs
from backend.api.schemas.outcome_schema import OutcomeSubmissionRequest
from backend.api.services.anomaly_service import get_alerts_response
from backend.api.services.explainability_service import get_explanation_response
from backend.api.services.outcome_service import submit_outcome_response
from backend.api.services.planning_service import get_daily_plan_response
from backend.api.services.recommendation_service import get_recommendation_response
from backend.engines.contextual_decision_engine import build_contextual_decision_output_views
from backend.engines.priority_engine import build_ranked_priority_view
from backend.explainability.evidence_mapper import build_evidence_view
from backend.explainability.explanation_engine import (
    build_explanation_trace_view,
    build_explanation_view,
)
from backend.features.feature_pipeline import (
    build_combined_feature_view,
    build_feature_output_views,
    write_feature_output_views,
)
from backend.pipelines.pipeline_runner import Build01PipelineConfig, run_build01_pipeline


REP_ID = "REP_0164"
TERRITORY_ID = "TER_0164"
PLAN_DATE = "2026-05-17"
SOURCE_DIR = Path("private-data")
PROCESSED_DIR = Path("datasets/processed")
SAMPLE_OUTPUT_DIR = Path("demo/sample_outputs")


def generate_demo_outputs(
    *,
    source_dir: Path = SOURCE_DIR,
    processed_dir: Path = PROCESSED_DIR,
    sample_output_dir: Path = SAMPLE_OUTPUT_DIR,
) -> dict[str, Any]:
    """Generate processed and sanitized sample outputs for the demo scenario."""

    processed_dir.mkdir(parents=True, exist_ok=True)
    sample_output_dir.mkdir(parents=True, exist_ok=True)

    pipeline_result = run_build01_pipeline(
        Build01PipelineConfig(
            source_dir=source_dir,
            output_dir=processed_dir,
            write_outputs=True,
        )
    )
    combined_feature_view = build_combined_feature_view(pipeline_result.canonical_views)
    feature_views = build_feature_output_views(pipeline_result.canonical_views)
    write_feature_output_views(feature_views, processed_dir)

    ranked_visit_list = _prepare_ranked_visit_list(
        build_ranked_priority_view(combined_feature_view),
        pipeline_result.canonical_views["representatives"],
    )
    contextual_view = combined_feature_view.merge(
        ranked_visit_list[["entity_id", "priority_score", "priority_level"]],
        on="entity_id",
        how="left",
    )
    contextual_outputs = build_contextual_decision_output_views(contextual_view)
    anomaly_outputs = build_anomaly_outputs(combined_feature_view)
    scenario_entity_id = _scenario_entity_id(ranked_visit_list)
    explanation_outputs = _build_explanation_outputs(
        ranked_visit_list,
        contextual_outputs["recommendation_outputs"],
        anomaly_outputs.anomaly_alerts,
        entity_id=scenario_entity_id,
    )

    output_views = {
        "combined_feature_view": combined_feature_view,
        "ranked_visit_list": ranked_visit_list,
        **contextual_outputs,
        **anomaly_outputs.to_mapping(),
        **explanation_outputs,
    }
    _write_output_views(output_views, processed_dir)

    scenario_recommendation = get_recommendation_response(scenario_entity_id)
    scenario_alerts = get_alerts_response(territory_id=TERRITORY_ID)
    scenario_alert_id = scenario_alerts.alerts[0].alert_id if scenario_alerts.alerts else ""
    sample_payloads = {
        "daily_plan_response": get_daily_plan_response(
            rep_id=REP_ID,
            territory_id=TERRITORY_ID,
            date=PLAN_DATE,
        ).model_dump(mode="json"),
        "recommendation_response": scenario_recommendation.model_dump(mode="json"),
        "alerts_response": scenario_alerts.model_dump(mode="json"),
        "explanation_response": get_explanation_response(scenario_entity_id).model_dump(mode="json"),
        "outcome_submission_response": submit_outcome_response(
            OutcomeSubmissionRequest(
                recommendation_id=scenario_recommendation.risk_or_opportunity,
                entity_id=scenario_entity_id,
                rep_id=REP_ID,
                visit_completed=True,
                recommendation_followed=True,
                sale_made=True,
                order_placed=True,
                order_value=25000,
                alert_validated=True,
                feedback_category="useful",
                rep_feedback="Retailer confirmed demand and requested follow-up stock planning.",
                alert_id=scenario_alert_id,
            )
        ).model_dump(mode="json"),
    }
    _write_sample_outputs(sample_payloads, sample_output_dir)

    return {
        "scenario": {
            "rep_id": REP_ID,
            "territory_id": TERRITORY_ID,
            "date": PLAN_DATE,
            "entity_id": scenario_entity_id,
        },
        "processed_outputs": sorted(output_views),
        "sample_outputs": sorted(sample_payloads),
    }


def _prepare_ranked_visit_list(
    ranked_visit_list: pd.DataFrame,
    representatives: pd.DataFrame,
) -> pd.DataFrame:
    territory_rep_map = representatives.loc[:, ["rep_id", "territory_id"]].drop_duplicates()
    output = ranked_visit_list.merge(territory_rep_map, on="territory_id", how="left")
    output["date"] = PLAN_DATE
    output["entity_name"] = output["entity_id"]
    output["main_reason"] = output["component_scores"].map(_main_reason)
    return output


def _main_reason(component_scores: Any) -> str:
    if not isinstance(component_scores, dict) or not component_scores:
        return ""
    component_name, score = sorted(
        component_scores.items(),
        key=lambda item: (-float(item[1]), str(item[0])),
    )[0]
    return f"Highest signal: {component_name.replace('_', ' ')} ({round(float(score), 2)})"


def _build_explanation_outputs(
    ranked_visit_list: pd.DataFrame,
    recommendation_outputs: pd.DataFrame,
    anomaly_alerts: pd.DataFrame,
    *,
    entity_id: str,
) -> dict[str, pd.DataFrame]:
    explainable_recommendations = recommendation_outputs[
        recommendation_outputs["matched_rule_id"] != "NO_CONTEXTUAL_RULE_MATCH"
    ].copy()
    ranked_visit_list = ranked_visit_list[ranked_visit_list["entity_id"] == entity_id].copy()
    explainable_recommendations = explainable_recommendations[
        explainable_recommendations["entity_id"] == entity_id
    ].copy()
    anomaly_alerts = anomaly_alerts[anomaly_alerts["entity_id"] == entity_id].copy()
    evidence_views = [
        build_evidence_view(ranked_visit_list, "priority"),
        build_evidence_view(explainable_recommendations, "recommendation"),
        build_evidence_view(anomaly_alerts, "anomaly"),
    ]
    evidence_view = pd.concat(evidence_views, ignore_index=True)
    explanation_view = build_explanation_view(evidence_view)
    return {
        "evidence_view": evidence_view,
        "explanation_outputs": explanation_view,
        "explanation_trace_log": build_explanation_trace_view(evidence_view),
    }


def _scenario_entity_id(ranked_visit_list: pd.DataFrame) -> str:
    scenario_rows = ranked_visit_list[
        (ranked_visit_list["rep_id"] == REP_ID)
        & (ranked_visit_list["territory_id"] == TERRITORY_ID)
        & (ranked_visit_list["date"] == PLAN_DATE)
    ].sort_values("rank", kind="mergesort")
    if scenario_rows.empty:
        raise RuntimeError(f"No ranked visit rows found for {REP_ID}, {TERRITORY_ID}, {PLAN_DATE}.")
    return str(scenario_rows.iloc[0]["entity_id"])


def _write_output_views(output_views: dict[str, pd.DataFrame], output_dir: Path) -> None:
    for view_name, dataframe in output_views.items():
        _serialize_complex_columns(dataframe).to_csv(
            output_dir / f"{view_name}.csv",
            index=False,
            lineterminator="\n",
        )


def _write_sample_outputs(sample_payloads: dict[str, Any], output_dir: Path) -> None:
    for name, payload in sample_payloads.items():
        path = output_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _serialize_complex_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    output = dataframe.copy()
    for column in output.columns:
        if output[column].map(lambda value: isinstance(value, (dict, list, tuple))).any():
            output[column] = output[column].map(_stable_json)
    return output


def _stable_json(value: Any) -> str:
    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value


def main() -> int:
    summary = generate_demo_outputs()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
