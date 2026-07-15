"""Tests for LVĢMC icon to HA condition mapping."""

from __future__ import annotations

from latvia_weather.conditions import map_icon_to_condition


def test_map_icon_to_condition_uses_clear_night_for_night_sunny() -> None:
    assert map_icon_to_condition("2101") == "clear-night"


def test_map_icon_to_condition_uses_sunny_for_day_sunny() -> None:
    assert map_icon_to_condition("1101") == "sunny"


def test_map_icon_to_condition_returns_exceptional_for_unknown_icon() -> None:
    assert map_icon_to_condition("1999") == "exceptional"
