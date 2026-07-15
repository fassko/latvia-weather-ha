"""Tests for upcoming forecast selection."""

from __future__ import annotations

from datetime import datetime, timezone

from latvia_weather.forecasts import get_upcoming_hourly_forecasts, get_upcoming_today_forecasts
from latvia_weather.parser import parse_hourly_forecast
from latvia_weather.timezone import format_laiks
from tests.fixtures import sample_raw_forecast


def _forecasts_from_laiks(*laiks_values: str):
    return tuple(
        parse_hourly_forecast(sample_raw_forecast(laiks)) for laiks in laiks_values
    )


def test_upcoming_hourly_forecasts_start_from_current_latvia_hour() -> None:
    forecasts = _forecasts_from_laiks(
        "202607090300",
        "202607090400",
        "202607090500",
        "202607090600",
        "202607090700",
    )
    now = datetime(2026, 7, 9, 3, 45, tzinfo=timezone.utc)

    upcoming = get_upcoming_hourly_forecasts(forecasts, now)

    assert [format_laiks(forecast.time) for forecast in upcoming] == [
        "202607090600",
        "202607090700",
    ]


def test_upcoming_hourly_forecasts_start_from_current_hour() -> None:
    forecasts = _forecasts_from_laiks(
        "202607080800",
        "202607081000",
        "202607081200",
        "202607081400",
        "202607090000",
    )
    now = datetime(2026, 7, 8, 7, 30, tzinfo=timezone.utc)

    upcoming = get_upcoming_hourly_forecasts(forecasts, now)

    assert [format_laiks(forecast.time) for forecast in upcoming] == [
        "202607081000",
        "202607081200",
        "202607081400",
        "202607090000",
    ]


def test_upcoming_today_forecasts_cover_next_24_hours() -> None:
    forecasts = _forecasts_from_laiks(
        "202607080800",
        "202607081000",
        "202607081200",
        "202607081400",
        "202607090000",
    )
    now = datetime(2026, 7, 8, 7, 30, tzinfo=timezone.utc)

    upcoming = get_upcoming_today_forecasts(forecasts, now)

    assert [format_laiks(forecast.time) for forecast in upcoming] == [
        "202607081000",
        "202607081200",
        "202607081400",
        "202607090000",
    ]
