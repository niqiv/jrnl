"""Git commit processing utilities."""

import subprocess
from typing import Optional, Dict


def extract_commit_info(repo_path: str, commit_hash: str) -> Optional[Dict]:
    """
    Extract commit message and diff from a git repository.

    Args:
        repo_path: Path to git repository
        commit_hash: Commit hash to extract

    Returns:
        Dictionary with commit info or None if extraction fails
    """
    try:
        # Get commit message
        result = subprocess.run(
            ['git', '-C', repo_path, 'log', '-1', '--pretty=%B', commit_hash],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return None

        commit_message = result.stdout.strip()

        # Get commit diff with context
        result = subprocess.run(
            ['git', '-C', repo_path, 'show', '--unified=3', '--no-color', commit_hash],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return None

        commit_diff = result.stdout

        return {
            'hash': commit_hash,
            'message': commit_message,
            'diff': commit_diff,
            'repo': repo_path
        }

    except FileNotFoundError:
        # git not in PATH
        return None
    except subprocess.TimeoutExpired:
        return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        # Catch-all for other subprocess errors
        return None


def get_repo_name(repo_path: str) -> str:
    """Get repository name from path."""
    from pathlib import Path
    return Path(repo_path).name
