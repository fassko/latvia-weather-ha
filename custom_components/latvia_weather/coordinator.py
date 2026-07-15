"""Data update coordinator for Latvia Weather."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LatviaWeatherApi, LatviaWeatherApiError
from .const import CONF_PUNKTS, DOMAIN, SCAN_INTERVAL
from .parser import WeatherData

if TYPE_CHECKING:
    from . import LatviaWeatherConfigEntry

_LOGGER = logging.getLogger(__name__)


class LatviaWeatherCoordinator(DataUpdateCoordinator[WeatherData]):
    """Coordinator that fetches LVĢMC hourly forecast data."""

    config_entry: LatviaWeatherConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: LatviaWeatherApi,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
            always_update=False,
        )
        self.api = api
        self.punkts = entry.data[CONF_PUNKTS]

    async def _async_update_data(self) -> WeatherData:
        """Fetch data from the LVĢMC API."""
        try:
            data = await self.api.get_hourly_forecast(self.punkts)
        except LatviaWeatherApiError as err:
            raise UpdateFailed(f"Error communicating with LVĢMC API: {err}") from err

        if data.is_stale:
            _LOGGER.warning(
                "Serving stale LVĢMC data for %s (last fetched: %s)",
                self.punkts,
                data.fetched_at,
            )
        return data
