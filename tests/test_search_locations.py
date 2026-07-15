"""Tests for accent-insensitive location search."""

from __future__ import annotations

from latvia_weather.parser import WeatherLocationPoint
from latvia_weather.search_locations import search_locations

SAMPLE_LOCATIONS = [
    WeatherLocationPoint(
        id="P269",
        name="Rīga",
        region="Rīga",
        lat=56.95,
        lon=24.1,
        temperature=18,
        icon_code="1101",
    ),
    WeatherLocationPoint(
        id="P450",
        name="Liepāja",
        region="Liepāja",
        lat=56.51,
        lon=21.01,
        temperature=16,
        icon_code="1102",
    ),
    WeatherLocationPoint(
        id="P364",
        name="Daugavpils",
        region="Augšdaugava",
        lat=55.87,
        lon=26.53,
        temperature=17,
        icon_code="1101",
    ),
]


def test_search_locations_matches_latvian_and_ascii_queries() -> None:
    riga_matches = search_locations(SAMPLE_LOCATIONS, "Rīga")
    assert len(riga_matches) == 1
    assert riga_matches[0].id == "P269"

    riga_ascii_matches = search_locations(SAMPLE_LOCATIONS, "riga")
    assert len(riga_ascii_matches) == 1
    assert riga_ascii_matches[0].name == "Rīga"


def test_search_locations_matches_region_names() -> None:
    matches = search_locations(SAMPLE_LOCATIONS, "Augšdaugava")
    assert len(matches) == 1
    assert matches[0].id == "P364"


def test_search_locations_returns_empty_for_no_match() -> None:
    assert search_locations(SAMPLE_LOCATIONS, "Valmiera") == []
    assert search_locations(SAMPLE_LOCATIONS, "   ") == []


def test_search_locations_respects_limit() -> None:
    matches = search_locations(SAMPLE_LOCATIONS, "a", limit=2)
    assert len(matches) == 2
