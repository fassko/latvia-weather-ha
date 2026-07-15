"""Tests for Latvia Weather sensor platform compatibility."""

from __future__ import annotations

from pathlib import Path


def test_uv_index_sensor_uses_native_unit_instead_of_device_class() -> None:
    """UV index should use homeassistant.const.UV_INDEX, not SensorDeviceClass."""
    sensor_source = (
        Path(__file__).resolve().parents[1]
        / "custom_components/latvia_weather/sensor.py"
    ).read_text(encoding="utf-8")

    assert "SensorDeviceClass.UV_INDEX" not in sensor_source
    assert "_attr_native_unit_of_measurement = UV_INDEX" in sensor_source
