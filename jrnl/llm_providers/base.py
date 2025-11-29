"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, List


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Dict):
        """Initialize provider with configuration."""
        self.config = config

    @abstractmethod
    def compress_commit(self, commit_message: str, commit_diff: str) -> str:
        """
        Compress git commit information into a concise log message.

        Args:
            commit_message: The git commit message
            commit_diff: The git diff output

        Returns:
            Compressed log message suitable for standup
        """
        pass

    @abstractmethod
    def generate_daily(self, logs: List[Dict], days: int = 1) -> str:
        """
        Generate a daily standup message from logs.

        Args:
            logs: List of log entries (dicts with timestamp, message, type, label)
            days: Number of days being covered

        Returns:
            Formatted standup message
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider is accessible and configured correctly."""
        pass
