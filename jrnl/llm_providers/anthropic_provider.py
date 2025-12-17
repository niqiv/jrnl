"""Anthropic/Claude LLM provider."""

from typing import Dict, List
from .base import LLMProvider
from .prompts import COMPRESS_COMMIT_PROMPT, GENERATE_DAILY_PROMPT
import requests


class AnthropicProvider(LLMProvider):
    """Anthropic/Claude LLM provider."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        if not self.api_key:
            raise ValueError("Anthropic API key not configured. Run: jrnl config set anthropic api_key YOUR_KEY")

        self.model = config.get('model', 'claude-sonnet-4-5-20250929')
        self.max_tokens_commit = config.get('max_tokens_commit', 200)
        self.max_tokens_daily = config.get('max_tokens_daily', 500)
        
    def _send_message(self, prompt: dict, max_tokens=200) -> dict:
        res = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                'x-api-key': self.api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            },
            json={
                'model': self.model,
                'max_tokens': max_tokens,
                'temperature': 0.3,
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': prompt
                            }
                        ]
                    }
                ]
            }
        )

        return res.json()
        
    def compress_commit(self, commit_message: str, commit_diff: str) -> str:
        """Compress commit using Claude."""
        prompt = COMPRESS_COMMIT_PROMPT.format(
            commit_message=commit_message,
            commit_diff=commit_diff
        )

        try:
            message = self._send_message(
                prompt=prompt,
                max_tokens=self.max_tokens_commit,
            )
            
            return message.get('content', [])[0].get('text').strip()
        except IndexError as e:
            return f"[Anthropic Error] {commit_message}"
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
            message = self._send_message(
                prompt=prompt,
                max_tokens=self.max_tokens_daily,
            )
            
            return message.get('content', [])[0].get('text').strip()

        except IndexError as e:
            return f"[Anthropic Error] Failed to generate daily: {type(e).__name__}: {e}"
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
