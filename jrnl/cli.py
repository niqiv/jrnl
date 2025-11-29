"""JRNL - Developer work journal for standups."""

import sys
import argparse
from .commands import new, daily, logs, config_cmd, uninstall_cmd
from .version import __version__


def create_parser():
    """Create the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog='jrnl',
        description='Developer work journal for standups'
    )
    parser.add_argument('--version', action='version', version=f'jrnl {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # jrnl new
    new_parser = subparsers.add_parser('new', help='Create a log entry')
    new_parser.add_argument('-m', '--message', help='Log message')
    new_parser.add_argument('-l', '--label', help='Optional label for this entry')
    new_parser.add_argument('--git', action='store_true', help='Git hook mode')
    new_parser.add_argument('--repo-path', help='Repository path (git mode)')
    new_parser.add_argument('--commit-hash', help='Commit hash (git mode)')

    # jrnl daily / standup
    daily_parser = subparsers.add_parser('daily', aliases=['standup'],
                                         help='Generate standup message')
    daily_parser.add_argument('-d', '--days', type=int, default=1,
                             help='Number of days to include (default: 1)')
    daily_parser.add_argument('-r', '--regenerate', action='store_true',
                             help='Regenerate last daily')

    # jrnl logs
    logs_parser = subparsers.add_parser('logs', help='View log entries')
    logs_parser.add_argument('-d', '--days', type=int,
                            help='Filter logs by number of days')
    logs_parser.add_argument('-n', '--limit', type=int, default=50,
                            help='Maximum number of logs to show (default: 50)')

    # jrnl config
    config_parser = subparsers.add_parser('config', help='Manage configuration')
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
