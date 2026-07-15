"""Curated LVĢMC forecast location points."""

from __future__ import annotations

from typing import Final

DEFAULT_LOCATION_ID: Final[str] = "P269"

# Keep in sync with latvia-weather/src/lib/weather/locations.ts
LOCATION_POINT_IDS: Final[tuple[str, ...]] = (
    "P1134",
    "P1352",
    "P364",
    "P450",
    "P269",
    "P905",
    "P992",
    "P768",
    "P458",
    "P862",
    "P915",
    "P770",
    "P206",
    "P322",
    "P449",
    "P359",
    "P766",
    "P868",
    "P863",
    "P215",
    "P361",
    "P317",
    "P170",
    "P125",
    "P213",
    "P467",
    "P123",
    "P211",
    "P748",
    "P866",
    "P323",
    "P117",
    "P1098",
    "P1580",
    "P6992",
    "P362",
    "P363",
    "P122",
    "P126",
    "P6674",
)


def is_valid_location_id(location_id: str) -> bool:
    """Return True when the location ID is in the curated list."""
    return location_id in LOCATION_POINT_IDS
