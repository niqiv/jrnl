"""Ollama local LLM provider."""

import requests
from typing import Dict, List
from .base import LLMProvider
from .prompts import COMPRESS_COMMIT_PROMPT, GENERATE_DAILY_PROMPT


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config.get('url', 'http://localhost:11434')
        self.model = config.get('model', 'llama3.1:8b')
        self.max_tokens_commit = config.get('max_tokens_commit', 200)
        self.max_tokens_daily = config.get('max_tokens_daily', 500)

    def compress_commit(self, commit_message: str, commit_diff: str) -> str:
        """Compress commit using Ollama."""
        prompt = COMPRESS_COMMIT_PROMPT.format(
            commit_message=commit_message,
            commit_diff=commit_diff
        )

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": self.max_tokens_commit
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response'].strip()
        except requests.exceptions.ConnectionError:
            return f"[Ollama Not Running] {commit_message}"
        except requests.exceptions.Timeout:
            return f"[Ollama Timeout] {commit_message}"
        except requests.exceptions.RequestException as e:
            return f"[Ollama Error] {commit_message}"
        except Exception as e:
            return f"[LLM Error] {commit_message}"

    def generate_daily(self, logs: List[Dict], days: int = 1) -> str:
        """Generate daily standup using Ollama."""
        log_text = "\n".join([
            f"- [{log['type']}] {log['log_message']}"
            for log in logs
        ])

        prompt = GENERATE_DAILY_PROMPT.format(
            days=days,
            logs=log_text
        )

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,
                        "num_predict": self.max_tokens_daily
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response'].strip()
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Cannot connect to Ollama. Is it running at http://localhost:11434?")
        except requests.exceptions.Timeout:
            raise RuntimeError("Ollama request timed out. Try a faster model or increase timeout.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama HTTP error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate daily with Ollama: {type(e).__name__}: {e}")

    def test_connection(self) -> bool:
        """Test Ollama connection."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
