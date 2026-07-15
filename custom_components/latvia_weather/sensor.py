"""Sensor platform for Latvia Weather."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LatviaWeatherCoordinator
from .entity import get_device_info
from .forecasts import get_current_forecast


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Latvia Weather sensors from a config entry."""
    coordinator: LatviaWeatherCoordinator = entry.runtime_data
    async_add_entities(
        [
            LatviaWeatherPrecipitationSensor(coordinator, entry),
            LatviaWeatherSnowSensor(coordinator, entry),
            LatviaWeatherUvIndexSensor(coordinator, entry),
            LatviaWeatherThunderProbabilitySensor(coordinator, entry),
            LatviaWeatherPrecipitationProbabilitySensor(coordinator, entry),
        ]
    )


class LatviaWeatherSensor(CoordinatorEntity[LatviaWeatherCoordinator], SensorEntity):
    """Base class for Latvia Weather sensors."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: LatviaWeatherCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = get_device_info(entry)


class LatviaWeatherPrecipitationSensor(LatviaWeatherSensor):
    """Current hour precipitation sensor."""

    _attr_name = "Precipitation"
    _attr_native_unit_of_measurement = UnitOfLength.MILLIMETERS
    _attr_device_class = SensorDeviceClass.PRECIPITATION

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._entry.unique_id}_precipitation"

    @property
    def native_value(self) -> float | None:
        """Return the current precipitation amount."""
        if not self.coordinator.data:
            return None
        return get_current_forecast(self.coordinator.data.forecasts).precipitation


class LatviaWeatherSnowSensor(LatviaWeatherSensor):
    """Current hour snow amount sensor."""

    _attr_name = "Snow"
    _attr_native_unit_of_measurement = "cm"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._entry.unique_id}_snow"

    @property
    def native_value(self) -> float | None:
        """Return the current snow amount."""
        if not self.coordinator.data:
            return None
        return get_current_forecast(self.coordinator.data.forecasts).snow


class LatviaWeatherUvIndexSensor(LatviaWeatherSensor):
    """Current UV index sensor."""

    _attr_name = "UV index"
    _attr_device_class = SensorDeviceClass.UV_INDEX

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._entry.unique_id}_uv_index"

    @property
    def available(self) -> bool:
        """Return True when UV data is present."""
        if not super().available or not self.coordinator.data:
            return False
        return (
            get_current_forecast(self.coordinator.data.forecasts).uv_index is not None
        )

    @property
    def native_value(self) -> float | None:
        """Return the current UV index."""
        if not self.coordinator.data:
            return None
        return get_current_forecast(self.coordinator.data.forecasts).uv_index


class LatviaWeatherThunderProbabilitySensor(LatviaWeatherSensor):
    """Current thunder probability sensor."""

    _attr_name = "Thunder probability"
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._entry.unique_id}_thunder_probability"

    @property
    def native_value(self) -> int | None:
        """Return the current thunder probability."""
        if not self.coordinator.data:
            return None
        return int(
            get_current_forecast(self.coordinator.data.forecasts).thunder_probability
        )


class LatviaWeatherPrecipitationProbabilitySensor(LatviaWeatherSensor):
    """Current precipitation probability sensor."""

    _attr_name = "Precipitation probability"
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._entry.unique_id}_precipitation_probability"

    @property
    def native_value(self) -> int | None:
        """Return the current precipitation probability."""
        if not self.coordinator.data:
            return None
        return int(
            get_current_forecast(
                self.coordinator.data.forecasts
            ).precipitation_probability
        )
