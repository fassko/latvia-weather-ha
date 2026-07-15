"""Tests for curated location point configuration."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from latvia_weather.api import LatviaWeatherApi
from latvia_weather.locations import (
    DEFAULT_LOCATION_ID,
    LOCATION_POINT_IDS,
    is_valid_location_id,
)


def test_location_point_ids_include_garupe() -> None:
    assert "P1134" in LOCATION_POINT_IDS
    assert DEFAULT_LOCATION_ID == "P269"


def test_is_valid_location_id() -> None:
    assert is_valid_location_id("P1134")
    assert not is_valid_location_id("P9999")


@pytest.mark.asyncio
async def test_get_location_points_requests_curated_ids() -> None:
    session = MagicMock()
    api = LatviaWeatherApi(session)

    response = MagicMock()
    response.status = 200
    response.json = AsyncMock(
        return_value=[
            {
                "punkts": "P1134",
                "nosaukums": "Garupe",
                "novads": "Garupe, Carnikavas pag., Ādažu nov.",
                "lat": "57.1217",
                "lon": "24.235258",
                "temperatura": "21.3",
                "laika_apstaklu_ikona": "1101",
            }
        ]
    )
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=None)
    session.get = MagicMock(return_value=response)

    points = await api.get_location_points()

    assert len(points) == 1
    assert points[0].id == "P1134"
    assert points[0].name == "Garupe"

    url = session.get.call_args[0][0]
    assert "punkti=" in url
    assert "P1134" in url
    assert "P269" in url
