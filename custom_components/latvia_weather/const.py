"""Constants for the Latvia Weather integration."""

from datetime import timedelta

DOMAIN = "latvia_weather"

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
