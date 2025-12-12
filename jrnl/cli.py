"""JRNL - Developer work journal for standups."""

import sys
import argparse
from .commands import new, daily, logs, config_cmd, uninstall_cmd
from .version import __version__


def create_parser():
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog='jrnl',
        description='Developer work journal for standups - automatically track your work with git hooks and LLM-powered summaries',
        epilog='Run "jrnl <command> --help" for more information on a specific command.'
    )
    parser.add_argument('--version', action='version', version=f'jrnl {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # jrnl new
    new_parser = subparsers.add_parser(
        'new',
        help='Create a log entry',
        epilog='''
Examples:
  # Create a manual log entry
  jrnl new -m "fixed authentication bug"

  # Add an old commit manually
  jrnl new --git --repo-path "$(pwd)" --commit-hash abc123

  # Add multiple old commits
  for hash in $(git log -5 --format=%%H); do
    jrnl new --git --repo-path "$(pwd)" --commit-hash "$hash"
  done
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    new_parser.add_argument('-m', '--message', help='Log message for manual entry')
    new_parser.add_argument('-l', '--label', help='Optional label for this entry')
    new_parser.add_argument('--git', action='store_true',
                           help='Git mode: process a commit with LLM compression')
    new_parser.add_argument('--repo-path', help='Repository path (required with --git)')
    new_parser.add_argument('--commit-hash', help='Commit hash to process (required with --git)')

    # jrnl daily / standup
    daily_parser = subparsers.add_parser(
        'daily',
        aliases=['standup'],
        help='Generate standup message from your logs',
        epilog='''
Examples:
  # Generate today's standup
  jrnl daily

  # Regenerate today's standup with latest logs
  jrnl daily --regenerate

  # Generate standup including last 2 days
  jrnl daily --days 2

  # Delete a daily entry
  jrnl daily --delete 2024-12-12
  jrnl daily --delete today
  jrnl daily --delete latest
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    daily_parser.add_argument('-d', '--days', type=int, default=1,
                             help='Number of days to include (default: 1)')
    daily_parser.add_argument('-r', '--regenerate', action='store_true',
                             help='Regenerate today\'s standup with latest logs')
    daily_parser.add_argument('--delete', metavar='DATE',
                             help='Delete a daily entry (DATE: YYYY-MM-DD, "today", or "latest")')

    # jrnl logs
    logs_parser = subparsers.add_parser(
        'logs',
        help='View log entries',
        epilog='''
Examples:
  # View last 50 logs (default)
  jrnl logs

  # View last 10 logs
  jrnl logs -n 10

  # View logs from last 3 days
  jrnl logs --days 3

  # Delete a log entry by hash/label
  jrnl logs --delete 5a546f30
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    logs_parser.add_argument('-d', '--days', type=int,
                            help='Filter logs by number of days')
    logs_parser.add_argument('-n', '--limit', type=int, default=50,
                            help='Maximum number of logs to show (default: 50)')
    logs_parser.add_argument('--delete', metavar='HASH',
                            help='Delete a log entry by its hash/label')

    # jrnl config
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration',
        epilog='''
Examples:
  # Show current configuration
  jrnl config

  # Set LLM provider
  jrnl config set-provider anthropic
  jrnl config set-provider ollama

  # Configure Anthropic API key and model
  jrnl config set anthropic api_key sk-ant-...
  jrnl config set anthropic model claude-sonnet-4-5-20250929

  # Exclude repositories from git hooks
  jrnl config exclude /path/to/repo
  jrnl config exclude-current

  # Re-enable a repository
  jrnl config include /path/to/repo
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    config_parser.add_argument('action', nargs='?',
                              choices=['show', 'set-provider', 'set', 'exclude', 'include', 'exclude-current'],
                              help='Configuration action')
    config_parser.add_argument('args', nargs='*', help='Action arguments')

    # jrnl uninstall
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall jrnl')
    uninstall_parser.add_argument('--no-backup', action='store_true',
                                 help='Skip database backup')

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    try:
        # Route to appropriate command handler
        if args.command == 'new':
            return new.handle(args)
        elif args.command in ['daily', 'standup']:
            return daily.handle(args)
        elif args.command == 'logs':
            return logs.handle(args)
        elif args.command == 'config':
            return config_cmd.handle(args)
        elif args.command == 'uninstall':
            return uninstall_cmd.handle(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\nInterrupted")
        return 130
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
