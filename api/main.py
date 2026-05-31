"""
api/main.py

A small REST API around the trained model so the recommendations can be served
instead of just dumped to CSV. This is the production face of the project. It
loads the model once at startup and answers requests.

Endpoints:
  GET  /health                       is the service up
  GET  /territory/{id}/beat-plan      ranked visit list for a territory
  GET  /retailer/{id}/score           score and explanation for one retailer
  POST /retailer/{id}/next-action     SALAH recommendation (LLM or fallback)
  POST /outcome                       log a visit outcome into SEEKHO
  GET  /eval                          current evaluation report

Run it:
    uvicorn api.main:app --reload --port 8000

Then open http://localhost:8000/docs for the interactive Swagger UI.

Everything is traced through observability.get_tracer() so if Langfuse is
configured you can watch requests come through.
"""

import os
import sys
import logging
from typing import Optional

# make src importable when run as uvicorn api.main:app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src import config
from src.observability import get_tracer

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("kshetra.api")

app = FastAPI(
    title="KshetraAI",
    description="Field force intelligence. Ranks retailers, explains why, suggests the pitch.",
    version="1.0.0",
)

tracer = get_tracer()

# Loaded lazily on first request so the API starts even before a pipeline run.
_state = {"scores": None, "shap": None, "routes": None, "model": None}


def _load_outputs():
    import pandas as pd
    if _state["scores"] is None:
        for key, fname in [("scores", "final_scores.csv"), ("shap", "shap_values.csv"),
                           ("routes", "optimized_routes.csv")]:
            path = os.path.join(config.OUTPUT, fname)
            _state[key] = pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
    return _state


class OutcomeIn(BaseModel):
    rep_id: str
    retailer_id: str
    product_pitched: str
    sale_made: bool
    recommended_rank: Optional[int] = None
    notes: Optional[str] = ""


class NextActionIn(BaseModel):
    language: str = "english"


@app.get("/health")
def health():
    return {"status": "ok", "tracing": tracer.enabled}


@app.get("/territory/{territory_id}/beat-plan")
def beat_plan(territory_id: str):
    span = tracer.start("api.beat_plan", {"territory_id": territory_id})
    s = _load_outputs()
    routes = s["routes"]
    if routes.empty:
        span.end({"error": "no outputs"})
        raise HTTPException(503, "no pipeline outputs yet, run python run_pipeline.py first")
    sub = routes[routes["territory_id"] == territory_id].sort_values("visit_order")
    if sub.empty:
        span.end({"error": "not found"})
        raise HTTPException(404, f"no plan for {territory_id}")
    span.end({"stops": len(sub)})
    return {"territory_id": territory_id, "stops": sub.to_dict(orient="records")}


@app.get("/retailer/{retailer_id}/score")
def retailer_score(retailer_id: str):
    span = tracer.start("api.retailer_score", {"retailer_id": retailer_id})
    s = _load_outputs()
    scores, shap = s["scores"], s["shap"]
    if scores.empty:
        span.end({"error": "no outputs"})
        raise HTTPException(503, "no pipeline outputs yet")
    row = scores[scores["retailer_id"] == retailer_id]
    if row.empty:
        span.end({"error": "not found"})
        raise HTTPException(404, f"no score for {retailer_id}")
    result = row.iloc[0].to_dict()
    if not shap.empty:
        srow = shap[shap["retailer_id"] == retailer_id]
        if not srow.empty:
            shap_cols = [c for c in shap.columns if c.startswith("shap_")]
            contribs = {c.replace("shap_", ""): float(srow.iloc[0][c]) for c in shap_cols}
            result["explanation"] = dict(sorted(contribs.items(), key=lambda x: abs(x[1]), reverse=True))
    span.end({"score": result.get("final_score_100")})
    return result


@app.post("/retailer/{retailer_id}/next-action")
def next_action(retailer_id: str, body: NextActionIn):
    from src import salah_agent
    s = _load_outputs()
    scores = s["scores"]
    if scores.empty:
        raise HTTPException(503, "no pipeline outputs yet")
    row = scores[scores["retailer_id"] == retailer_id]
    if row.empty:
        raise HTTPException(404, f"no retailer {retailer_id}")
    rec = salah_agent.recommend(row.iloc[0].to_dict(), language=body.language, trace=tracer)
    return {"retailer_id": retailer_id, "recommendation": rec}


@app.post("/outcome")
def log_outcome(o: OutcomeIn):
    from src import feedback
    feedback.log_visit_outcome(
        rep_id=o.rep_id, retailer_id=o.retailer_id, product_pitched=o.product_pitched,
        sale_made=o.sale_made, recommended_rank=o.recommended_rank, notes=o.notes,
    )
    return {"logged": True, "retailer_id": o.retailer_id}


@app.get("/eval")
def evaluation():
    from src import evaluation
    return evaluation.run_full_eval()
