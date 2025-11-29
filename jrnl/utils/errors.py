"""Custom exception classes for JRNL."""


class JRNLError(Exception):
    """Base exception for JRNL."""
    pass


class ConfigError(JRNLError):
    """Configuration-related error."""
    pass


class DatabaseError(JRNLError):
    """Database-related error."""
    pass


class LLMError(JRNLError):
    """LLM provider-related error."""
    pass


class GitError(JRNLError):
    """Git-related error."""
    pass
