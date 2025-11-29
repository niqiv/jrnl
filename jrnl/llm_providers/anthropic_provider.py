"""Anthropic/Claude LLM provider."""

import anthropic
from typing import Dict, List
from .base import LLMProvider
from .prompts import COMPRESS_COMMIT_PROMPT, GENERATE_DAILY_PROMPT


class AnthropicProvider(LLMProvider):
    """Anthropic/Claude LLM provider."""

    def __init__(self, config: Dict):
        super().__init__(config)
        api_key = config.get('api_key', '')
        if not api_key:
            raise ValueError("Anthropic API key not configured. Run: jrnl config set anthropic api_key YOUR_KEY")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = config.get('model', 'claude-sonnet-4-5-20250929')
        self.max_tokens_commit = config.get('max_tokens_commit', 200)
        self.max_tokens_daily = config.get('max_tokens_daily', 500)

    def compress_commit(self, commit_message: str, commit_diff: str) -> str:
        """Compress commit using Claude."""
        prompt = COMPRESS_COMMIT_PROMPT.format(
            commit_message=commit_message,
            commit_diff=commit_diff
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens_commit,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except anthropic.AuthenticationError:
            return f"[Auth Error] {commit_message}"
        except anthropic.RateLimitError:
            return f"[Rate Limit] {commit_message}"
        except anthropic.APIError as e:
            return f"[API Error] {commit_message}"
        except Exception as e:
            return f"[LLM Error] {commit_message}"

    def generate_daily(self, logs: List[Dict], days: int = 1) -> str:
        """Generate daily standup using Claude."""
        # Format logs for prompt
        log_text = "\n".join([
            f"- [{log['type']}] {log['log_message']}"
            for log in logs
        ])

        prompt = GENERATE_DAILY_PROMPT.format(
            days=days,
            logs=log_text
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens_daily,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except anthropic.AuthenticationError:
            raise RuntimeError("Invalid Anthropic API key. Run: jrnl config set anthropic api_key YOUR_KEY")
        except anthropic.RateLimitError:
            raise RuntimeError("Anthropic API rate limit exceeded. Try again later or use ollama.")
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate daily: {type(e).__name__}: {e}")

    def test_connection(self) -> bool:
        """Test Anthropic API connection."""
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
