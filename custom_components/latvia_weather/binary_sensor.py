"""Binary sensor platform for Latvia Weather."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LatviaWeatherCoordinator
from .entity import get_device_info
from .insights import build_insights


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Latvia Weather binary sensors from a config entry."""
    coordinator: LatviaWeatherCoordinator = entry.runtime_data
    async_add_entities([LatviaWeatherThunderAlertBinarySensor(coordinator, entry)])


class LatviaWeatherThunderAlertBinarySensor(
    CoordinatorEntity[LatviaWeatherCoordinator], BinarySensorEntity
):
    """Thunder alert for the next 24 hours."""

    _attr_has_entity_name = True
    _attr_name = "Thunder alert"
    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(
        self,
        coordinator: LatviaWeatherCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.unique_id}_thunder_alert"
        self._attr_device_info = get_device_info(entry)

    @property
    def is_on(self) -> bool | None:
        """Return True when thunder probability exceeds the alert threshold."""
        if not self.coordinator.data or not self.coordinator.data.forecasts:
            return None
        insights = build_insights(self.coordinator.data.forecasts)
        return bool(insights.get("thunder_alert"))
