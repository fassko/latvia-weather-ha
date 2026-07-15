"""Tests for LVĢMC icon to HA condition mapping."""

from __future__ import annotations

from latvia_weather.conditions import map_icon_to_condition


def test_map_icon_to_condition_uses_clear_night_for_night_sunny() -> None:
    assert map_icon_to_condition("2101") == "clear-night"


def test_map_icon_to_condition_uses_sunny_for_day_sunny() -> None:
    assert map_icon_to_condition("1101") == "sunny"


def test_map_icon_to_condition_maps_variable_day_icon() -> None:
    assert map_icon_to_condition("1105") == "partlycloudy"
    assert map_icon_to_condition("2105") == "partlycloudy"


def test_map_icon_to_condition_uses_prefix_fallback_for_unknown_icons() -> None:
    assert map_icon_to_condition("1399") == "partlycloudy"
    assert map_icon_to_condition("2599") == "cloudy"
    assert map_icon_to_condition("3301") == "rainy"


def test_map_icon_to_condition_returns_partlycloudy_for_empty_icon() -> None:
    assert map_icon_to_condition("") == "partlycloudy"
