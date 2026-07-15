"""Accent-insensitive location search for Latvian place names."""

from __future__ import annotations

import unicodedata

from .parser import WeatherLocationPoint


def _normalize_for_search(value: str) -> str:
    """Normalize text for accent-insensitive Latvian search."""
    lowered = value.casefold()
    decomposed = unicodedata.normalize("NFD", lowered)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def _matches_query(value: str, query: str) -> bool:
    normalized_value = _normalize_for_search(value)
    normalized_query = _normalize_for_search(query)
    return normalized_query in normalized_value


def search_locations(
    points: list[WeatherLocationPoint],
    query: str,
    limit: int = 10,
) -> list[WeatherLocationPoint]:
    """Search forecast locations by city or region name."""
    trimmed_query = query.strip()
    if not trimmed_query:
        return []

    matches = [
        point
        for point in points
        if _matches_query(point.name, trimmed_query)
        or _matches_query(point.region, trimmed_query)
    ]
    return matches[:limit]
