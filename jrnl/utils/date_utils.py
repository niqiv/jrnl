"""Date and time utilities."""

from datetime import datetime, date, timedelta, timezone
from typing import Optional


def get_utc_now() -> str:
    """Get current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format."""
    return date.today().isoformat()


def parse_iso_datetime(timestamp: str) -> datetime:
    """Parse ISO 8601 timestamp to datetime object."""
    # Handle both with and without timezone
    if timestamp.endswith('Z'):
        timestamp = timestamp.replace('Z', '+00:00')
    return datetime.fromisoformat(timestamp)


def get_datetime_ago(days: int = 0, hours: int = 0) -> str:
    """Get datetime N days/hours ago in ISO 8601 format."""
    dt = datetime.now(timezone.utc) - timedelta(days=days, hours=hours)
    return dt.isoformat()


def format_relative_time(timestamp: str) -> str:
    """Format timestamp as relative time (e.g., '2 hours ago')."""
    try:
        dt = parse_iso_datetime(timestamp)
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()

        # Make both timezone-aware or both naive
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        delta = now - dt

        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"
    except (ValueError, TypeError):
        return timestamp
    except Exception:
        # Keep catch-all for formatting - don't want to crash display
        return timestamp


def format_date_for_display(date_str: str) -> str:
    """Format YYYY-MM-DD date for display."""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%A, %B %d, %Y")
    except (ValueError, TypeError):
        return date_str
    except Exception:
        # Keep catch-all for formatting - don't want to crash display
        return date_str
