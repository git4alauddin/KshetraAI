"""
The SEEKHO outcome loop.

In the original this existed only as a slide. Even a small implementation lets
the team say the loop is real. Each visit outcome is appended to a CSV with a
fixed schema. A retraining job can later read this file, attach it to the
features that were shown at recommendation time, and refresh the ranker. The
schema is the contract that makes that possible.
"""

import os
import csv
import logging
import pandas as pd

from . import config

log = logging.getLogger("kshetra.feedback")

OUTCOME_FILE = os.path.join(config.OUTPUT, "visit_outcomes.csv")
FIELDS = ["timestamp", "rep_id", "retailer_id", "product_pitched",
          "recommended_rank", "sale_made", "notes"]


def _ensure_header():
    if not os.path.exists(OUTCOME_FILE):
        with open(OUTCOME_FILE, "w", newline="") as f:
            csv.writer(f).writerow(FIELDS)


def log_visit_outcome(rep_id, retailer_id, product_pitched, sale_made,
                      recommended_rank=None, notes=""):
    """Append one visit outcome. This is what closes the learning loop."""
    _ensure_header()
    row = [pd.Timestamp.now().isoformat(), rep_id, retailer_id, product_pitched,
           recommended_rank if recommended_rank is not None else "",
           int(bool(sale_made)), notes]
    with open(OUTCOME_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)
    log.info("Logged outcome for %s at %s, sale=%s", product_pitched, retailer_id, bool(sale_made))


def load_outcomes():
    if not os.path.exists(OUTCOME_FILE):
        return pd.DataFrame(columns=FIELDS)
    return pd.read_csv(OUTCOME_FILE)


def acceptance_rate():
    """Share of recommended visits the rep actually acted on. One of the
    success metrics the pilot is meant to track."""
    df = load_outcomes()
    if df.empty:
        return None
    acted = df[df["recommended_rank"].astype(str) != ""]
    return None if acted.empty else round(len(acted) / len(df), 3)
