"""Upcoming forecast selection helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from .parser import HourlyForecast
from .timezone import get_latvia_start_of_hour, get_latvia_wall_clock


def get_upcoming_hourly_forecasts(
    forecasts: tuple[HourlyForecast, ...],
    now: datetime | None = None,
) -> tuple[HourlyForecast, ...]:
    """Return forecasts from the current Latvia hour onward."""
    if not forecasts:
        return ()

    reference = now or datetime.now(forecasts[0].time.tzinfo)
    current_hour = get_latvia_start_of_hour(reference)
    upcoming = tuple(
        forecast
        for forecast in forecasts
        if get_latvia_wall_clock(forecast.time) >= current_hour
    )

    if upcoming:
        return upcoming
    return forecasts[-1:]


def get_upcoming_today_forecasts(
    forecasts: tuple[HourlyForecast, ...],
    now: datetime | None = None,
) -> tuple[HourlyForecast, ...]:
    """Return the next 24 hours of forecasts from the current Latvia hour."""
    if not forecasts:
        return ()

    reference = now or datetime.now(forecasts[0].time.tzinfo)
    current_hour = get_latvia_start_of_hour(reference)
    end = current_hour + timedelta(hours=24)
    upcoming = get_upcoming_hourly_forecasts(forecasts, reference)
    next_24_hours = tuple(
        forecast
        for forecast in upcoming
        if get_latvia_wall_clock(forecast.time) < end
    )

    if next_24_hours:
        return next_24_hours

    if upcoming:
        return upcoming[:24]
    return forecasts[-1:]


def get_current_forecast(
    forecasts: tuple[HourlyForecast, ...],
    now: datetime | None = None,
) -> HourlyForecast:
    """Return the forecast entry for the current or next available hour."""
    upcoming = get_upcoming_hourly_forecasts(forecasts, now)
    return upcoming[0]
