"""Daily forecast aggregation from hourly data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.weather import Forecast

from .conditions import map_icon_to_condition
from .parser import HourlyForecast
from .timezone import get_latvia_day_key, get_latvia_wall_clock


@dataclass(frozen=True, slots=True)
class DailyForecastGroup:
    """Hourly forecasts grouped by calendar day."""

    day_key: str
    date: datetime
    forecasts: tuple[HourlyForecast, ...]


@dataclass(frozen=True, slots=True)
class DailySummary:
    """Aggregated daily forecast values."""

    min_temperature: float
    max_temperature: float
    min_feels_like: float
    max_feels_like: float
    total_precipitation: float
    max_precipitation_probability: float
    avg_humidity: float
    max_wind_speed: float
    wind_direction_at_max_wind: float
    avg_pressure: float
    representative_icon_code: str


def _day_key(time: datetime) -> str:
    return get_latvia_day_key(time)


def group_forecasts_by_day(
    forecasts: tuple[HourlyForecast, ...],
) -> list[DailyForecastGroup]:
    """Group hourly forecasts by calendar day in the forecast timezone."""
    groups: dict[str, DailyForecastGroup] = {}

    for forecast in forecasts:
        key = _day_key(forecast.time)
        if key in groups:
            existing = groups[key]
            groups[key] = DailyForecastGroup(
                day_key=existing.day_key,
                date=existing.date,
                forecasts=(*existing.forecasts, forecast),
            )
        else:
            groups[key] = DailyForecastGroup(
                day_key=key,
                date=get_latvia_wall_clock(forecast.time),
                forecasts=(forecast,),
            )

    return list(groups.values())


def _find_representative_icon_code(forecasts: tuple[HourlyForecast, ...]) -> str:
    midday = forecasts[0]
    closest_distance = abs(midday.time.hour - 12)

    for forecast in forecasts[1:]:
        hour_distance = abs(forecast.time.hour - 12)
        if hour_distance < closest_distance:
            midday = forecast
            closest_distance = hour_distance

    return midday.icon_code


def summarize_day(forecasts: tuple[HourlyForecast, ...]) -> DailySummary:
    """Aggregate hourly forecasts into a daily summary."""
    first = forecasts[0]
    min_temperature = first.temperature
    max_temperature = first.temperature
    min_feels_like = first.feels_like
    max_feels_like = first.feels_like
    total_precipitation = 0.0
    max_precipitation_probability = 0.0
    humidity_sum = 0.0
    max_wind_speed = 0.0
    wind_direction_at_max_wind = first.wind_direction
    pressure_sum = 0.0

    for forecast in forecasts:
        min_temperature = min(min_temperature, forecast.temperature)
        max_temperature = max(max_temperature, forecast.temperature)
        min_feels_like = min(min_feels_like, forecast.feels_like)
        max_feels_like = max(max_feels_like, forecast.feels_like)
        total_precipitation += forecast.precipitation
        max_precipitation_probability = max(
            max_precipitation_probability,
            forecast.precipitation_probability,
        )
        humidity_sum += forecast.humidity
        if forecast.wind_speed >= max_wind_speed:
            max_wind_speed = forecast.wind_speed
            wind_direction_at_max_wind = forecast.wind_direction
        pressure_sum += forecast.pressure

    count = len(forecasts)
    return DailySummary(
        min_temperature=min_temperature,
        max_temperature=max_temperature,
        min_feels_like=min_feels_like,
        max_feels_like=max_feels_like,
        total_precipitation=total_precipitation,
        max_precipitation_probability=max_precipitation_probability,
        avg_humidity=humidity_sum / count,
        max_wind_speed=max_wind_speed,
        wind_direction_at_max_wind=wind_direction_at_max_wind,
        avg_pressure=pressure_sum / count,
        representative_icon_code=_find_representative_icon_code(forecasts),
    )


def build_daily_forecasts(
    forecasts: tuple[HourlyForecast, ...],
) -> list[Forecast]:
    """Build Home Assistant daily forecast dicts from hourly data."""
    result: list[Forecast] = []

    for group in group_forecasts_by_day(forecasts):
        summary = summarize_day(group.forecasts)
        midday = datetime(
            group.date.year,
            group.date.month,
            group.date.day,
            12,
            0,
            0,
        )
        if group.forecasts:
            midday = midday.replace(tzinfo=group.forecasts[0].time.tzinfo)
        result.append(
            Forecast(
                datetime=midday.astimezone().isoformat(),
                condition=map_icon_to_condition(summary.representative_icon_code),
                native_temperature=summary.max_temperature,
                native_templow=summary.min_temperature,
                native_apparent_temperature=summary.max_feels_like,
                native_precipitation=summary.total_precipitation,
                precipitation_probability=int(summary.max_precipitation_probability),
                humidity=int(summary.avg_humidity),
                native_wind_speed=summary.max_wind_speed,
                wind_bearing=summary.wind_direction_at_max_wind,
                native_pressure=summary.avg_pressure,
            )
        )

    return result


def build_hourly_forecasts(
    forecasts: tuple[HourlyForecast, ...],
) -> list[Forecast]:
    """Build Home Assistant hourly forecast dicts."""
    return [
        Forecast(
            datetime=forecast.time.astimezone().isoformat(),
            condition=map_icon_to_condition(forecast.icon_code),
            icon_code=forecast.icon_code,
            native_temperature=forecast.temperature,
            native_apparent_temperature=forecast.feels_like,
            native_precipitation=forecast.precipitation,
            precipitation_probability=int(forecast.precipitation_probability),
            humidity=int(forecast.humidity),
            native_wind_speed=forecast.wind_speed,
            native_wind_gust_speed=forecast.wind_gust,
            wind_bearing=forecast.wind_direction,
            native_pressure=forecast.pressure,
            cloud_coverage=int(forecast.cloud_cover),
            uv_index=forecast.uv_index,
        )
        for forecast in forecasts
    ]
