"""Tests for timezone helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from latvia_weather.timezone import format_laiks


def test_format_laiks_formats_europe_riga_hours_across_midnight_and_dst() -> None:
    assert (
        format_laiks(datetime(2026, 1, 1, 22, 30, tzinfo=timezone.utc))
        == "202601020000"
    )
    assert (
        format_laiks(datetime(2026, 3, 29, 0, 30, tzinfo=timezone.utc))
        == "202603290200"
    )
    assert (
        format_laiks(datetime(2026, 3, 29, 1, 30, tzinfo=timezone.utc))
        == "202603290400"
    )
