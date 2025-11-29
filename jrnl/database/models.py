"""Data models for JRNL."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Log:
    """Log entry model."""
    timestamp: str
    log_message: str
    type: str  # 'manual' or 'git-hook'
    label: str
    id: Optional[int] = None

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'log_message': self.log_message,
            'type': self.type,
            'label': self.label
        }


@dataclass
class Daily:
    """Daily standup model."""
    timestamp: str
    daily_date: str
    daily_message: str
    id: Optional[int] = None

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'daily_date': self.daily_date,
            'daily_message': self.daily_message
        }
