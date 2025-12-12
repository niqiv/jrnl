"""jrnl daily command - Generate standup summaries."""

import sqlite3
from ..database.operations import (
    get_logs_since,
    get_latest_daily,
    get_previous_daily_before,
    get_daily_for_date,
    insert_daily,
    delete_daily
)
from ..database.models import Daily
from ..config import Config
from ..llm_providers import get_provider
from ..utils.date_utils import get_utc_now, get_current_date, get_datetime_ago
from ..utils.formatting import format_daily_header


def handle(args):
    """Handle the 'daily' command."""
    try:
        # Handle deletion if requested
        if hasattr(args, 'delete') and args.delete:
            return handle_delete(args.delete)

        config = Config.load()

        # Determine date range for logs
        if args.regenerate:
            cutoff = get_regenerate_cutoff()
        else:
            cutoff = get_normal_cutoff()

        # Get logs
        logs = get_logs_since(cutoff)

        if not logs:
            if args.regenerate:
                print("No logs found. Cannot regenerate - no previous daily exists.")
            else:
                print("No logs found since last daily. Try: jrnl logs")
            return 0

        print(f"Generating standup from {len(logs)} log entries...")

        # Get LLM provider
        provider = get_provider(config)

        # Generate daily message
        print("Generating standup (this may take 10-30 seconds)...")
        daily_message = provider.generate_daily(
            logs=[log.to_dict() for log in logs],
            days=args.days
        )

        # Save daily
        today = get_current_date()
        daily = Daily(
            timestamp=get_utc_now(),
            daily_date=today,
            daily_message=daily_message
        )

        insert_daily(daily)

        # Display result
        print(format_daily_header(today))
        print(daily_message)
        print("\n" + "="*60 + "\n")

        return 0

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 1
    except RuntimeError as e:  # From LLM providers
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error generating daily: {e}")
        import traceback
        traceback.print_exc()
        return 1


def handle_delete(date_arg: str) -> int:
    """Handle deleting a daily entry."""
    try:
        # Resolve date argument
        if date_arg.lower() in ['today', 'latest']:
            # Get today's date or latest daily date
            if date_arg.lower() == 'today':
                date = get_current_date()
            else:
                latest = get_latest_daily()
                if not latest:
                    print("No daily entries found.")
                    return 1
                date = latest.daily_date
        else:
            # Assume it's a date in YYYY-MM-DD format
            date = date_arg

        # Check if daily exists
        daily = get_daily_for_date(date)
        if not daily:
            print(f"No daily found for date: {date}")
            return 1

        # Delete the daily
        if delete_daily(date):
            print(f"Deleted daily for {date}")
            return 0
        else:
            print(f"Failed to delete daily for {date}")
            return 1

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 1
    except Exception as e:
        print(f"Error deleting daily: {e}")
        return 1


def get_normal_cutoff():
    """Get cutoff timestamp for normal daily generation."""
    latest_daily = get_latest_daily()
    if latest_daily:
        return latest_daily.timestamp
    else:
        # No previous daily - get logs from 24 hours ago
        return get_datetime_ago(hours=24)


def get_regenerate_cutoff():
    """Get cutoff timestamp for regenerating today's daily."""
    today = get_current_date()
    latest_daily = get_latest_daily()

    if latest_daily and latest_daily.daily_date == today:
        # Today's daily exists - get previous daily's timestamp
        prev_daily = get_previous_daily_before(today)
        if prev_daily:
            return prev_daily.timestamp

    # Fallback: 24 hours ago
    return get_datetime_ago(hours=24)
