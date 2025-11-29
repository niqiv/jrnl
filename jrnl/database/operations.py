"""Database CRUD operations."""

from typing import List, Optional
from .connection import get_connection
from .models import Log, Daily


def insert_log(log: Log) -> int:
    """Insert a new log entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO logs (timestamp, log_message, type, label)
               VALUES (?, ?, ?, ?)''',
            (log.timestamp, log.log_message, log.type, log.label)
        )
        return cursor.lastrowid


def get_logs_since(timestamp: str) -> List[Log]:
    """Get all logs since a given timestamp."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM logs
               WHERE timestamp >= ?
               ORDER BY timestamp ASC''',
            (timestamp,)
        )
        rows = cursor.fetchall()
        return [Log(
            id=row['id'],
            timestamp=row['timestamp'],
            log_message=row['log_message'],
            type=row['type'],
            label=row['label']
        ) for row in rows]


def get_all_logs(limit: int = 50) -> List[Log]:
    """Get recent logs."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM logs
               ORDER BY timestamp DESC
               LIMIT ?''',
            (limit,)
        )
        rows = cursor.fetchall()
        return [Log(
            id=row['id'],
            timestamp=row['timestamp'],
            log_message=row['log_message'],
            type=row['type'],
            label=row['label']
        ) for row in rows]


def insert_daily(daily: Daily) -> int:
    """Insert or replace a daily entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT OR REPLACE INTO dailies (timestamp, daily_date, daily_message)
               VALUES (?, ?, ?)''',
            (daily.timestamp, daily.daily_date, daily.daily_message)
        )
        return cursor.lastrowid


def get_latest_daily() -> Optional[Daily]:
    """Get the most recent daily entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM dailies
               ORDER BY timestamp DESC
               LIMIT 1'''
        )
        row = cursor.fetchone()
        if row:
            return Daily(
                id=row['id'],
                timestamp=row['timestamp'],
                daily_date=row['daily_date'],
                daily_message=row['daily_message']
            )
        return None


def get_daily_for_date(date: str) -> Optional[Daily]:
    """Get daily for a specific date."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM dailies
               WHERE daily_date = ?''',
            (date,)
        )
        row = cursor.fetchone()
        if row:
            return Daily(
                id=row['id'],
                timestamp=row['timestamp'],
                daily_date=row['daily_date'],
                daily_message=row['daily_message']
            )
        return None


def get_previous_daily_before(date: str) -> Optional[Daily]:
    """Get the daily entry before a specific date."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM dailies
               WHERE daily_date < ?
               ORDER BY daily_date DESC
               LIMIT 1''',
            (date,)
        )
        row = cursor.fetchone()
        if row:
            return Daily(
                id=row['id'],
                timestamp=row['timestamp'],
                daily_date=row['daily_date'],
                daily_message=row['daily_message']
            )
        return None
