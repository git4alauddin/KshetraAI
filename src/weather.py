"""
Weather fetch with retry and a local cache.

The original called the weather API once with no retry and no fallback, so the
feature matrix could only be built while the API was up. Here a failed call
retries with backoff, and a cached copy on disk is used when the network is
unavailable so the pipeline still runs offline.
"""

import os
import time
import logging
import pandas as pd

from . import config

log = logging.getLogger("kshetra.weather")

CACHE = os.path.join(config.PROCESSED, "weather_data.csv")
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def _fetch_one(district, lat, lon, start, end, retries=3):
    import requests
    params = {
        "latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min",
                  "precipitation_sum", "relative_humidity_2m_max"],
        "timezone": "Asia/Kolkata",
    }
    for attempt in range(retries):
        try:
            resp = requests.get(ARCHIVE_URL, params=params, timeout=15)
            resp.raise_for_status()
            d = resp.json().get("daily")
            if not d:
                return None
            return pd.DataFrame({
                "date": pd.to_datetime(d["time"]),
                "temp_max": d["temperature_2m_max"],
                "temp_min": d["temperature_2m_min"],
                "precipitation": d["precipitation_sum"],
                "humidity_max": d["relative_humidity_2m_max"],
                "district": district,
            })
        except Exception as exc:                       # network or parse failure
            if attempt == retries - 1:
                log.warning("Weather fetch failed for %s: %s", district, exc)
                return None
            time.sleep(2 ** attempt)


def get_weather(start="2025-10-01", end=None, use_cache=True):
    """Return a weather dataframe, preferring the cache, fetching if needed."""
    end = end or config.DATA_LAST_DATE
    if use_cache and os.path.exists(CACHE):
        log.info("Using cached weather from %s", CACHE)
        return pd.read_csv(CACHE, parse_dates=["date"])

    frames = []
    for district, (lat, lon) in config.DISTRICT_COORDS.items():
        df = _fetch_one(district, lat, lon, start, end)
        if df is not None:
            frames.append(df)
        time.sleep(0.3)                                 # be polite to the free API

    if not frames:
        # Could not fetch and no cache. Instead of killing the whole pipeline,
        # return an empty frame and let the weather signal be treated as missing.
        # The features module already handles missing signals with a flag, so the
        # pipeline runs fine, just without the weather contribution. This keeps
        # the project runnable offline on a first run or when the API is down.
        log.warning("No weather data fetched and no cache. Continuing without weather; "
                    "the weather signal will be neutral this run.")
        return pd.DataFrame(columns=["district", "date", "temp_max", "temp_min",
                                     "precip", "humidity_max"])

    weather = pd.concat(frames, ignore_index=True)
    weather.to_csv(CACHE, index=False)
    log.info("Fetched and cached weather: %d rows", len(weather))
    return weather
