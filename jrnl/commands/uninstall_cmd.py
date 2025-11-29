"""jrnl uninstall command - Uninstall the application."""

import subprocess
import sys
from pathlib import Path


def handle(args):
    """Handle the 'uninstall' command."""
    print("This will run the uninstall script.")
    print("Note: You can also run ./uninstall.sh directly")

    # Confirm
    response = input("\nContinue with uninstall? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Uninstall cancelled")
        return 0

    # Find and run uninstall.sh
    # Assume it's in the git repo root
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        repo_root = Path(result.stdout.strip())
        uninstall_script = repo_root / 'uninstall.sh'

        if uninstall_script.exists():
            subprocess.run(['bash', str(uninstall_script)], check=True)
            return 0
        else:
            print(f"Error: uninstall.sh not found at {uninstall_script}")
            print("Please run the uninstall script manually")
            return 1

    except subprocess.CalledProcessError:
        print("Error: Could not locate uninstall script")
        print("Please run: ./uninstall.sh from the jrnl repository")
        return 1
