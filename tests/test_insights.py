"""Tests for weather insight attributes."""

from __future__ import annotations

from datetime import datetime, timezone

from latvia_weather.insights import build_insights
from latvia_weather.parser import parse_hourly_forecast
from tests.fixtures import sample_raw_forecast


def test_build_insights_flags_thunder_alert_and_snow_totals() -> None:
    forecasts = tuple(
        parse_hourly_forecast(
            sample_raw_forecast(
                laiks,
                precipitation="1.0" if laiks.endswith("1200") else "0",
                snow="0.5" if laiks.endswith("1400") else "0",
                thunder="25" if laiks.endswith("1500") else "0",
                precipitation_probability="80" if laiks.endswith("1200") else "10",
                temperature="20" if laiks.endswith("1300") else "18",
            )
        )
        for laiks in (
            "202607151000",
            "202607151200",
            "202607151300",
            "202607151400",
            "202607151500",
        )
    )
    now = datetime(2026, 7, 15, 7, 0, tzinfo=timezone.utc)

    insights = build_insights(forecasts, now)

    assert insights["warmest_temperature"] == 20
    assert insights["rain_total_mm"] == 1.0
    assert insights["rain_max_probability"] == 80
    assert insights["snow_total_cm"] == 0.5
    assert insights["thunder_alert"] is True
    assert insights["thunder_max_probability"] == 25
