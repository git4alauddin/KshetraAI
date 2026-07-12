"""
Backtest against business as usual.

This answers the question the whole project rests on: would the ranking have
surfaced converting retailers better than the rep's actual choices. It reports
recall at k, that is, of the retailers that did convert in a rep-day, how many
landed in the top k of the recommended order. Without a number like this the
claim of being better than habitual routing is just an assertion.
"""

import logging
import numpy as np
import pandas as pd

log = logging.getLogger("kshetra.backtest")


def recall_at_k(scored_visits, score_col="final_score", k=6):
    """scored_visits has rep_id, visit_date, label, and a score column."""
    groups, hits, total = 0, 0, 0
    for _, g in scored_visits.groupby(["rep_id", "visit_date"]):
        converters = g[g["label"] == 1]
        if converters.empty:
            continue
        topk = g.sort_values(score_col, ascending=False).head(k)
        hits += topk["label"].sum()
        total += converters.shape[0]
        groups += 1
    recall = hits / total if total else float("nan")
    log.info("Recall@%d over %d rep-days: %.3f", k, groups, recall)
    return {"k": k, "groups": groups, "recall_at_k": round(float(recall), 4)}
