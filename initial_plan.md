# JRNL Implementation Plan

## Overview

JRNL is a CLI tool that helps developers automatically track work for daily standups. It captures work via git hooks (automatic) or manual logging, uses LLM to compress and summarize, and generates standup messages.

## Project Structure

```
jrnl/                                   # Repository root
├── install.sh                          # Bash installation script
├── uninstall.sh                        # Bash uninstallation script
├── requirements.txt                    # Python dependencies
├── jrnl/                              # Main Python package
│   ├── cli.py                         # CLI entry point and routing
│   ├── config.py                      # Configuration management
│   ├── __main__.py                    # Entry point for python -m jrnl
│   ├── commands/                      # Command implementations
│   │   ├── new.py                     # Manual logging
│   │   ├── daily.py                   # Standup generation
│   │   ├── logs.py                    # View logs
│   │   ├── config_cmd.py              # Configuration
│   │   └── uninstall_cmd.py           # Uninstall
│   ├── database/                      # Database layer
│   │   ├── connection.py              # SQLite connection
│   │   ├── models.py                  # Data models (Log, Daily)
│   │   ├── operations.py              # CRUD operations
│   │   └── sql_statements/            # SQL queries
│   │       └── __init__.py            # Table definitions
│   ├── llm_providers/                 # LLM abstraction
│   │   ├── base.py                    # Abstract base class
│   │   ├── anthropic_provider.py      # Anthropic/Claude
│   │   ├── ollama_provider.py         # Ollama (local)
│   │   ├── prompts.py                 # LLM prompts
│   │   └── __init__.py                # Provider factory
│   ├── git_integration/               # Git processing
│   │   └── commit_processor.py        # Extract and process commits
│   └── utils/                         # Utilities
│       ├── date_utils.py              # Date/time handling, formatting
│       ├── formatting.py              # Output formatting
│       └── errors.py                  # Custom exceptions
└── hooks/                             # Git hook templates
    └── post-commit.template           # Post-commit hook template

~/.jrnl/                               # Application directory (created on install)
├── config.json                        # User configuration
├── jrnl.db                           # SQLite database
├── venv/                             # Python virtual environment
└── logs/                             # Application logs

~/.local/bin/                          # User binaries (standard location)
└── jrnl                              # CLI wrapper script
```

## Key Design Decisions

### 1. Git Hooks: Global with Opt-Out
- Install hooks globally via `git config --global core.hooksPath ~/.git-hooks`
- Use dispatcher pattern to coexist with existing hooks (user has git-journal)
- Run in background (`&` + `disown`) to avoid blocking commits
- Config flag `git_hooks_enabled` allows opt-out

### 2. LLM Processing: Immediate During Commit
- Git hook calls `git_logger.py` with commit hash and repo path
- Extract commit message and diff
- Process through LLM immediately to compress into log message
- Background execution ensures commits aren't blocked
- Fallback to raw commit message if LLM fails

### 3. Installation: Standalone Script
- Bash `install.sh` script creates:
  - `~/.jrnl/` directory structure
  - Python venv at `~/.jrnl/venv/`
  - SQLite database with schema
  - Default config.json
  - CLI wrapper script at `~/.local/bin/jrnl`
  - Checks if `~/.local/bin` is in PATH, guides user if not
- Prompts user for git hook installation

### 4. Configuration: JSON File
- Store at `~/.jrnl/config.json`
- Contains: LLM provider, model, API keys, git hooks toggle, excluded repos, standup time
- Set permissions to 600 for API key security
- Managed via `jrnl config` command

### 5. Per-Directory Opt-Out
- **Global toggle**: `git_hooks_enabled: false` disables all git logging
- **Per-repo exclude**: `excluded_repos` array contains repository paths to skip
- **Easy management**:
  - `jrnl config exclude /path/to/repo` - opt-out specific repo
  - `jrnl config exclude-current` - opt-out current repo
  - `jrnl config include /path/to/repo` - opt-back-in
- **Hook checks**: Post-commit hook checks if current repo is in exclude list before logging

## Database Schema

### Table: logs
```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,              -- ISO 8601 UTC
    log_message TEXT NOT NULL,            -- Compressed log message
    type TEXT NOT NULL,                   -- 'manual' or 'git-hook'
    label TEXT NOT NULL,                  -- git hash/user title/UUID
    CHECK (type IN ('manual', 'git-hook'))
);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
```

### Table: dailies
```sql
CREATE TABLE dailies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,              -- When generated (UTC)
    daily_date TEXT NOT NULL,             -- Date represented (YYYY-MM-DD)
    daily_message TEXT NOT NULL,          -- Generated standup
    UNIQUE(daily_date)
);
CREATE INDEX idx_dailies_date ON dailies(daily_date);
```

## LLM Provider Architecture

### Abstract Base Class
- `LLMProvider` defines interface:
  - `compress_commit(message, diff) -> str`: Compress commit to log message
  - `generate_daily(logs, days) -> str`: Generate standup from logs
  - `test_connection() -> bool`: Test provider availability

### Initial Providers
1. **AnthropicProvider**: Uses Anthropic SDK, configurable model
2. **OllamaProvider**: Uses Ollama REST API, local models

### Provider Selection
- Factory pattern in `llm_providers/__init__.py`
- `get_provider(config)` reads `active_llm_provider` from config
- Passes provider-specific config section to provider constructor
- Example: `AnthropicProvider(config['llm_providers']['anthropic'])`

### Prompts
- **compress_commit**: Max 100 chars, focus on WHAT was done, past tense
- **generate_daily**: 3-5 sentence paragraph covering completed work, next steps, obstacles

## CLI Commands

### `jrnl new -m "message"`
- Create manual log entry
- Generate UUID label if not provided
- Store with type='manual' and UTC timestamp

**Git Hook Mode:** `jrnl new --git --repo-path <path> --commit-hash <hash>`
- Extract commit message and diff from git repository
- Process through LLM to compress into log message
- Store with type='git-hook' and commit hash as label
- Used by post-commit hook instead of separate git_logger module

### `jrnl daily` / `jrnl standup`
- Get logs since last daily generation (or 24h if none)
- Call LLM provider to generate standup message
- Store in dailies table with today's date
- Display formatted output

**Options:**
- `--days N`: Include logs from N days
- `--regenerate`: Regenerate today's daily using logs since previous workday

### `jrnl logs`
- Display recent log entries
- Optional: `--days N` to filter by date range
- Format: `[TYPE] timestamp label message`

### `jrnl config`
- `jrnl config`: Show current configuration (all providers, excluded repos)
- `jrnl config set-provider <provider>`: Switch active LLM provider
- `jrnl config set <provider> <key> <value>`: Set provider-specific setting
  - Examples:
    - `jrnl config set anthropic api_key sk-...`
    - `jrnl config set anthropic model claude-3-5-sonnet-20241022`
    - `jrnl config set ollama url http://localhost:11434`
    - `jrnl config set anthropic max_tokens_daily 1000`
- `jrnl config exclude <repo-path>`: Add repository to exclude list (opt-out)
- `jrnl config include <repo-path>`: Remove repository from exclude list (opt-in)
- `jrnl config exclude-current`: Exclude current repository (shortcut)

### `jrnl uninstall`
- Prompt for confirmation
- Optional database backup
- Remove git hooks
- Remove `~/.jrnl/` directory
- Remove PATH entry from shell RC

## Git Hook Implementation

### Post-Commit Hook Template
```bash
#!/bin/bash
REPO_PATH=$(git rev-parse --show-toplevel)
COMMIT_HASH=$(git rev-parse HEAD)
JRNL_DIR="$HOME/.jrnl"
JRNL_CMD="$JRNL_DIR/jrnl"

# Check if enabled in config
HOOKS_ENABLED=$(cat "$JRNL_DIR/config.json" | grep '"git_hooks_enabled".*true')
if [ -z "$HOOKS_ENABLED" ]; then exit 0; fi

# Check if current repo is excluded
EXCLUDED=$(cat "$JRNL_DIR/config.json" | grep -o "\"$REPO_PATH\"")
if [ -n "$EXCLUDED" ]; then exit 0; fi

# Run jrnl new command in background
"$JRNL_CMD" new --git \
    --repo-path "$REPO_PATH" \
    --commit-hash "$COMMIT_HASH" \
    >> "$JRNL_DIR/logs/hook.log" 2>&1 &
disown
```

### Hook Installation (in ./install.sh script)
- Check for existing global hooks path via `git config --global core.hooksPath`
- If no hooks path, set to `~/.git-hooks`
- Check if post-commit hook exists
- If exists: Append jrnl call to existing hook (coexist with other tools)
- If not: Create new hook from template
- Make hook executable: `chmod +x`

### Hook Uninstallation (in ./uninstall.sh script)
- Find post-commit hook at global hooks path
- Remove jrnl-specific lines from hook
- If hook becomes empty, delete the file

### Git Commit Processing (via `jrnl new --git`)
1. When `--git` flag is present in `jrnl new` command:
2. Extract commit message: `git log -1 --pretty=%B <hash>`
3. Extract commit diff: `git show --unified=3 <hash>`
4. Call LLM provider to compress commit info
5. Create Log entry with type='git-hook' and commit hash as label
6. Insert to database
7. Log errors silently (never block commits)

**Implementation**: The `commands/new.py` module handles both manual and git modes

## Standup Generation Logic

### Normal Generation (`jrnl daily`)
1. Get timestamp of latest daily from database
2. If no previous daily exists, use logs from last 24 hours
3. Query logs with `timestamp >= latest_daily.timestamp`
4. Pass logs to LLM provider
5. Store generated message with today's date

### Regeneration (`jrnl daily --regenerate`)
1. Get today's daily from database (if exists)
2. Get the previous daily before today
3. Use previous daily's timestamp as cutoff
4. Generate new message from those logs
5. Replace today's daily (UNIQUE constraint on daily_date handles this)

### Key Insight
No need to calculate workdays! Just use timestamps from dailies table:
- Handles holidays/vacations automatically
- Works regardless of schedule variations
- Simple timestamp-based queries

## Installation Flow

### install.sh Script
1. Check Python 3.8+ available
2. Create `~/.jrnl/` directory structure
3. Create `~/.local/bin/` if it doesn't exist
4. Create venv: `python3 -m venv ~/.jrnl/venv`
5. Install dependencies: `pip install -r requirements.txt`
6. Initialize database: `python -c "from jrnl.database.connection import init_database; init_database()"`
7. Create default config.json
8. Prompt for git hook installation
9. Create CLI wrapper at `~/.local/bin/jrnl`
10. Check if `~/.local/bin` is in PATH
11. If not in PATH, display instructions to add it:
    - For bash: `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`
    - For zsh: `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc`
    - Remind user to reload shell or run `source ~/.bashrc`
12. Display setup instructions

### uninstall.sh Script
1. Confirm with user
2. Offer database backup
3. Remove git hooks (directly in script)
4. Remove `~/.jrnl/` directory
5. Remove `~/.local/bin/jrnl` wrapper
6. Display completion message

## Dependencies (requirements.txt)

```
anthropic>=0.39.0
requests>=2.31.0
```

## Implementation Order

### Phase 1: Core Infrastructure
1. Create directory structure and package files
2. Implement database layer (connection, models, operations, SQL)
3. Implement config.py
4. Create requirements.txt
5. Manual testing of database operations

### Phase 2: Utilities
1. Implement date_utils.py (date/time parsing, formatting, relative time)
2. Implement formatting.py (log display formatting)
3. Implement errors.py (custom exceptions)

### Phase 3: LLM Providers
1. Implement base.py (abstract interface)
2. Implement prompts.py (prompt templates)
3. Implement anthropic_provider.py
4. Implement ollama_provider.py
5. Implement factory pattern in __init__.py
6. Test with sample data

### Phase 4: CLI Commands
1. Implement new.py (simplest command)
2. Implement logs.py (read-only)
3. Implement config_cmd.py (config management)
4. Implement daily.py (most complex - standup generation)
5. Implement uninstall_cmd.py
6. Implement cli.py (routing) and __main__.py

### Phase 5: Git Integration
1. Create post-commit.template (calls `jrnl new --git`)
2. Implement commit_processor.py (extract commit info from git)
3. Update new.py to handle `--git`, `--repo-path`, `--commit-hash` flags
4. Test git commit processing with manual invocation
5. Hook installation/uninstallation will be handled in Phase 6 scripts

### Phase 6: Installation Scripts
1. Create install.sh script (includes git hook installation logic)
2. Create uninstall.sh script (includes git hook removal logic)
3. Test complete installation flow
4. Test hook installation with existing hooks
5. Handle edge cases (existing hooks from other tools, missing dependencies)

### Phase 7: Testing & Polish
1. End-to-end testing
2. Error handling improvements
3. Performance testing (LLM call times)
4. Documentation

## Critical Implementation Files

The following files are most critical and should be reviewed carefully during implementation:

1. **jrnl/database/connection.py**: Database initialization and connection management
2. **jrnl/llm_providers/base.py**: Abstract interface for all LLM providers
3. **jrnl/commands/new.py**: Handles both manual and git hook logging modes
4. **jrnl/commands/daily.py**: Complex standup generation logic with timestamp handling
5. **install.sh**: Main installation script, user's first interaction

## Security Considerations

1. **API Keys**: Stored in `~/.jrnl/config.json` plain text
   - Set file permissions to 600 during install
   - Future: Use OS keychain for better security

2. **Git Diffs**: Commit diffs sent to LLM provider
   - Anthropic: External API (has privacy policy)
   - Ollama: Local, no external transmission
   - User should be aware of what data is sent

3. **Database**: Contains work history
   - No sensitive data stored (just commit summaries)
   - Regular backups recommended

4. **Hook Safety**: Background execution with error handling
   - Never blocks commits
   - Fails silently with error logging

## Default Configuration

```json
{
    "active_llm_provider": "anthropic",
    "llm_providers": {
        "anthropic": {
            "api_key": "",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens_commit": 200,
            "max_tokens_daily": 500
        },
        "ollama": {
            "url": "http://localhost:11434",
            "model": "llama3.1:8b",
            "max_tokens_commit": 200,
            "max_tokens_daily": 500
        }
    },
    "git_hooks_enabled": true,
    "excluded_repos": [],
    "standup_time": "10:30",
    "timezone": "local"
}
```

**Benefits:**
- Each provider has its own configuration section
- Provider-specific settings (API key, model, URL, token limits)
- Easy to add new providers without config structure changes
- Can configure different token limits for commit compression vs daily generation

## Error Handling Strategy

1. **Git Hook Errors**: Log to `~/.jrnl/logs/errors.log`, never fail commit
2. **LLM Failures**: Fallback to raw commit message with [LLM Error] prefix
3. **Database Errors**: Raise exception with clear message to user
4. **Config Errors**: Merge with defaults, warn on invalid values
5. **API Key Missing**: Clear error message with setup instructions

## Future Enhancements (Not in Initial Scope)

- OpenAI and Gemini providers
- Custom prompt templates per organization
- Export to Markdown/PDF
- Integration with Jira/Linear
- Slack bot for posting standups
- Web UI for log viewing
- Team-specific formatting

## Success Criteria

Implementation is complete when:
1. ✓ install.sh script creates working environment
2. ✓ Manual logging works (`jrnl new -m "message"`)
3. ✓ Git hooks capture and compress commits
4. ✓ Daily standup generation works with both providers
5. ✓ All CLI commands function as specified
6. ✓ Configuration management works
7. ✓ uninstall.sh script removes everything cleanly
8. ✓ Error handling is robust (never blocks commits)
