"""Constants for the Latvia Weather integration."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Final

DOMAIN = "latvia_weather"

MANIFEST_PATH = Path(__file__).parent / "manifest.json"
with MANIFEST_PATH.open(encoding="utf-8") as manifest_file:
    INTEGRATION_VERSION: Final[str] = json.load(manifest_file)["version"]

URL_BASE: Final[str] = f"/{DOMAIN}"

JSMODULES: Final[list[dict[str, str]]] = [
    {
        "name": "Latvia Weather Chart Card",
        "filename": "latvia-weather-chart-card.js",
        "version": INTEGRATION_VERSION,
    },
]

WEATHER_API_BASE = "https://videscentrs.lvgmc.lv/data"
RIGA_TIMEZONE = "Europe/Riga"

SCAN_INTERVAL = timedelta(minutes=15)
STALE_FALLBACK = timedelta(hours=6)
THUNDER_INSIGHT_THRESHOLD = 20

CONF_PUNKTS = "punkts"
CONF_NAME = "name"
CONF_REGION = "region"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"

ATTRIBUTION = (
    "Latvian Environment, Geology and Meteorology Centre (LVĢMC)"
)
