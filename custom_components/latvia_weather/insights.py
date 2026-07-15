"""24-hour weather insight attributes for automations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .const import THUNDER_INSIGHT_THRESHOLD
from .forecasts import get_upcoming_today_forecasts
from .parser import HourlyForecast


def _max_by(
    forecasts: tuple[HourlyForecast, ...],
    get_value: Any,
) -> HourlyForecast:
    return max(forecasts, key=get_value)


def _sum_precipitation(forecasts: tuple[HourlyForecast, ...]) -> float:
    return sum(forecast.precipitation for forecast in forecasts)


def _sum_snow(forecasts: tuple[HourlyForecast, ...]) -> float:
    return sum(forecast.snow for forecast in forecasts)


def _main_rain_period(
    forecasts: tuple[HourlyForecast, ...],
) -> tuple[HourlyForecast, ...]:
    periods: list[tuple[HourlyForecast, ...]] = []
    current: list[HourlyForecast] = []

    for forecast in forecasts:
        if forecast.precipitation > 0:
            current.append(forecast)
        elif current:
            periods.append(tuple(current))
            current = []

    if current:
        periods.append(tuple(current))

    if not periods:
        return ()

    return max(periods, key=_sum_precipitation)


def _main_snow_period(
    forecasts: tuple[HourlyForecast, ...],
) -> tuple[HourlyForecast, ...]:
    periods: list[tuple[HourlyForecast, ...]] = []
    current: list[HourlyForecast] = []

    for forecast in forecasts:
        if forecast.snow > 0:
            current.append(forecast)
        elif current:
            periods.append(tuple(current))
            current = []

    if current:
        periods.append(tuple(current))

    if not periods:
        return ()

    return max(periods, key=_sum_snow)


def _iso_or_none(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def build_insights(
    forecasts: tuple[HourlyForecast, ...],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build machine-readable insight attributes for the next 24 hours."""
    period_forecasts = get_upcoming_today_forecasts(forecasts, now)
    if not period_forecasts:
        return {}

    warmest = _max_by(period_forecasts, lambda forecast: forecast.temperature)
    wettest = _max_by(
        period_forecasts,
        lambda forecast: forecast.precipitation_probability,
    )
    windiest = _max_by(period_forecasts, lambda forecast: forecast.wind_gust)
    stormiest = _max_by(
        period_forecasts,
        lambda forecast: forecast.thunder_probability,
    )
    total_precipitation = _sum_precipitation(period_forecasts)
    total_snow = _sum_snow(period_forecasts)
    main_rain_period = _main_rain_period(period_forecasts)
    main_snow_period = _main_snow_period(period_forecasts)

    rain_start = main_rain_period[0] if main_rain_period else None
    rain_end = main_rain_period[-1] if main_rain_period else None
    rain_max_probability = (
        max(forecast.precipitation_probability for forecast in main_rain_period)
        if main_rain_period
        else 0.0
    )

    snow_start = main_snow_period[0] if main_snow_period else None
    snow_end = main_snow_period[-1] if main_snow_period else None

    insights: dict[str, Any] = {
        "warmest_time": warmest.time.isoformat(),
        "warmest_temperature": round(warmest.temperature),
        "rain_period_start": _iso_or_none(rain_start.time if rain_start else None),
        "rain_period_end": _iso_or_none(rain_end.time if rain_end else None),
        "rain_total_mm": round(total_precipitation, 1),
        "rain_max_probability": int(rain_max_probability),
        "wettest_time": wettest.time.isoformat(),
        "wettest_precipitation_probability": int(wettest.precipitation_probability),
        "windiest_time": windiest.time.isoformat(),
        "windiest_gust_ms": round(windiest.wind_gust, 1),
        "windiest_direction": windiest.wind_direction,
        "thunder_max_probability": int(stormiest.thunder_probability),
        "thunder_alert_time": stormiest.time.isoformat(),
        "thunder_alert": stormiest.thunder_probability >= THUNDER_INSIGHT_THRESHOLD,
    }

    if total_snow > 0:
        insights["snow_total_cm"] = round(total_snow, 1)
        insights["snow_period_start"] = _iso_or_none(
            snow_start.time if snow_start else None
        )
        insights["snow_period_end"] = _iso_or_none(snow_end.time if snow_end else None)

    return insights
