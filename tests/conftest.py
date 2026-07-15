"""Pytest configuration and Home Assistant stubs for unit tests."""

from __future__ import annotations

import sys
from types import ModuleType
from typing import TypedDict


class _GenericStub(type):
    """Allow subscripting stub classes like DataUpdateCoordinator[T]."""

    def __getitem__(cls, _item):
        return cls


class _Forecast(TypedDict, total=False):
    """Minimal Forecast stub for daily module imports."""


def _install_homeassistant_stubs() -> None:
    """Install minimal homeassistant module stubs for offline unit tests."""
    if "homeassistant" in sys.modules:
        return

    homeassistant = ModuleType("homeassistant")
    components = ModuleType("homeassistant.components")
    weather = ModuleType("homeassistant.components.weather")
    config_entries = ModuleType("homeassistant.config_entries")
    const = ModuleType("homeassistant.const")
    core = ModuleType("homeassistant.core")
    helpers = ModuleType("homeassistant.helpers")
    entity_platform = ModuleType("homeassistant.helpers.entity_platform")
    update_coordinator = ModuleType("homeassistant.helpers.update_coordinator")
    aiohttp_client = ModuleType("homeassistant.helpers.aiohttp_client")
    sensor = ModuleType("homeassistant.components.sensor")
    binary_sensor = ModuleType("homeassistant.components.binary_sensor")

    weather.Forecast = _Forecast
    weather.WeatherEntity = _GenericStub("WeatherEntity", (), {})()
    weather.WeatherEntityFeature = ModuleType("WeatherEntityFeature")

    sensor.SensorEntity = _GenericStub("SensorEntity", (), {})()
    sensor.SensorDeviceClass = ModuleType("SensorDeviceClass")
    sensor.SensorStateClass = ModuleType("SensorStateClass")

    binary_sensor.BinarySensorEntity = _GenericStub("BinarySensorEntity", (), {})()
    binary_sensor.BinarySensorDeviceClass = ModuleType("BinarySensorDeviceClass")

    const.UnitOfLength = ModuleType("UnitOfLength")
    const.UnitOfLength.MILLIMETERS = "mm"
    const.UnitOfPressure = ModuleType("UnitOfPressure")
    const.UnitOfPressure.HPA = "hPa"
    const.UnitOfSpeed = ModuleType("UnitOfSpeed")
    const.UnitOfSpeed.METERS_PER_SECOND = "m/s"
    const.UnitOfTemperature = ModuleType("UnitOfTemperature")
    const.UnitOfTemperature.CELSIUS = "°C"
    const.PERCENTAGE = "%"
    const.Platform = ModuleType("Platform")
    const.Platform.WEATHER = "weather"
    const.Platform.SENSOR = "sensor"
    const.Platform.BINARY_SENSOR = "binary_sensor"
    const.CONDITION_SUNNY = "sunny"
    const.CONDITION_CLEAR_NIGHT = "clear-night"
    const.CONDITION_PARTLYCLOUDY = "partlycloudy"
    const.CONDITION_CLOUDY = "cloudy"
    const.CONDITION_FOG = "fog"
    const.CONDITION_RAINY = "rainy"
    const.CONDITION_POURING = "pouring"
    const.CONDITION_LIGHTNING = "lightning"
    const.CONDITION_LIGHTNING_RAINY = "lightning-rainy"
    const.CONDITION_HAIL = "hail"
    const.CONDITION_SNOWY = "snowy"
    const.CONDITION_SNOWY_RAINY = "snowy-rainy"
    const.CONDITION_EXCEPTIONAL = "exceptional"

    config_entries.ConfigEntry = object
    core.HomeAssistant = object
    entity_platform.AddEntitiesCallback = object

    class DataUpdateCoordinator(metaclass=_GenericStub):
        """Stub coordinator base class."""

    class CoordinatorEntity(metaclass=_GenericStub):
        """Stub coordinator entity base class."""

    update_coordinator.CoordinatorEntity = CoordinatorEntity
    update_coordinator.DataUpdateCoordinator = DataUpdateCoordinator
    update_coordinator.UpdateFailed = Exception
    aiohttp_client.async_get_clientsession = lambda _hass: None

    homeassistant.components = components
    homeassistant.config_entries = config_entries
    homeassistant.const = const
    homeassistant.core = core
    homeassistant.helpers = helpers

    components.weather = weather
    components.sensor = sensor
    components.binary_sensor = binary_sensor
    helpers.entity_platform = entity_platform
    helpers.update_coordinator = update_coordinator
    helpers.aiohttp_client = aiohttp_client

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.components"] = components
    sys.modules["homeassistant.components.weather"] = weather
    sys.modules["homeassistant.components.sensor"] = sensor
    sys.modules["homeassistant.components.binary_sensor"] = binary_sensor
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.const"] = const
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.entity_platform"] = entity_platform
    sys.modules["homeassistant.helpers.update_coordinator"] = update_coordinator
    sys.modules["homeassistant.helpers.aiohttp_client"] = aiohttp_client


_install_homeassistant_stubs()
