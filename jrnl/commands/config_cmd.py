"""jrnl config command - Manage configuration."""

import os
import subprocess
from ..config import Config
from ..utils.formatting import format_success


def handle(args):
    """Handle the 'config' command."""
    config = Config.load()

    if not args.action or args.action == 'show':
        return show_config(config)
    elif args.action == 'set-provider':
        return set_provider(config, args)
    elif args.action == 'set':
        return set_value(config, args)
    elif args.action == 'exclude':
        return exclude_repo(config, args)
    elif args.action == 'include':
        return include_repo(config, args)
    elif args.action == 'exclude-current':
        return exclude_current_repo(config)
    else:
        print(f"Unknown action: {args.action}")
        return 1


def show_config(config):
    """Show current configuration."""
    print("\nCurrent Configuration:")
    print(f"  Active LLM Provider: {config.get('active_llm_provider')}")
    print(f"  Git Hooks Enabled: {config.get('git_hooks_enabled')}")
    print(f"  Standup Time: {config.get('standup_time')}")

    # Show LLM provider settings
    print("\n  LLM Providers:")
    providers = config.get('llm_providers', {})
    for provider_name, provider_config in providers.items():
        print(f"\n    {provider_name}:")
        for key, value in provider_config.items():
            if key == 'api_key' and value:
                # Mask API key - show last 4 chars if long enough, otherwise full mask
                if len(value) > 4:
                    print(f"      {key}: {'*' * 8}{value[-4:]}")
                else:
                    print(f"      {key}: {'*' * len(value)}")
            else:
                print(f"      {key}: {value}")

    # Show excluded repos
    excluded = config.get('excluded_repos', [])
    print(f"\n  Excluded Repositories: {len(excluded)}")
    for repo in excluded:
        print(f"    - {repo}")

    return 0


def set_provider(config, args):
    """Switch active LLM provider."""
    if len(args.args) != 1:
        print("Usage: jrnl config set-provider <provider>")
        return 1

    provider = args.args[0]
    if provider not in config.get('llm_providers', {}):
        print(f"Unknown provider: {provider}")
        print(f"Available: {', '.join(config.get('llm_providers', {}).keys())}")
        return 1

    config['active_llm_provider'] = provider
    Config.save(config)
    print(format_success(f"Active LLM provider set to {provider}"))
    return 0


def set_value(config, args):
    """Set provider-specific value."""
    if len(args.args) != 3:
        print("Usage: jrnl config set <provider> <key> <value>")
        return 1

    provider, key, value = args.args

    if provider not in config.get('llm_providers', {}):
        print(f"Unknown provider: {provider}")
        return 1

    # Get allowed keys from default config
    from ..config import Config as ConfigClass
    allowed_keys = ConfigClass.DEFAULT_CONFIG['llm_providers'].get(provider, {}).keys()

    if key not in allowed_keys:
        print(f"Unknown key '{key}' for provider '{provider}'")
        print(f"Allowed keys: {', '.join(allowed_keys)}")
        return 1

    # Convert numeric values
    if value.isdigit():
        value = int(value)

    config['llm_providers'][provider][key] = value
    Config.save(config)

    # Mask API key in output
    display_value = value
    if key == 'api_key' and value:
        if len(str(value)) > 4:
            display_value = f"{'*' * 8}{str(value)[-4:]}"
        else:
            display_value = '*' * len(str(value))

    print(format_success(f"Set {provider}.{key} = {display_value}"))
    return 0


def exclude_repo(config, args):
    """Add repository to exclude list."""
    if len(args.args) != 1:
        print("Usage: jrnl config exclude <repo-path>")
        return 1

    repo_path = os.path.abspath(args.args[0])
    excluded = config.get('excluded_repos', [])

    if repo_path in excluded:
        print(f"Repository already excluded: {repo_path}")
        return 0

    excluded.append(repo_path)
    config['excluded_repos'] = excluded
    Config.save(config)
    print(format_success(f"Excluded repository: {repo_path}"))
    return 0


def include_repo(config, args):
    """Remove repository from exclude list."""
    if len(args.args) != 1:
        print("Usage: jrnl config include <repo-path>")
        return 1

    repo_path = os.path.abspath(args.args[0])
    excluded = config.get('excluded_repos', [])

    if repo_path not in excluded:
        print(f"Repository not in exclude list: {repo_path}")
        return 0

    excluded.remove(repo_path)
    config['excluded_repos'] = excluded
    Config.save(config)
    print(format_success(f"Re-enabled repository: {repo_path}"))
    return 0


def exclude_current_repo(config):
    """Exclude current repository."""
    try:
        # Get current git repo path
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        repo_path = result.stdout.strip()

        excluded = config.get('excluded_repos', [])
        if repo_path in excluded:
            print(f"Current repository already excluded: {repo_path}")
            return 0

        excluded.append(repo_path)
        config['excluded_repos'] = excluded
        Config.save(config)
        print(format_success(f"Excluded current repository: {repo_path}"))
        return 0

    except subprocess.CalledProcessError:
        print("Error: Not in a git repository")
        return 1
    except RuntimeError as e:  # From Config class
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1
