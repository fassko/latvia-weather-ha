"""Map LVĢMC weather icon codes to Home Assistant conditions."""

from __future__ import annotations

try:
    from homeassistant.components.weather import (
        ATTR_CONDITION_CLEAR_NIGHT as CONDITION_CLEAR_NIGHT,
        ATTR_CONDITION_CLOUDY as CONDITION_CLOUDY,
        ATTR_CONDITION_EXCEPTIONAL as CONDITION_EXCEPTIONAL,
        ATTR_CONDITION_FOG as CONDITION_FOG,
        ATTR_CONDITION_HAIL as CONDITION_HAIL,
        ATTR_CONDITION_LIGHTNING as CONDITION_LIGHTNING,
        ATTR_CONDITION_LIGHTNING_RAINY as CONDITION_LIGHTNING_RAINY,
        ATTR_CONDITION_PARTLYCLOUDY as CONDITION_PARTLYCLOUDY,
        ATTR_CONDITION_POURING as CONDITION_POURING,
        ATTR_CONDITION_RAINY as CONDITION_RAINY,
        ATTR_CONDITION_SNOWY as CONDITION_SNOWY,
        ATTR_CONDITION_SNOWY_RAINY as CONDITION_SNOWY_RAINY,
        ATTR_CONDITION_SUNNY as CONDITION_SUNNY,
    )
except ImportError:
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
    "105": CONDITION_PARTLYCLOUDY,
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
        return CONDITION_PARTLYCLOUDY

    is_night = icon_code.startswith("2")
    code = icon_code[1:]

    if is_night and code in _NIGHT_ICON_TO_CONDITION:
        return _NIGHT_ICON_TO_CONDITION[code]

    if code in _ICON_TO_CONDITION:
        return _ICON_TO_CONDITION[code]

    if code.startswith(("30", "50")):
        return CONDITION_RAINY
    if code.startswith("40"):
        return CONDITION_SNOWY
    if code.startswith("20"):
        return CONDITION_FOG
    if code.startswith("10"):
        return CONDITION_CLOUDY if is_night else CONDITION_PARTLYCLOUDY

    return CONDITION_CLOUDY if is_night else CONDITION_PARTLYCLOUDY
