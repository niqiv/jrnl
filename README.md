# JRNL

A CLI tool for developers to automatically track work for daily standups using LLM-powered summaries.

## Features

- **Automatic Git Logging**: Captures commits via global git hooks
- **LLM-Powered Summarization**: Compresses commit info into concise standup messages
- **Multiple LLM Providers**: Support for Anthropic Claude and Ollama
- **Manual Logging**: Add work items manually
- **Daily Standup Generation**: Generate formatted standup messages from your work logs
- **Per-Repository Control**: Opt-out specific repositories from tracking

## Installation

```bash
./install.sh
```

This will:
1. Create a Python virtual environment at `~/.jrnl/venv`
2. Install dependencies
3. Initialize the SQLite database
4. Create default configuration
5. Optionally install global git hooks
6. Install the `jrnl` CLI command to `~/.local/bin`

## Configuration

After installation, configure your LLM provider:

```bash
# For Anthropic Claude
jrnl config set anthropic api_key YOUR_API_KEY

# Or for Ollama (local)
jrnl config set-provider ollama
```

Configuration file: `~/.jrnl/config.json`

## Usage

### Manual Logging

```bash
jrnl new -m "Had meeting with customer about the service"
```

### View Logs

```bash
# View recent logs
jrnl logs

# View logs from last N days
jrnl logs --days 3
```

### Generate Daily Standup

```bash
# Generate standup from logs since last daily
jrnl daily

# Generate standup covering multiple days
jrnl daily --days 2

# Regenerate today's standup
jrnl daily --regenerate

# Delete a daily entry
jrnl daily --delete 2024-12-12
jrnl daily --delete today
jrnl daily --delete latest
```

### Configuration Management

```bash
# Show current configuration
jrnl config

# Switch LLM provider
jrnl config set-provider ollama

# Set provider-specific settings
jrnl config set anthropic model claude-3-5-sonnet-20241022
jrnl config set anthropic max_tokens_daily 1000
```

### Repository Exclusion

```bash
# Exclude current repository from tracking
jrnl config exclude-current

# Exclude specific repository
jrnl config exclude /path/to/repo

# Re-enable repository
jrnl config include /path/to/repo
```

## How It Works

1. **Git Hooks**: When you make a commit, the post-commit hook captures the commit message and diff
2. **LLM Compression**: The commit info is processed through your chosen LLM to create a concise summary
3. **Database Storage**: Logs are stored in SQLite at `~/.jrnl/jrnl.db`
4. **Daily Generation**: When you run `jrnl daily`, all logs since your last daily are sent to the LLM to generate a formatted standup message

## Project Structure

```
~/.jrnl/                  # Application directory
├── config.json           # Configuration
├── jrnl.db              # SQLite database
├── venv/                # Python virtual environment
└── logs/                # Application logs
```

## Uninstallation

```bash
./uninstall.sh
```

Or from anywhere:

```bash
jrnl uninstall
```

## Requirements

- Python 3.8+
- Git
- Anthropic API key (for Claude) or Ollama installation (for local models)

## License

MIT

## Development

The project follows a modular structure:

- `jrnl/commands/` - CLI command implementations
- `jrnl/database/` - Database layer with SQLite
- `jrnl/llm_providers/` - LLM provider abstractions
- `jrnl/git_integration/` - Git hook and commit processing
- `jrnl/utils/` - Utility functions

To run from source:

```bash
python3 -m jrnl --help
```

