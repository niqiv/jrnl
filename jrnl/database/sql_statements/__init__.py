"""SQL statement definitions for JRNL database."""

CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    log_message TEXT NOT NULL,
    type TEXT NOT NULL,
    label TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    CHECK (type IN ('manual', 'git-hook'))
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(type);
"""

CREATE_DAILIES_TABLE = """
CREATE TABLE IF NOT EXISTS dailies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    daily_date TEXT NOT NULL,
    daily_message TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(daily_date)
);

CREATE INDEX IF NOT EXISTS idx_dailies_date ON dailies(daily_date);
CREATE INDEX IF NOT EXISTS idx_dailies_timestamp ON dailies(timestamp);
"""
