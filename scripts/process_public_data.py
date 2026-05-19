"""Process fetched public-domain data into stable local signal views.

Raw public files live under ignored `public-data/`. This script converts the
usable fetched files into ignored processed views under `datasets/processed/public/`.

The script is intentionally conservative:
- Weather is converted into entity-level public weather signals.
- Sentinel-2 metadata is preserved as scene inventory and metadata-only NDVI
  availability signals. It does not invent crop stress without raster analysis.
- Pest advisory references are recorded as source availability, not active alerts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DATA_DIR = REPO_ROOT / "public-data"
PROCESSED_DIR = REPO_ROOT / "datasets" / "processed"
PUBLIC_PROCESSED_DIR = PROCESSED_DIR / "public"

OPEN_METEO_FILE = (
    PUBLIC_DATA_DIR
    / "weather"
    / "open_meteo"
    / "amritsar_2026-05-17_2026-05-19.json"
)
SENTINEL_STAC_FILE = (
    PUBLIC_DATA_DIR
    / "ndvi"
    / "sentinel2_earth_search"
    / "amritsar_sentinel2_l2a_2026-05-01_2026-05-19.json"
)

DEMO_TERRITORY_ID = "TER_0164"
DEMO_DATE = "2026-05-17"
DEMO_CROP = "cotton"
DEMO_CROP_STAGE = "flowering"
DEMO_CROP_STAGE_RISK_SCORE = 80


def process_public_data(
    *,
    public_data_dir: Path = PUBLIC_DATA_DIR,
    processed_dir: Path = PROCESSED_DIR,
    output_dir: Path = PUBLIC_PROCESSED_DIR,
) -> dict[str, Path]:
    """Write public processed views and return their output paths."""

    output_dir.mkdir(parents=True, exist_ok=True)
    entity_base = _load_entity_base(processed_dir)

    outputs = {
        "weather_signals": _build_weather_signals(entity_base, public_data_dir),
        "crop_context": _build_crop_context(entity_base),
        "ndvi_scene_inventory": _build_ndvi_scene_inventory(public_data_dir),
        "ndvi_signals": _build_ndvi_signals(entity_base, public_data_dir),
        "pest_source_references": _build_pest_source_references(public_data_dir),
        "pest_signals": _build_pest_signals(entity_base, public_data_dir),
    }

    written: dict[str, Path] = {}
    for name, frame in outputs.items():
        output_path = output_dir / f"{name}.csv"
        frame.to_csv(output_path, index=False, lineterminator="\n")
        written[name] = output_path
    return written


def _load_entity_base(processed_dir: Path) -> pd.DataFrame:
    visit_entities_path = processed_dir / "visit_entities.csv"
    if not visit_entities_path.exists():
        raise FileNotFoundError(
            "Missing processed visit_entities.csv. Run demo output generation first."
        )

    visit_entities = pd.read_csv(visit_entities_path)
    required_columns = {"entity_id", "territory_id", "primary_crop"}
    missing = required_columns.difference(visit_entities.columns)
    if missing:
        raise ValueError("visit_entities.csv missing columns: " + ", ".join(sorted(missing)))

    base = visit_entities.loc[
        visit_entities["territory_id"].astype("string") == DEMO_TERRITORY_ID,
        ["entity_id", "territory_id", "primary_crop"],
    ].copy()
    if base.empty:
        raise ValueError(f"No visit entities found for territory {DEMO_TERRITORY_ID}.")

    return base.sort_values("entity_id", kind="mergesort").reset_index(drop=True)


def _build_weather_signals(entity_base: pd.DataFrame, public_data_dir: Path) -> pd.DataFrame:
    payload = _read_json(
        public_data_dir
        / "weather"
        / "open_meteo"
        / "amritsar_2026-05-17_2026-05-19.json"
    )
    daily = payload.get("daily", {})
    dates = daily.get("time", [])
    if DEMO_DATE not in dates:
        raise ValueError(f"Open-Meteo payload does not include demo date {DEMO_DATE}.")

    index = dates.index(DEMO_DATE)
    max_temp = float(daily["temperature_2m_max"][index])
    min_temp = float(daily["temperature_2m_min"][index])
    temperature_c = round((max_temp + min_temp) / 2, 2)
    humidity = float(daily["relative_humidity_2m_mean"][index])
    rainfall = float(daily["precipitation_sum"][index])
    wind_speed = float(daily["wind_speed_10m_max"][index])
    rainfall_deviation_score = _clamp_score(70 if rainfall <= 1 else max(0, 40 - rainfall))

    output = entity_base.loc[:, ["entity_id", "territory_id"]].copy()
    output["date"] = DEMO_DATE
    output["source"] = "open_meteo"
    output["temperature_c"] = temperature_c
    output["temperature_2m_max_c"] = max_temp
    output["temperature_2m_min_c"] = min_temp
    output["humidity_percent"] = humidity
    output["rainfall_7d_mm"] = rainfall
    output["rainfall_deviation_score"] = rainfall_deviation_score
    output["wind_speed_10m_max_kmh"] = wind_speed
    output["public_signal_status"] = "usable"
    return output


def _build_crop_context(entity_base: pd.DataFrame) -> pd.DataFrame:
    output = entity_base.loc[:, ["entity_id", "territory_id", "primary_crop"]].copy()
    output["date"] = DEMO_DATE
    output["crop"] = output["primary_crop"].fillna(DEMO_CROP).replace("", DEMO_CROP)
    output["crop_stage"] = DEMO_CROP_STAGE
    output["crop_stage_risk_score"] = DEMO_CROP_STAGE_RISK_SCORE
    output["source"] = "controlled_crop_calendar_context"
    output["public_signal_status"] = "curated"
    return output.drop(columns=["primary_crop"])


def _build_ndvi_scene_inventory(public_data_dir: Path) -> pd.DataFrame:
    payload = _read_json(
        public_data_dir
        / "ndvi"
        / "sentinel2_earth_search"
        / "amritsar_sentinel2_l2a_2026-05-01_2026-05-19.json"
    )
    rows: list[dict[str, Any]] = []
    for feature in payload.get("features", []):
        properties = feature.get("properties", {})
        assets = feature.get("assets", {})
        rows.append(
            {
                "scene_id": feature.get("id", ""),
                "datetime": properties.get("datetime", ""),
                "cloud_cover": properties.get("eo:cloud_cover", ""),
                "red_asset_available": "red" in assets,
                "nir_asset_available": "nir" in assets,
                "scl_asset_available": "scl" in assets,
                "visual_asset_available": "visual" in assets,
                "source": "sentinel_2_l2a_earth_search_stac",
            }
        )

    return pd.DataFrame(rows).sort_values(["datetime", "scene_id"], kind="mergesort").reset_index(drop=True)


def _build_ndvi_signals(entity_base: pd.DataFrame, public_data_dir: Path) -> pd.DataFrame:
    scene_inventory = _build_ndvi_scene_inventory(public_data_dir)
    latest_scene = scene_inventory.sort_values("datetime", kind="mergesort").tail(1)
    latest = latest_scene.iloc[0].to_dict() if not latest_scene.empty else {}

    output = entity_base.loc[:, ["entity_id", "territory_id"]].copy()
    output["date"] = DEMO_DATE
    output["source"] = "sentinel_2_l2a_earth_search_stac"
    output["scene_id"] = latest.get("scene_id", "")
    output["scene_datetime"] = latest.get("datetime", "")
    output["cloud_cover"] = latest.get("cloud_cover", "")
    output["ndvi_stress_score"] = 0
    output["ndvi_stress_level"] = "unknown"
    output["public_signal_status"] = "metadata_only"
    output["processing_note"] = "Sentinel-2 red/nir assets found; NDVI raster calculation not executed."
    return output


def _build_pest_source_references(public_data_dir: Path) -> pd.DataFrame:
    references = [
        {
            "source": "npss",
            "file": public_data_dir / "pest_advisories" / "npss" / "aboutproject.pdf",
            "status": "reference_only",
            "note": "Public NPSS project reference fetched; active alert feed not found.",
        },
        {
            "source": "ppqs",
            "file": public_data_dir
            / "pest_advisories"
            / "ppqs"
            / "sop_on_national_system_for_pest_monitoring_response_mechanism.pdf",
            "status": "reference_only",
            "note": "Public PPQS pest monitoring SOP fetched; active alert feed not found.",
        },
    ]
    rows = []
    for reference in references:
        rows.append(
            {
                "source": reference["source"],
                "local_file_available": Path(reference["file"]).exists(),
                "status": reference["status"],
                "note": reference["note"],
            }
        )
    return pd.DataFrame(rows)


def _build_pest_signals(entity_base: pd.DataFrame, public_data_dir: Path) -> pd.DataFrame:
    references = _build_pest_source_references(public_data_dir)
    active_feed_found = bool((references["status"] == "active_feed").any())

    output = entity_base.loc[:, ["entity_id", "territory_id"]].copy()
    output["date"] = DEMO_DATE
    output["source"] = "npss_ppqs_public_references"
    output["pest_alert_active"] = active_feed_found
    output["alert_severity"] = "none"
    output["pest_disease_risk_score"] = 0
    output["pest_or_disease_type"] = ""
    output["public_signal_status"] = "reference_only"
    output["processing_note"] = "No active machine-readable public pest alert feed found."
    return output


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing public data file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _clamp_score(value: float) -> int:
    return int(round(max(0, min(100, value))))


def main() -> None:
    written = process_public_data()
    for name, path in written.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
