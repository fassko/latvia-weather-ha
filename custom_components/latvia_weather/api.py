"""LVĢMC API client with stale fallback caching."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import aiohttp

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import STALE_FALLBACK, WEATHER_API_BASE
from .locations import LOCATION_POINT_IDS
from .parser import (
    WeatherData,
    WeatherLocationPoint,
    parse_location_point,
    parse_weather_data,
)
from .timezone import format_laiks

_LOGGER = logging.getLogger(__name__)


class LatviaWeatherApiError(Exception):
    """Raised when the LVĢMC API returns an error."""


@dataclass
class _CachedForecast:
    """Cached weather payload with storage timestamp."""

    data: WeatherData
    stored_at: datetime


class LatviaWeatherApi:
    """Async client for the LVĢMC weather API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._session = session
        self._hourly_cache: dict[str, _CachedForecast] = {}

    @classmethod
    def from_hass(cls, hass) -> LatviaWeatherApi:
        """Create a client using Home Assistant's aiohttp session."""
        return cls(async_get_clientsession(hass))

    def _is_usable_stale(self, cached: _CachedForecast) -> bool:
        """Return True if cached data is within the stale fallback window."""
        if not cached.data.forecasts:
            return False
        age = datetime.now(timezone.utc) - cached.stored_at
        return age <= STALE_FALLBACK

    def _remember_forecast(self, punkts: str, data: WeatherData) -> None:
        """Store a successful forecast fetch in the cache."""
        self._hourly_cache[punkts] = _CachedForecast(
            data=data,
            stored_at=datetime.now(timezone.utc),
        )

    def _stale_forecast(self, punkts: str) -> WeatherData | None:
        """Return stale cached data for a location, if available."""
        cached = self._hourly_cache.get(punkts)
        if cached is None or not self._is_usable_stale(cached):
            return None
        return WeatherData(
            location=cached.data.location,
            forecasts=cached.data.forecasts,
            is_stale=True,
            fetched_at=cached.stored_at,
        )

    async def get_hourly_forecast(self, punkts: str) -> WeatherData:
        """Fetch hourly forecast for a location point."""
        url = (
            f"{WEATHER_API_BASE}/weather_forecast_for_location_hourly"
            f"?punkts={punkts}"
        )
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    stale = self._stale_forecast(punkts)
                    if stale is not None:
                        _LOGGER.warning(
                            "LVĢMC API returned %s for %s, using stale cache",
                            response.status,
                            punkts,
                        )
                        return stale
                    msg = f"Weather API returned {response.status}"
                    raise LatviaWeatherApiError(msg)
                raw = await response.json()
        except (aiohttp.ClientError, TimeoutError) as err:
            stale = self._stale_forecast(punkts)
            if stale is not None:
                _LOGGER.warning(
                    "LVĢMC API unavailable for %s, using stale cache", punkts
                )
                return stale
            msg = f"Error communicating with LVĢMC API: {err}"
            raise LatviaWeatherApiError(msg) from err

        if not isinstance(raw, list) or not raw:
            stale = self._stale_forecast(punkts)
            if stale is not None:
                _LOGGER.warning(
                    "LVĢMC API returned empty data for %s, using stale cache",
                    punkts,
                )
                return stale
            msg = "Weather API returned empty data"
            raise LatviaWeatherApiError(msg)

        fetched_at = datetime.now(timezone.utc)
        data = parse_weather_data(raw, is_stale=False, fetched_at=fetched_at)
        self._remember_forecast(punkts, data)
        return data

    async def get_location_points(
        self,
        moment: datetime | None = None,
    ) -> list[WeatherLocationPoint]:
        """Fetch curated location points from the LVĢMC API."""
        laiks = format_laiks(moment)
        punkti = ",".join(LOCATION_POINT_IDS)
        url = (
            f"{WEATHER_API_BASE}/weather_points_forecast"
            f"?laiks={laiks}&punkti={punkti}"
        )
        async with self._session.get(url) as response:
            if response.status != 200:
                msg = f"Location points API returned {response.status}"
                raise LatviaWeatherApiError(msg)
            raw = await response.json()

        if not isinstance(raw, list) or not raw:
            msg = "Location points API returned empty data"
            raise LatviaWeatherApiError(msg)

        points = [parse_location_point(item) for item in raw]
        return sorted(points, key=lambda point: point.name)
