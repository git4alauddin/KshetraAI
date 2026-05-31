# CHANGELOG

Engineering changes in this version, listed with the file that contains the fix.
Use this as a quick reference when walking through what changed and why.

## P0 -- Q&A critical

1. **Deck and code alignment.** Documentation and code now describe the same
   system. The deck described a LambdaRank model with NDCG@5 and Isolation
   Forest. The code now implements LambdaRank with NDCG@5 (`src/ranker.py`)
   and produces a priority ranked anomaly feed (`src/anomaly.py`). The NDVI
   claim is everywhere now labelled a proxy.

2. **Anomaly example honesty.** The fabricated "Score 250 EC at Rs.517 vs
   Rs.2,183" example is removed. The real Vertimec 1.8 EC at retailer
   RTL_03909 (Rs.382 to Rs.2,136, CV 0.70) is used in the documentation.
   See `docs/KshetraAI_Documentation.docx` section 8.

3. **ML weight on a coin-flip model.** Blend changed to 50 percent rule and
   50 percent ranker, both normalised to a common 0 to 1 scale before blending.
   See `src/config.py: RULE_BLEND_WEIGHT, ML_BLEND_WEIGHT` and
   `src/scoring.py: hybrid_score`.

## P1 -- Real bugs

4. **Demand spike unit mismatch.** Earlier code compared a monthly total to a
   per-day mean, flagging 90 percent of retailers. Now both sides are weekly
   rates. See `src/anomaly.py: demand_spikes`.

5. **Train vs inference feature drift.** Earlier code trained on per-visit
   time-varying features but scored production on static features. Now one
   shared function (`_assemble` in `src/features.py`) is called by both
   `build_training_features` and `build_inference_features`, each with the
   appropriate as-of date.

6. **Circular leakage.** Rule score was both a model feature and a 40 percent
   blend component. Now rule score is computed only in `src/scoring.py` and
   is not passed to the ranker. The model sees the nine raw signals only.

7. **Score-scale blend.** Rule score (0 to 0.6) and model score (0 to 1) used
   to blend with no normalisation. Now `_unit_scale` in `src/scoring.py`
   brings both to 0 to 1 before applying the weights.

8. **Binary to LambdaRank.** Objective changed from binary classifier to
   `lambdarank`, grouped by `rep_id, visit_date`, metric `ndcg_eval_at=[5]`.
   See `src/ranker.py: train`. NDCG@5 is now actually computed, not just
   targeted.

9. **Serving function.** `src/predict.py` adds `score_all`, `beat_plan`,
   and `score_one_retailer`. The earlier code saved the model with no way
   to call it for a live recommendation.

10. **Magic fill value.** `fillna(0.3)` replaced with `MISSING_FILL = 0.0` and
    a companion `<signal>_missing` flag column. See `src/config.py` and
    `src/features.py: _assemble`.

## P2 -- Model quality

11. **Uplift proxy.** `src/labels.py: uplift_proxy` provides a documented
    experimental approximation. Real causal uplift needs a control group,
    which this single season data does not contain. Labelled experimental
    everywhere it appears.

12. **Backtest vs business as usual.** `src/backtest.py: recall_at_k`
    reports, of the converters in each rep-day, how many the ranking would
    have placed in the top k. This is the figure that proves the system
    beats habitual routing.

13. **Overfitting defence.** Three changes in `src/ranker.py`: a baseline
    that ranks by recent sales velocity is computed alongside the model
    (`baseline_ndcg`), L1 (`reg_alpha=0.1`) and L2 (`reg_lambda=0.1`) added,
    and `min_child_samples=50`.

14. **Cross validation.** `src/ranker.py: cross_validate` runs expanding
    window CV across four test months instead of a single fold.

15. **Dead signals.** Reference date moved from 29 March (season end) to
    15 January (peak season) so the crop stage signal carries real signal.
    See `src/config.py: REFERENCE_DATE`. Configurable via env var
    `KSHETRA_REF_DATE`.

16. **Score range compressed.** `src/scoring.py: hybrid_score` applies a
    final min-max scaling so the score uses the full 0 to 100 range and
    the urgent / important / monitor tiers separate cleanly.

## P3 -- Claimed but not built

17. **SEEKHO feedback loop.** `src/feedback.py: log_visit_outcome` writes
    each rep outcome to a CSV with a fixed schema. `acceptance_rate` reads
    it back. The schema is the contract that lets a retraining job attach
    outcomes to the features that were shown at the time.

18. **Offline support.** `src/weather.py` caches weather to disk so the
    pipeline runs even when the network is down. Full offline-first mobile
    is still on the roadmap, honestly labelled.

19. **SALAH next best action.** The hardcoded crop-to-product dictionary is
    presented as a rule-based v1 in the documentation, with the path to a
    POS-driven product affinity model marked as future work.

20. **CHETAVANI priority feed.** `src/anomaly.py: build_alert_feed` returns
    alerts in severity order, top N, instead of a flat dump of hundreds.

## P4 -- Hygiene

21. **Hardcoded paths.** `src/config.py: BASE = os.environ.get("KSHETRA_BASE", ...)`.
22. **Pinned requirements.** `requirements.txt` pins all versions.
23. **Magic numbers.** All thresholds, weights, and windows in `src/config.py`.
24. **API retry.** `src/weather.py: _fetch_one` has exponential backoff.
25. **JSON parsing.** `src/data_io.py: parse_json_field` logs failures.
26. **Modular code.** Notebook god-functions split into focused modules.
27. **Output versioning.** Outputs go to `outputs/`; rotation can be added
    in deployment with a date-stamped subdirectory.

## P5 -- Documentation

28. **NDVI honesty.** Now labelled "weather based proxy" everywhere.
29. **Grower to retailer bridge.** Documentation section 5 explains the
    tehsil-level join explicitly.
30. **Statistical caveats.** Documentation acknowledges single season and
    notes that significance tests are not run.
