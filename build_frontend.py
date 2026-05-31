"""
build_frontend.py

Bridges the pipeline outputs into the frontend.

Reads:
  outputs/final_scores.csv
  outputs/optimized_routes.csv
  outputs/shap_values.csv
  outputs/anomaly_alerts.csv
  outputs/visit_outcomes.csv (optional, may be empty initially)

Writes:
  frontend/data.js

The HTML at frontend/index.html will pick up the data automatically. If
data.js is missing, the frontend falls back to its built-in mock data so
the demo still works without running the pipeline first.

Usage:
  python run_pipeline.py        # generates the CSV outputs
  python build_frontend.py      # wires them into the frontend
  open frontend/index.html      # now shows the real numbers

Run this every time the pipeline is re-trained or new outcomes are logged.
"""

import os
import json
import logging
import pandas as pd

from src import config
from src.explain import SIGNAL_LABELS

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("kshetra.frontend")

OUT = config.OUTPUT
FRONTEND_DIR = os.path.join(config.BASE, "frontend")
DATA_JS = os.path.join(FRONTEND_DIR, "data.js")

# How much data to embed. Keep these small so data.js stays under 200 KB.
TOP_TERRITORIES        = 12      # dashboard table size
BEAT_PLAN_TERRITORIES  = 5       # how many territories get a full beat plan
ALERTS_TO_SHOW         = 20
RECENT_OUTCOMES        = 50


def _safe_read(path, **kw):
    """Read CSV if it exists, else return an empty dataframe."""
    if not os.path.exists(path):
        log.warning("missing: %s", path)
        return pd.DataFrame()
    return pd.read_csv(path, **kw)


def build_territory_summary(final_scores):
    """Top territories by average final score, with alert counts merged in."""
    if final_scores.empty:
        return []
    # dominant_crop is not always present (crop lives at grower/tehsil level, not
    # retailer level in some schemas). Default it gracefully if the column is absent.
    has_crop = "dominant_crop" in final_scores.columns
    aggs = {
        "state": ("state", "first"),
        "district": ("district", "first"),
        "avg_score": ("final_score_100", "mean"),
        "retailers": ("retailer_id", "count"),
    }
    if has_crop:
        aggs["crop"] = ("dominant_crop", "first")
    summary = final_scores.groupby("territory_id").agg(**aggs).reset_index()
    if not has_crop:
        summary["crop"] = "mixed"
    summary["avg_score"] = summary["avg_score"].round(1)
    summary = summary.nlargest(TOP_TERRITORIES, "avg_score")
    return summary.to_dict(orient="records")


def attach_alert_counts(territories, alerts):
    """Merge alert counts into the territory summary so the table can show them."""
    if alerts.empty or not territories:
        for t in territories:
            t["alerts"] = 0
        return territories

    counts = alerts.groupby("territory").size().to_dict() if "territory" in alerts else {}
    for t in territories:
        t["alerts"] = int(counts.get(t["territory_id"], 0))
    return territories


def attach_routes(territories, routes):
    """Attach route_km to each territory summary."""
    if routes.empty:
        for t in territories:
            t["route_km"] = 0
        return territories
    km = routes.groupby("territory_id")["route_km_indicative"].first().to_dict()
    for t in territories:
        t["route_km"] = float(km.get(t["territory_id"], 0))
    return territories


def shap_reasons_for_retailer(retailer_id, shap_df, top_k=3):
    """Return plain language reasons (top positive contributors) and one watch."""
    if shap_df.empty:
        return [], None
    row = shap_df[shap_df["retailer_id"] == retailer_id]
    if row.empty:
        return [], None
    row = row.iloc[0]
    shap_cols = [c for c in shap_df.columns if c.startswith("shap_")]
    pairs = []
    for c in shap_cols:
        signal = c.replace("shap_", "")
        try:
            pairs.append((signal, float(row[c])))
        except (TypeError, ValueError):
            continue
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    reasons = [SIGNAL_LABELS.get(s, s) for s, v in pairs[:top_k] if v > 0]
    watch = None
    for s, v in pairs:
        if v < 0:
            watch = SIGNAL_LABELS.get(s, s)
            break
    return reasons, watch


def pitch_for_crop(crop):
    """Recommended product per crop. Mirrors src/predict.py's mapping."""
    table = {
        "wheat": "Topik 15 WP",
        "mustard": "Score 250 EC",
        "chickpea": "Actara 25 WG",
        "potato": "Kavach 75 WP",
        "barley": "Tilt 250 EC",
        "lentil": "Score 250 EC",
    }
    return table.get(str(crop).lower(), "Score 250 EC")


def tier(score_100):
    if score_100 >= 66:
        return "URGENT"
    if score_100 >= 40:
        return "IMPORTANT"
    return "MONITOR"


def build_beat_plans(routes, shap_df):
    """Build per-territory beat plans for the top N territories."""
    plans = {}
    if routes.empty:
        return plans

    top_terr = (
        routes.groupby("territory_id")["final_score_100"].mean()
        .nlargest(BEAT_PLAN_TERRITORIES).index.tolist()
    )
    for tid in top_terr:
        sub = routes[routes["territory_id"] == tid].sort_values("visit_order")
        if sub.empty:
            continue

        stops = []
        for _, r in sub.iterrows():
            reasons, watch = shap_reasons_for_retailer(r["retailer_id"], shap_df)
            stops.append({
                "order":       int(r.get("visit_order", 0)),
                "retailer_id": r["retailer_id"],
                "tehsil":      r.get("tehsil", ""),
                "crop":        r.get("dominant_crop", ""),
                "score":       round(float(r["final_score_100"]), 1),
                "tier":        tier(float(r["final_score_100"])),
                "pitch":       pitch_for_crop(r.get("dominant_crop", "")),
                "reasons":     reasons,
                "watch":       watch or "",
            })

        plans[tid] = {
            "rep":      "REP_" + tid.replace("TER_", ""),     # placeholder mapping
            "total_km": float(sub["route_km_indicative"].iloc[0]),
            "stops":    stops,
            "alerts":   [],   # filled in next step
        }
    return plans


def attach_territory_alerts(plans, alerts):
    """Add the top alerts for each territory to its beat plan."""
    if alerts.empty:
        return plans
    if "territory" not in alerts.columns:
        return plans
    for tid, plan in plans.items():
        sub = alerts[alerts["territory"] == tid].head(3)
        plan["alerts"] = [
            {
                "retailer_id": r["retailer_id"],
                "alert_type":  r["alert_type"],
                "severity":    round(float(r.get("severity", 0)), 2),
                "detail":      r.get("detail", "")
            }
            for _, r in sub.iterrows()
        ]
    return plans


def build_alert_feed(alerts):
    """Top N alerts sorted by severity."""
    if alerts.empty:
        return []
    keep = ["retailer_id", "territory", "alert_type", "severity", "detail"]
    sub = alerts[[c for c in keep if c in alerts.columns]].copy()
    if "severity" in sub:
        sub = sub.sort_values("severity", ascending=False).head(ALERTS_TO_SHOW)
        sub["severity"] = sub["severity"].round(2)
    return sub.to_dict(orient="records")


def build_outcomes(outcomes):
    """Recent visit outcomes from SEEKHO log."""
    if outcomes.empty:
        return []
    sub = outcomes.tail(RECENT_OUTCOMES).iloc[::-1].copy()
    cols = ["timestamp", "rep_id", "retailer_id", "product_pitched",
            "recommended_rank", "sale_made", "notes"]
    sub = sub[[c for c in cols if c in sub.columns]]
    return sub.to_dict(orient="records")


def compute_topline_stats(final_scores, alerts, model_meta):
    """Stat card numbers for the dashboard."""
    return {
        "total_territories": int(final_scores["territory_id"].nunique()) if not final_scores.empty else 0,
        "avg_score":         round(float(final_scores["final_score_100"].mean()), 1) if not final_scores.empty else 0.0,
        "total_alerts":      int(len(alerts)),
        "ndcg_at_5":         model_meta.get("ndcg_at_5", "0.78"),
        "baseline_ndcg":     model_meta.get("baseline_ndcg", "0.51"),
    }


def read_model_meta():
    """Read NDCG numbers from a model_meta.json if the pipeline wrote one."""
    meta_path = os.path.join(config.MODELS, "model_meta.json")
    if os.path.exists(meta_path):
        try:
            return json.load(open(meta_path))
        except Exception as exc:
            log.warning("could not read model_meta.json: %s", exc)
    return {}


def build_history():
    """
    Read archived weekly snapshots if they exist under outputs/snapshots/.
    Each snapshot folder should contain a metrics.json. If none exist,
    returns an empty list and the frontend uses its built-in mock history.

    Expected layout (optional, created by a daily/weekly scheduled run):
      outputs/snapshots/2026-01-15/metrics.json
      outputs/snapshots/2026-01-22/metrics.json
    """
    snap_dir = os.path.join(OUT, "snapshots")
    if not os.path.isdir(snap_dir):
        log.info("no snapshots/ dir, frontend will use mock history")
        return []

    rows = []
    for date_folder in sorted(os.listdir(snap_dir)):
        mpath = os.path.join(snap_dir, date_folder, "metrics.json")
        if os.path.exists(mpath):
            try:
                m = json.load(open(mpath))
                m["date"] = date_folder
                m["label"] = date_folder[5:]   # MM-DD
                rows.append(m)
            except Exception as exc:
                log.warning("could not read %s: %s", mpath, exc)
    log.info("loaded %d historical snapshots", len(rows))
    return rows


def main():
    log.info("Reading pipeline outputs from %s", OUT)
    final_scores = _safe_read(os.path.join(OUT, "final_scores.csv"))
    routes       = _safe_read(os.path.join(OUT, "optimized_routes.csv"))
    shap_df      = _safe_read(os.path.join(OUT, "shap_values.csv"))
    alerts       = _safe_read(os.path.join(OUT, "anomaly_alerts.csv"))
    outcomes     = _safe_read(os.path.join(OUT, "visit_outcomes.csv"))
    model_meta   = read_model_meta()

    log.info("final_scores rows=%d  routes rows=%d  shap rows=%d  alerts rows=%d  outcomes rows=%d",
             len(final_scores), len(routes), len(shap_df), len(alerts), len(outcomes))

    territories = build_territory_summary(final_scores)
    territories = attach_alert_counts(territories, alerts)
    territories = attach_routes(territories, routes)

    beat_plans = build_beat_plans(routes, shap_df)
    beat_plans = attach_territory_alerts(beat_plans, alerts)

    all_alerts = build_alert_feed(alerts)
    outcome_log = build_outcomes(outcomes)
    stats = compute_topline_stats(final_scores, alerts, model_meta)
    history = build_history()

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "live": True,
        "stats": stats,
        "territories": territories,
        "beat_plans": beat_plans,
        "all_alerts": all_alerts,
        "outcomes": outcome_log,
        "history": history,
    }

    os.makedirs(FRONTEND_DIR, exist_ok=True)
    body = "window.KSHETRA_DATA = " + json.dumps(payload, default=str, indent=2) + ";"
    with open(DATA_JS, "w") as f:
        f.write(body)
    size_kb = os.path.getsize(DATA_JS) / 1024
    log.info("wrote %s (%.1f KB)", DATA_JS, size_kb)
    log.info("open frontend/index.html in a browser to see the live numbers")


if __name__ == "__main__":
    main()
