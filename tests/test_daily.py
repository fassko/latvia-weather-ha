"""Tests for daily forecast grouping."""

from __future__ import annotations

from latvia_weather.daily import build_hourly_forecasts, group_forecasts_by_day
from latvia_weather.parser import parse_hourly_forecast
from tests.fixtures import sample_raw_forecast


def test_group_forecasts_by_day_uses_latvia_day_keys() -> None:
    forecasts = tuple(
        parse_hourly_forecast(sample_raw_forecast(laiks))
        for laiks in ("202607092100", "202607100100", "202607100300")
    )

    groups = group_forecasts_by_day(forecasts)

    assert len(groups) == 2
    assert [group.day_key for group in groups] == ["2026-07-09", "2026-07-10"]
    assert [len(group.forecasts) for group in groups] == [1, 2]


def test_build_hourly_forecasts_includes_icon_code() -> None:
    forecasts = tuple(
        parse_hourly_forecast(sample_raw_forecast("202607091200", icon="2102"))
        for _ in range(1)
    )

    hourly = build_hourly_forecasts(forecasts)

    assert len(hourly) == 1
    assert hourly[0]["icon_code"] == "2102"
