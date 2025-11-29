"""jrnl new command - Create log entries."""

import uuid
import subprocess
import sqlite3
from pathlib import Path
from ..database.operations import insert_log
from ..database.models import Log
from ..utils.date_utils import get_utc_now
from ..utils.formatting import format_success, format_error
from ..config import Config
from ..llm_providers import get_provider


def handle(args):
    """Handle the 'new' command."""
    if args.git:
        # Git hook mode
        return handle_git_mode(args)
    else:
        # Manual mode
        return handle_manual_mode(args)


def handle_manual_mode(args):
    """Handle manual log entry."""
    # Validate required arguments
    if not args.message:
        print(format_error("Message is required. Use: jrnl new -m 'your message'"))
        return 1

    try:
        # Create log entry
        log = Log(
            timestamp=get_utc_now(),
            log_message=args.message,
            type='manual',
            label=args.label or str(uuid.uuid4())[:8]
        )

        # Save to database
        insert_log(log)

        print(format_success(f"Log entry created: {args.message}"))
        return 0

    except sqlite3.IntegrityError as e:
        print(format_error(f"Database constraint error: {e}"))
        return 1
    except sqlite3.Error as e:
        print(format_error(f"Database error: {e}"))
        return 1
    except Exception as e:
        print(format_error(f"Unexpected error: {e}"))
        import traceback
        traceback.print_exc()
        return 1


def handle_git_mode(args):
    """Handle git hook mode."""
    # Validate required arguments
    if not args.repo_path or not args.commit_hash:
        log_error("Git mode requires --repo-path and --commit-hash")
        return 1

    try:
        # Extract commit info
        commit_info = extract_commit_info(args.repo_path, args.commit_hash)
        if not commit_info:
            return 1  # Silently fail

        # Load config and get LLM provider
        config = Config.load()
        provider = get_provider(config)

        # Compress commit info
        log_message = provider.compress_commit(
            commit_message=commit_info['message'],
            commit_diff=commit_info['diff']
        )

        # Create log entry
        log = Log(
            timestamp=get_utc_now(),
            log_message=log_message,
            type='git-hook',
            label=commit_info['hash'][:8]
        )

        # Save to database
        insert_log(log)

        return 0

    except Exception as e:
        # Log error but don't fail (never block commits)
        log_error(f"Error processing commit: {type(e).__name__}: {e}")
        return 0  # Return success to avoid blocking commit


def extract_commit_info(repo_path: str, commit_hash: str) -> dict:
    """Extract commit message and diff."""
    try:
        # Get commit message
        result = subprocess.run(
            ['git', '-C', repo_path, 'log', '-1', '--pretty=%B', commit_hash],
            capture_output=True,
            text=True,
            timeout=5
        )
        commit_message = result.stdout.strip()

        # Get commit diff with context
        result = subprocess.run(
            ['git', '-C', repo_path, 'show', '--unified=3', '--no-color', commit_hash],
            capture_output=True,
            text=True,
            timeout=10
        )
        commit_diff = result.stdout

        # Truncate large diffs to avoid exceeding LLM context limits
        MAX_DIFF_SIZE = 50000  # characters
        if len(commit_diff) > MAX_DIFF_SIZE:
            commit_diff = commit_diff[:MAX_DIFF_SIZE] + "\n... (diff truncated for size)"

        return {
            'hash': commit_hash,
            'message': commit_message,
            'diff': commit_diff,
            'repo': repo_path
        }
    except FileNotFoundError:
        log_error("git command not found in PATH")
        return None
    except subprocess.TimeoutExpired:
        log_error("Git command timed out")
        return None
    except subprocess.CalledProcessError as e:
        log_error(f"Git command failed: {e}")
        return None
    except Exception as e:
        log_error(f"Unexpected error extracting commit: {type(e).__name__}: {e}")
        return None


def log_error(message: str):
    """Log error to error log file."""
    try:
        error_log = Path.home() / '.jrnl' / 'logs' / 'errors.log'
        error_log.parent.mkdir(parents=True, exist_ok=True)
        with open(error_log, 'a') as f:
            from datetime import datetime
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    except Exception:
        pass  # Silently fail logging
