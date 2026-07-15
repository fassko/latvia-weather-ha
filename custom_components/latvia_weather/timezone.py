"""Europe/Riga timezone helpers for LVĢMC data."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .const import RIGA_TIMEZONE

RIGA_TZ = ZoneInfo(RIGA_TIMEZONE)


def parse_laiks(laiks: str) -> datetime:
    """Parse LVĢMC time string (yyyyMMddHHmm) as Europe/Riga wall time."""
    return datetime(
        int(laiks[0:4]),
        int(laiks[4:6]),
        int(laiks[6:8]),
        int(laiks[8:10]),
        int(laiks[10:12]),
        tzinfo=RIGA_TZ,
    )


def format_laiks(moment: datetime | None = None) -> str:
    """Format time for LVĢMC API (Europe/Riga, start of current hour)."""
    if moment is None:
        moment = datetime.now(RIGA_TZ)
    else:
        moment = moment.astimezone(RIGA_TZ)

    moment = moment.replace(minute=0, second=0, microsecond=0)
    return moment.strftime("%Y%m%d%H00")


def get_latvia_wall_clock(date: datetime) -> datetime:
    """Map an instant to Latvia wall-clock fields as a naive datetime."""
    local = date.astimezone(RIGA_TZ)
    return datetime(
        local.year,
        local.month,
        local.day,
        local.hour,
        local.minute,
        local.second,
        local.microsecond,
    )


def get_latvia_start_of_hour(date: datetime) -> datetime:
    """Return start of the current hour in Latvia wall-clock time."""
    wall = get_latvia_wall_clock(date)
    return wall.replace(minute=0, second=0, microsecond=0)


def get_latvia_day_key(date: datetime) -> str:
    """Return yyyy-MM-dd day key in Europe/Riga."""
    wall = get_latvia_wall_clock(date)
    return wall.strftime("%Y-%m-%d")
