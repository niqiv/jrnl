"""jrnl logs command - View log entries."""

import sqlite3
from ..database.operations import get_logs_since, get_all_logs, get_log_by_label, delete_log
from ..utils.date_utils import get_datetime_ago
from ..utils.formatting import format_log_entry, format_success, format_error


def handle(args):
    """Handle the 'logs' command."""
    try:
        # Handle deletion if --delete flag is provided
        if args.delete:
            return handle_delete(args.delete)

        # Get logs based on filters
        if args.days:
            cutoff = get_datetime_ago(days=args.days)
            logs = get_logs_since(cutoff)
        else:
            logs = get_all_logs(limit=args.limit)

        if not logs:
            print("No logs found")
            return 0

        # Display logs
        print(f"\nShowing {len(logs)} log entries:\n")
        for log in logs:
            print(format_log_entry(log))

        return 0

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_delete(label: str):
    """Handle log deletion with confirmation."""
    try:
        # Find the log entry
        log = get_log_by_label(label)

        if not log:
            print(format_error(f"Log entry not found: {label}"))
            return 1

        # Show the log entry to be deleted
        print("\nLog entry to be deleted:")
        print(format_log_entry(log))

        # Ask for confirmation
        response = input("\nAre you sure you want to delete this log entry? (y/N): ")

        if response.lower() != 'y':
            print("Deletion cancelled")
            return 0

        # Delete the log
        if delete_log(label):
            print(format_success(f"Log entry deleted: {label}"))
            return 0
        else:
            print(format_error(f"Failed to delete log entry: {label}"))
            return 1

    except sqlite3.Error as e:
        print(format_error(f"Database error: {e}"))
        return 1
    except Exception as e:
        print(format_error(f"Unexpected error: {type(e).__name__}: {e}"))
        import traceback
        traceback.print_exc()
        return 1
