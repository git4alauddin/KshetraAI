"""
End to end pipeline. Run this after placing the eight raw CSV files in
<BASE>/raw_data/. It loads data, builds labels and features, trains the
LambdaRank ranker, scores every retailer, optimises routes, detects anomalies,
and writes outputs. Each stage prints a short status line.

    python run_pipeline.py
"""

import logging
import pandas as pd

from src import config, data_io, weather as weather_mod, labels, features
from src import ranker, scoring, route, anomaly, explain, backtest

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("kshetra.run")


def main():
    # 1. Load and clean
    data = data_io.load_all()
    retailers = data["retailers"]

    # 2. Weather, cached or fetched with retry
    weather = weather_mod.get_weather()

    # 3. Labels (product specific conversion within the sale window)
    labeled = labels.build_labels(data["visit_log"], retailers, data["pos"])

    # 4. Training features, point in time, same definitions as inference
    train_feats = features.build_training_features(labeled, retailers, data, weather)

    # Attach rep_id (one rep per territory) so the ranker can group visits by
    # rep and day, which is what makes NDCG@5 meaningful.
    reps = data["reps"][["rep_id", "territory_id"]].drop_duplicates()
    train_feats = train_feats.merge(reps, on="territory_id", how="left")

    split = pd.Timestamp(config.SPLIT_DATE)
    tr = train_feats[train_feats["visit_date"] < split]
    te = train_feats[train_feats["visit_date"] >= split]

    # 5. Train the ranker, report NDCG@5 and a baseline to compare against
    model, ndcg = ranker.train(tr, te)
    base = ranker.baseline_ndcg(te)
    log.info("NDCG@5  model=%.4f  baseline=%.4f", ndcg, base)

    cv = ranker.cross_validate(train_feats)
    log.info("Cross validation by month:\n%s", cv.to_string(index=False))
    ranker.save(model, f"{config.MODELS}/lambdarank.txt")

    # Save model meta so build_frontend.py can show the NDCG numbers in the UI
    import json
    with open(f"{config.MODELS}/model_meta.json", "w") as f:
        json.dump({
            "ndcg_at_5": round(float(ndcg), 4),
            "baseline_ndcg": round(float(base), 4) if base == base else None,  # NaN check
            "best_iteration": int(model.best_iteration) if model.best_iteration else None,
        }, f, indent=2)

    # 6. Score every retailer for the reference date
    inf = features.build_inference_features(retailers, data, weather)
    ml_scores = ranker.predict(model, inf)
    scored = scoring.hybrid_score(inf, ml_scores)
    scored.to_csv(f"{config.OUTPUT}/final_scores.csv", index=False)

    # 7. SHAP explanations for every retailer
    expl = explain.build_explainer(model)
    shap_df = explain.shap_table(expl, scored)
    shap_df.to_csv(f"{config.OUTPUT}/shap_values.csv", index=False)

    # 8. Routes per territory
    routes = []
    for tid in scored["territory_id"].unique():
        r = route.optimize_territory(scored, tid)
        if r is not None:
            routes.append(r)
    if routes:
        pd.concat(routes, ignore_index=True).to_csv(f"{config.OUTPUT}/optimized_routes.csv", index=False)

    # 9. Anomalies, priority ordered
    feed = anomaly.build_alert_feed(data["pos"])
    feed.to_csv(f"{config.OUTPUT}/anomaly_alerts.csv", index=False)

    # 10. Backtest the ranking against actual rep behaviour
    te_scored = te.copy()
    te_scored["final_score"] = ranker.predict(model, te_scored)
    bt = backtest.recall_at_k(te_scored, "final_score", k=config.VISITS_PER_TERRITORY)
    log.info("Backtest %s", bt)

    # 11. Run the evaluation suite (precision@k, faithfulness, acceptance, golden set)
    try:
        from src import evaluation
        import json as _json
        report = evaluation.run_full_eval()
        with open(f"{config.OUTPUT}/evaluation_report.json", "w") as f:
            _json.dump(report, f, indent=2, default=str)
        log.info("Evaluation report written. precision@k=%s",
                 report.get("precision_at_k", {}).get("precision_at_k"))
    except Exception as exc:
        log.warning("evaluation step failed: %s", exc)

    # 12. Generate a few SALAH next-best-action samples (LLM if key set, else fallback)
    try:
        from src import salah_agent
        from src.observability import get_tracer
        tracer = get_tracer()
        samples = scored.nlargest(3, "final_score_100").to_dict(orient="records")
        salah_samples = [salah_agent.recommend(r, language="hinglish", trace=tracer) for r in samples]
        with open(f"{config.OUTPUT}/salah_samples.json", "w") as f:
            import json as _json2
            _json2.dump(salah_samples, f, indent=2, ensure_ascii=False)
        tracer.flush()
        log.info("SALAH samples written (%d), source=%s",
                 len(salah_samples), salah_samples[0]["source"] if salah_samples else "none")
    except Exception as exc:
        log.warning("SALAH sample step failed: %s", exc)

    # 13. Wire outputs into the frontend so the dashboard shows real numbers
    try:
        import build_frontend
        build_frontend.main()
    except Exception as exc:
        log.warning("build_frontend step failed (frontend will use mock data): %s", exc)

    log.info("Pipeline complete. Outputs in %s", config.OUTPUT)
    log.info("Open frontend/index.html in a browser to see the dashboard.")


if __name__ == "__main__":
    main()
