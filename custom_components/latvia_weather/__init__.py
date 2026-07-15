"""The Latvia Weather integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import LatviaWeatherApi
from .const import DOMAIN
from .coordinator import LatviaWeatherCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR, Platform.BINARY_SENSOR]

type LatviaWeatherConfigEntry = ConfigEntry[LatviaWeatherCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: LatviaWeatherConfigEntry) -> bool:
    """Set up Latvia Weather from a config entry."""
    api = LatviaWeatherApi.from_hass(hass)
    coordinator = LatviaWeatherCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LatviaWeatherConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
