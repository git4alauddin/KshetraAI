"""
Central configuration for KshetraAI.

Reason this file exists: the original notebooks hardcoded Google Drive paths
and scattered magic numbers (0.40, 0.60, 14, 0.3, 0.5) across five files.
Everything tunable now lives here in one place so the pipeline can move
between machines without editing code.
"""

import os

# ---------------------------------------------------------------------------
# Paths. Override BASE by setting the KSHETRA_BASE environment variable.
# The pipeline expects the eight raw CSV files inside <BASE>/raw_data/.
# ---------------------------------------------------------------------------
BASE = os.environ.get(
    "KSHETRA_BASE",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),  # project root, not src/
)
RAW = os.path.join(BASE, "raw_data")
PROCESSED = os.path.join(BASE, "processed")
MODELS = os.path.join(BASE, "models")
OUTPUT = os.path.join(BASE, "outputs")

for _folder in (PROCESSED, MODELS, OUTPUT):
    os.makedirs(_folder, exist_ok=True)

# ---------------------------------------------------------------------------
# Reference date.
# The data covers a single Rabi season (Oct 2025 to Mar 2026). The last date
# in POS is 2026-03-29, which is near harvest. Scoring on that date leaves the
# crop-stage signal almost flat. For a demo that reflects peak-season urgency,
# point this at a flowering window in mid-January instead.
# ---------------------------------------------------------------------------
REFERENCE_DATE = os.environ.get("KSHETRA_REF_DATE", "2026-01-15")
DATA_LAST_DATE = "2026-03-29"

# Temporal split for model training (train before, test on or after).
SPLIT_DATE = "2026-02-01"

# ---------------------------------------------------------------------------
# Label construction
# ---------------------------------------------------------------------------
SALE_WINDOW_DAYS = 14          # a recommended product counts as converted if it
                               # sells at the retailer within this many days

# ---------------------------------------------------------------------------
# Rule based scorer weights. Must sum to 1.00. The earlier version shipped a
# set that summed to 1.05, which silently inflated scores before it was caught.
# A runtime assert now guards against that.
# ---------------------------------------------------------------------------
RULE_WEIGHTS = {
    "days_since_visit_score":  0.20,
    "stock_urgency_score":     0.20,
    "sales_velocity_score":    0.15,
    "stock_decline_score":     0.15,
    "weather_risk_score":      0.10,
    "product_gap_score":       0.10,
    "crop_stage_score":        0.05,
    "grower_engagement_score": 0.03,
    "ndvi_proxy_score":        0.02,
}
assert abs(sum(RULE_WEIGHTS.values()) - 1.0) < 1e-9, "RULE_WEIGHTS must sum to 1.0"

# ---------------------------------------------------------------------------
# Hybrid blend. Both component scores are normalised to 0..1 before blending,
# so these weights now act on a common scale. In the original code the rule
# score sat on a 0..0.6 range while the model score was a 0..1 probability,
# which meant the stated 40/60 split did not hold in practice.
# ---------------------------------------------------------------------------
RULE_BLEND_WEIGHT = 0.50
ML_BLEND_WEIGHT = 0.50
assert abs(RULE_BLEND_WEIGHT + ML_BLEND_WEIGHT - 1.0) < 1e-9

# ---------------------------------------------------------------------------
# Feature handling
# ---------------------------------------------------------------------------
MISSING_FILL = 0.0             # absent signal means "no evidence", so fill with 0
                               # and carry a companion *_missing flag instead of
                               # the earlier unexplained 0.3 constant

# ---------------------------------------------------------------------------
# Anomaly detection
# ---------------------------------------------------------------------------
PRICE_ANOMALY_CV_THRESHOLD = 0.5     # coefficient of variation per retailer-SKU
DEMAND_SPIKE_RATIO = 3.0             # recent weekly rate vs trailing weekly rate
DEMAND_SPIKE_RECENT_DAYS = 28
DEMAND_SPIKE_BASELINE_DAYS = 84      # trailing window before the recent window

# ---------------------------------------------------------------------------
# Route optimiser
# ---------------------------------------------------------------------------
VISITS_PER_TERRITORY = 6
ORTOOLS_TIME_LIMIT_SEC = 5

# ---------------------------------------------------------------------------
# Campaign products (the four official SKUs the field force is asked to push)
# ---------------------------------------------------------------------------
CAMPAIGN_PRODUCTS = ["Topik 15 WP", "Score 250 EC", "Actara 25 WG", "Kavach 75 WP"]

# ---------------------------------------------------------------------------
# District centroids. Used only to seed approximate coordinates for the route
# optimiser. These are district centres, not retailer GPS. The offsets applied
# in route.py are synthetic and the resulting distances are indicative only.
# ---------------------------------------------------------------------------
DISTRICT_COORDS = {
    "Patna": (25.5941, 85.1376), "Muzaffarpur": (26.1209, 85.3647),
    "Hisar": (29.1492, 75.7217), "Sirsa": (29.5326, 75.0309),
    "Karnal": (29.6857, 76.9905), "Rohtak": (28.8955, 76.6066),
    "Varanasi": (25.3176, 82.9739), "Lucknow": (26.8467, 80.9462),
    "Kanpur Nagar": (26.4499, 80.3319), "Agra": (27.1767, 78.0081),
    "Meerut": (28.9845, 77.7064), "Bharatpur": (27.2152, 77.4938),
    "Bikaner": (28.0229, 73.3119), "Sikar": (27.6094, 75.1399),
    "Jaipur": (26.9124, 75.7873), "Jalgaon": (21.0077, 75.5626),
    "Akola": (20.7002, 77.0082), "Amravati": (20.9374, 77.7796),
    "Ratlam": (23.3315, 75.0367), "Sehore": (23.2006, 77.0851),
    "Ujjain": (23.1765, 75.7885), "Indore": (22.7196, 75.8577),
    "Ahmedabad": (23.0225, 72.5714), "Rajkot": (22.3039, 70.8022),
    "Mehsana": (23.6000, 72.3693), "Ludhiana": (30.9010, 75.8573),
    "Bathinda": (30.2110, 74.9455), "Patiala": (30.3398, 76.3869),
    "Amritsar": (31.6340, 74.8723), "Bardhaman": (23.2324, 87.8615),
    "Nadia": (23.4700, 88.5560), "Kalaburagi": (17.3297, 76.8200),
    "Vijayapura": (16.8302, 75.7100),
}

RANDOM_STATE = 42
