"""Tests for parser module."""

from __future__ import annotations

from latvia_weather.parser import parse_hourly_forecast, parse_number
from tests.fixtures import sample_raw_forecast


def test_parse_number_normalizes_invalid_values() -> None:
    assert parse_number("12.5") == 12.5
    assert parse_number("") == 0.0
    assert parse_number(None) == 0.0
    assert parse_number("not-a-number") == 0.0


def test_parse_hourly_forecast_maps_raw_lvgmc_fields() -> None:
    forecast = parse_hourly_forecast(
        sample_raw_forecast(
            "202607061200",
            precipitation="0.3",
            snow="1.2",
            uv="5",
            thunder="7",
            precipitation_probability="42",
            icon="1102",
            temperature="24.7",
        )
    )

    assert forecast.temperature == 24.7
    assert forecast.feels_like == 24.7
    assert forecast.precipitation == 0.3
    assert forecast.precipitation_probability == 42
    assert forecast.snow == 1.2
    assert forecast.uv_index == 5
    assert forecast.thunder_probability == 7
