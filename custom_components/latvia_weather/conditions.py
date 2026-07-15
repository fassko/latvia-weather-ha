"""Map LVĢMC weather icon codes to Home Assistant conditions."""

from __future__ import annotations

from homeassistant.const import (
    CONDITION_CLEAR_NIGHT,
    CONDITION_CLOUDY,
    CONDITION_EXCEPTIONAL,
    CONDITION_FOG,
    CONDITION_HAIL,
    CONDITION_LIGHTNING,
    CONDITION_LIGHTNING_RAINY,
    CONDITION_PARTLYCLOUDY,
    CONDITION_POURING,
    CONDITION_RAINY,
    CONDITION_SNOWY,
    CONDITION_SNOWY_RAINY,
    CONDITION_SUNNY,
)

_ICON_TO_CONDITION: dict[str, str] = {
    "101": CONDITION_SUNNY,
    "102": CONDITION_PARTLYCLOUDY,
    "103": CONDITION_CLOUDY,
    "104": CONDITION_CLOUDY,
    "201": CONDITION_FOG,
    "202": CONDITION_FOG,
    "203": CONDITION_FOG,
    "204": CONDITION_CLOUDY,
    "301": CONDITION_RAINY,
    "302": CONDITION_RAINY,
    "303": CONDITION_POURING,
    "304": CONDITION_LIGHTNING,
    "305": CONDITION_LIGHTNING_RAINY,
    "306": CONDITION_HAIL,
    "401": CONDITION_SNOWY,
    "402": CONDITION_SNOWY,
    "403": CONDITION_SNOWY,
    "404": CONDITION_SNOWY_RAINY,
    "501": CONDITION_RAINY,
    "502": CONDITION_RAINY,
    "503": CONDITION_SNOWY_RAINY,
    "504": CONDITION_SNOWY_RAINY,
    "505": CONDITION_RAINY,
    "506": CONDITION_RAINY,
}

_NIGHT_ICON_TO_CONDITION: dict[str, str] = {
    "101": CONDITION_CLEAR_NIGHT,
}


def map_icon_to_condition(icon_code: str) -> str:
    """Map an LVĢMC icon code to a Home Assistant weather condition."""
    if not icon_code or len(icon_code) < 2:
        return CONDITION_EXCEPTIONAL

    is_night = icon_code.startswith("2")
    code = icon_code[1:]

    if is_night and code in _NIGHT_ICON_TO_CONDITION:
        return _NIGHT_ICON_TO_CONDITION[code]

    return _ICON_TO_CONDITION.get(code, CONDITION_EXCEPTIONAL)
