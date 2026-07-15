"""Parse LVĢMC API responses into domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .timezone import parse_laiks


@dataclass(frozen=True, slots=True)
class HourlyForecast:
    """Parsed hourly forecast entry."""

    time: datetime
    temperature: float
    feels_like: float
    precipitation: float
    snow: float
    humidity: float
    wind_speed: float
    wind_gust: float
    wind_direction: float
    pressure: float
    cloud_cover: float
    icon_code: str
    precipitation_probability: float
    uv_index: float | None
    thunder_probability: float


@dataclass(frozen=True, slots=True)
class WeatherLocation:
    """Location metadata."""

    id: str
    name: str
    region: str
    lat: float
    lon: float


@dataclass(frozen=True, slots=True)
class WeatherLocationPoint(WeatherLocation):
    """Location point with current snapshot values."""

    temperature: float
    icon_code: str


@dataclass(frozen=True, slots=True)
class WeatherData:
    """Full weather payload for a location."""

    location: WeatherLocation
    forecasts: tuple[HourlyForecast, ...]
    is_stale: bool = False
    fetched_at: datetime | None = None


def parse_number(value: str | None) -> float:
    """Parse a numeric string from the LVĢMC API."""
    if value is None or value == "":
        return 0.0
    try:
        number = float(value)
    except ValueError:
        return 0.0
    return number if number == number else 0.0  # NaN check


def parse_hourly_forecast(raw: dict[str, str | None]) -> HourlyForecast:
    """Parse a single hourly forecast record."""
    uv_raw = raw.get("uvi_indekss")
    return HourlyForecast(
        time=parse_laiks(str(raw["laiks"])),
        temperature=parse_number(raw.get("temperatura")),
        feels_like=parse_number(raw.get("sajutu_temperatura")),
        precipitation=parse_number(raw.get("nokrisni_1h")),
        snow=parse_number(raw.get("sniegs")),
        humidity=parse_number(raw.get("relativais_mitrums")),
        wind_speed=parse_number(raw.get("veja_atrums")),
        wind_gust=parse_number(raw.get("brazmas")),
        wind_direction=parse_number(raw.get("veja_virziens")),
        pressure=parse_number(raw.get("spiediens")),
        cloud_cover=parse_number(raw.get("makoni")),
        icon_code=str(raw.get("laika_apstaklu_ikona", "")),
        precipitation_probability=parse_number(raw.get("nokrisnu_varbutiba")),
        uv_index=parse_number(uv_raw) if uv_raw not in (None, "") else None,
        thunder_probability=parse_number(raw.get("perkons")),
    )


def parse_weather_data(
    raw: list[dict[str, str | None]],
    *,
    is_stale: bool = False,
    fetched_at: datetime | None = None,
) -> WeatherData:
    """Parse hourly forecast API response into WeatherData."""
    if not raw:
        msg = "Weather API returned empty data"
        raise ValueError(msg)

    first = raw[0]
    location = WeatherLocation(
        id=str(first["punkts"]),
        name=str(first["nosaukums"]),
        region=str(first["novads"]),
        lat=0.0,
        lon=0.0,
    )
    forecasts = tuple(parse_hourly_forecast(item) for item in raw)
    return WeatherData(
        location=location,
        forecasts=forecasts,
        is_stale=is_stale,
        fetched_at=fetched_at,
    )


def parse_location_point(raw: dict[str, str | int | None]) -> WeatherLocationPoint:
    """Parse a location point snapshot from the points forecast API."""
    return WeatherLocationPoint(
        id=str(raw["punkts"]),
        name=str(raw["nosaukums"]),
        region=str(raw["novads"]),
        lat=parse_number(str(raw.get("lat"))),
        lon=parse_number(str(raw.get("lon"))),
        temperature=parse_number(str(raw.get("temperatura"))),
        icon_code=str(raw.get("laika_apstaklu_ikona", "")),
    )
