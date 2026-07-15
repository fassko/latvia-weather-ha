"""Weather platform for Latvia Weather."""

from __future__ import annotations

from typing import Any

from homeassistant.components.weather import (
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .conditions import map_icon_to_condition
from .const import (
    ATTRIBUTION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_REGION,
)
from .coordinator import LatviaWeatherCoordinator
from .daily import build_daily_forecasts, build_hourly_forecasts
from .entity import get_device_info
from .forecasts import get_current_forecast
from .insights import build_insights


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Latvia Weather from a config entry."""
    coordinator: LatviaWeatherCoordinator = entry.runtime_data
    async_add_entities([LatviaWeatherEntity(coordinator, entry)])


class LatviaWeatherEntity(CoordinatorEntity[LatviaWeatherCoordinator], WeatherEntity):
    """Representation of LVĢMC weather for a location."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_attribution = ATTRIBUTION
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_HOURLY | WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(
        self,
        coordinator: LatviaWeatherCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entry.unique_id
        self._attr_device_info = get_device_info(entry)
        self._attr_latitude = entry.data[CONF_LATITUDE]
        self._attr_longitude = entry.data[CONF_LONGITUDE]

    def _current(self):
        """Return the current-hour forecast entry."""
        return get_current_forecast(self.coordinator.data.forecasts)

    @property
    def condition(self) -> str | None:
        """Return the current weather condition."""
        return map_icon_to_condition(self._current().icon_code)

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._current().temperature

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the current apparent temperature."""
        return self._current().feels_like

    @property
    def native_precipitation(self) -> float | None:
        """Return the current hour precipitation amount."""
        return self._current().precipitation

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        return self._current().humidity

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        return self._current().wind_speed

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the current wind gust speed."""
        return self._current().wind_gust

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the current wind bearing."""
        return self._current().wind_direction

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        return self._current().pressure

    @property
    def cloud_coverage(self) -> int | None:
        """Return the current cloud coverage."""
        return int(self._current().cloud_cover)

    @property
    def uv_index(self) -> float | None:
        """Return the current UV index."""
        return self._current().uv_index

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast."""
        if not self.coordinator.data:
            return None
        return build_hourly_forecasts(self.coordinator.data.forecasts)

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        if not self.coordinator.data:
            return None
        return build_daily_forecasts(self.coordinator.data.forecasts)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if not self.coordinator.data or not self.coordinator.data.forecasts:
            return None

        current = self._current()
        data = self.coordinator.data
        attributes: dict[str, Any] = {
            "location_name": self._entry.data[CONF_NAME],
            "region": self._entry.data.get(CONF_REGION),
            "precipitation_probability": int(current.precipitation_probability),
            "snow": round(current.snow, 1),
            "thunder_probability": int(current.thunder_probability),
            "is_stale": data.is_stale,
            **build_insights(data.forecasts),
        }
        if data.fetched_at is not None:
            attributes["fetched_at"] = data.fetched_at.isoformat()
        return attributes
