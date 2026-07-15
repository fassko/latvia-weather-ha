"""Tests for API stale fallback caching."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from latvia_weather.api import LatviaWeatherApi
from tests.fixtures import sample_raw_forecast


@pytest.mark.asyncio
async def test_get_hourly_forecast_falls_back_to_stale_cache_on_api_failure() -> None:
    raw_forecast = [sample_raw_forecast("202607061200", temperature="21")]
    session = MagicMock()
    api = LatviaWeatherApi(session)

    success_response = MagicMock()
    success_response.status = 200
    success_response.json = AsyncMock(return_value=raw_forecast)
    success_response.__aenter__ = AsyncMock(return_value=success_response)
    success_response.__aexit__ = AsyncMock(return_value=None)

    failure_response = MagicMock()
    failure_response.status = 503
    failure_response.__aenter__ = AsyncMock(return_value=failure_response)
    failure_response.__aexit__ = AsyncMock(return_value=None)

    session.get = MagicMock(side_effect=[success_response, failure_response])

    fresh = await api.get_hourly_forecast("P269")
    assert fresh.is_stale is False
    assert fresh.forecasts[0].temperature == 21.0

    stale = await api.get_hourly_forecast("P269")
    assert stale.is_stale is True
    assert stale.forecasts[0].temperature == 21.0
