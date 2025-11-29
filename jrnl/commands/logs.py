"""jrnl logs command - View log entries."""

import sqlite3
from ..database.operations import get_logs_since, get_all_logs
from ..utils.date_utils import get_datetime_ago
from ..utils.formatting import format_log_entry


def handle(args):
    """Handle the 'logs' command."""
    try:
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
