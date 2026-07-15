"""Shared entity helpers."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry

from .const import CONF_NAME, CONF_REGION, DOMAIN


def get_device_info(entry: ConfigEntry) -> dict[str, Any]:
    """Build device info shared by weather, sensor, and binary_sensor entities."""
    return {
        "identifiers": {(DOMAIN, entry.unique_id)},
        "name": entry.data[CONF_NAME],
        "manufacturer": "LVĢMC",
        "model": entry.data.get(CONF_REGION, "Latvia"),
    }
