"""Shared LVĢMC test record builders."""

from __future__ import annotations


def sample_raw_forecast(
    laiks: str,
    *,
    precipitation: str = "0",
    snow: str | None = "0",
    thunder: str = "0",
    uv: str | None = None,
    precipitation_probability: str = "5",
    icon: str = "1101",
    temperature: str = "21",
) -> dict[str, str | None]:
    """Build a minimal raw LVĢMC hourly forecast record."""
    return {
        "punkts": "P269",
        "nosaukums": "Rīga",
        "novads": "Rīga",
        "laiks": laiks,
        "temperatura": temperature,
        "veja_atrums": "2",
        "veja_virziens": "180",
        "brazmas": "4",
        "nokrisni_1h": precipitation,
        "relativais_mitrums": "70",
        "laika_apstaklu_ikona": icon,
        "spiediens": "1010",
        "sajutu_temperatura": temperature,
        "sniegs": snow,
        "makoni": "10",
        "nokrisnu_varbutiba": precipitation_probability,
        "uvi_indekss": uv,
        "perkons": thunder,
    }
