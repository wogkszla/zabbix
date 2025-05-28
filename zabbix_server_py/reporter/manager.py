"""Utilities modeled on functions from ``report_manager.c``."""

from __future__ import annotations

from datetime import datetime, timedelta

__all__ = [
    "time_to_urlfield",
    "get_report_range",
    "get_report_name",
]


def time_to_urlfield(dt: datetime) -> str:
    """Return *dt* formatted for use in a URL query field.

    Equivalent to ``rm_time_to_urlfield``.
    """
    return dt.strftime("%Y-%m-%d%%20%H%%3A%M%%3A%S")


def _start_of_period(dt: datetime, period: int) -> datetime:
    if period == 0:  # day
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == 1:  # week (start Monday)
        dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return dt - timedelta(days=dt.weekday())
    if period == 2:  # month
        return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if period == 3:  # year
        return dt.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    raise ValueError("invalid period")


def get_report_range(report_time: int, period: int) -> tuple[datetime, datetime]:
    """Calculate the start and end timestamps for a report.

    Mirrors ``rm_get_report_range`` for the supported periods.  ``period``
    is interpreted as 0=day, 1=week, 2=month, 3=year.
    """
    dt = datetime.fromtimestamp(report_time)
    to = _start_of_period(dt, period)
    if period == 0:
        delta = timedelta(days=1)
    elif period == 1:
        delta = timedelta(weeks=1)
    elif period == 2:
        # subtract one month by going to day 1 of previous month
        month = to.month - 1 or 12
        year = to.year - 1 if to.month == 1 else to.year
        delta = to - datetime(year, month, 1)
    elif period == 3:
        delta = timedelta(days=365)  # rough year
    else:
        raise ValueError("invalid period")
    frm = to - delta
    return frm, to


def get_report_name(name: str, report_time: int) -> str:
    """Return sanitized file name for report attachment.

    Translates ``rm_get_report_name``.
    """
    safe = "".join("_" if c in " \t:/\\" else c for c in name)
    dt = datetime.fromtimestamp(report_time)
    return f"{safe}_{dt:%Y-%m-%d_%H-%M}.pdf"
