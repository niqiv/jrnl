"""Output formatting utilities."""

from .date_utils import format_relative_time
from ..database.models import Log


def format_log_entry(log: Log) -> str:
    """Format a log entry for display."""
    time_str = format_relative_time(log.timestamp)
    type_badge = "[GIT]" if log.type == "git-hook" else "[MAN]"

    return f"{type_badge} {time_str:20} {log.label:10} {log.log_message}"


def format_daily_header(date_str: str) -> str:
    """Format a header for daily standup output."""
    return f"\n{'='*60}\nSTANDUP - {date_str}\n{'='*60}\n"


def format_success(message: str) -> str:
    """Format a success message."""
    return f"✓ {message}"


def format_error(message: str) -> str:
    """Format an error message."""
    return f"✗ {message}"


def format_info(message: str) -> str:
    """Format an info message."""
    return f"ℹ {message}"
