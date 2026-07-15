"""Config flow for Latvia Weather."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LatviaWeatherApi, LatviaWeatherApiError
from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_PUNKTS,
    CONF_REGION,
    DOMAIN,
)
from .parser import WeatherLocationPoint

_LOGGER = logging.getLogger(__name__)


def _location_label(point: WeatherLocationPoint) -> str:
    """Build a display label for a location point."""
    if point.region and point.region != point.name:
        return f"{point.name} ({point.region})"
    return point.name


def _location_entry_data(point: WeatherLocationPoint) -> dict[str, Any]:
    """Build config entry data from a location point."""
    return {
        CONF_PUNKTS: point.id,
        CONF_NAME: point.name,
        CONF_REGION: point.region,
        CONF_LATITUDE: point.lat,
        CONF_LONGITUDE: point.lon,
    }


async def _fetch_location_points(hass: HomeAssistant) -> list[WeatherLocationPoint]:
    """Fetch all location points from the LVĢMC API."""
    api = LatviaWeatherApi(async_get_clientsession(hass))
    return await api.get_location_points()


class LatviaWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Latvia Weather."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._location_points: list[WeatherLocationPoint] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        return await self._async_step_location("user", user_input)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of an existing entry."""
        return await self._async_step_location("reconfigure", user_input)

    async def _async_step_location(
        self,
        step_id: str,
        user_input: dict[str, Any] | None,
    ) -> FlowResult:
        """Shared logic for user and reconfigure steps."""
        errors: dict[str, str] = {}

        try:
            self._location_points = await _fetch_location_points(self.hass)
        except LatviaWeatherApiError:
            _LOGGER.exception("Failed to fetch location points")
            return self.async_abort(reason="cannot_connect")

        if user_input is not None:
            punkts = user_input[CONF_PUNKTS]
            point = next(
                (item for item in self._location_points if item.id == punkts),
                None,
            )
            if point is None:
                errors[CONF_PUNKTS] = "invalid_location"
            elif step_id == "user":
                await self.async_set_unique_id(punkts)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=point.name,
                    data=_location_entry_data(point),
                )
            else:
                entry = self._get_reconfigure_entry()
                if entry.unique_id != punkts:
                    self.hass.config_entries.async_update_entry(
                        entry,
                        unique_id=punkts,
                    )
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=_location_entry_data(point),
                    title=point.name,
                )

        schema = self._build_location_schema(step_id)
        return self.async_show_form(
            step_id=step_id,
            data_schema=schema,
            errors=errors,
        )

    def _build_location_schema(self, step_id: str) -> vol.Schema:
        """Build a searchable location selector from API data."""
        options = [
            selector.SelectOptionDict(
                value=point.id,
                label=_location_label(point),
            )
            for point in self._location_points
        ]
        select = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=options,
                mode=selector.SelectSelectorMode.DROPDOWN,
                sort=True,
            )
        )

        if step_id == "reconfigure":
            return vol.Schema(
                {
                    vol.Required(
                        CONF_PUNKTS,
                        default=self._get_reconfigure_entry().data[CONF_PUNKTS],
                    ): select,
                }
            )

        return vol.Schema({vol.Required(CONF_PUNKTS): select})

    def _get_reconfigure_entry(self) -> config_entries.ConfigEntry:
        """Return the config entry being reconfigured."""
        entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if entry is None:
            msg = "Reconfigure entry not found"
            raise RuntimeError(msg)
        return entry
