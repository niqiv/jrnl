"""Configuration management for JRNL."""

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager."""

    CONFIG_PATH = Path.home() / '.jrnl' / 'config.json'

    DEFAULT_CONFIG = {
        'active_llm_provider': 'anthropic',
        'llm_providers': {
            'anthropic': {
                'api_key': '',
                'model': 'claude-sonnet-4-5-20250929',
                'max_tokens_commit': 200,
                'max_tokens_daily': 500
            },
            'ollama': {
                'url': 'http://localhost:11434',
                'model': 'llama3.1:8b',
                'max_tokens_commit': 200,
                'max_tokens_daily': 500
            }
        },
        'git_hooks_enabled': True,
        'excluded_repos': [],
        'standup_time': '10:30',
        'timezone': 'local'
    }

    @classmethod
    def load(cls) -> Dict[str, Any]:
        """Load configuration from file."""
        if not cls.CONFIG_PATH.exists():
            return cls.DEFAULT_CONFIG.copy()

        try:
            with open(cls.CONFIG_PATH, 'r') as f:
                config = json.load(f)

            # Merge with defaults (for new fields)
            merged = cls._deep_merge(cls.DEFAULT_CONFIG.copy(), config)
            return merged

        except FileNotFoundError:
            # Config doesn't exist - return defaults (this is normal for first run)
            return cls.DEFAULT_CONFIG.copy()
        except json.JSONDecodeError as e:
            print(f"Config file is corrupted at line {e.lineno}: {e.msg}")
            response = input("Recreate config with defaults? (y/N): ")
            if response.lower() == 'y':
                cls.save(cls.DEFAULT_CONFIG.copy())
                return cls.DEFAULT_CONFIG.copy()
            raise RuntimeError(f"Invalid config file at {cls.CONFIG_PATH}")
        except PermissionError as e:
            raise RuntimeError(f"Cannot read config file (permission denied): {cls.CONFIG_PATH}")
        except Exception as e:
            raise RuntimeError(f"Failed to load config: {type(e).__name__}: {e}")

    @classmethod
    def save(cls, config: Dict[str, Any]):
        """Save configuration to file."""
        try:
            cls.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_PATH, 'w') as f:
                json.dump(config, f, indent=2)

            # Set permissions to 600 for security (API keys)
            cls.CONFIG_PATH.chmod(0o600)

        except PermissionError:
            raise RuntimeError(f"Cannot write config file (permission denied): {cls.CONFIG_PATH}")
        except OSError as e:
            raise RuntimeError(f"Failed to write config file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to save config: {type(e).__name__}: {e}")

    @classmethod
    def get(cls, key: str, default=None):
        """Get a configuration value."""
        config = cls.load()
        return config.get(key, default)

    @classmethod
    def set(cls, key: str, value):
        """Set a configuration value."""
        config = cls.load()
        config[key] = value
        cls.save(config)

    @classmethod
    def _deep_merge(cls, base: Dict, updates: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
