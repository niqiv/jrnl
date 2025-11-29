"""LLM provider factory and exports."""

from .base import LLMProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider

PROVIDERS = {
    'anthropic': AnthropicProvider,
    'ollama': OllamaProvider,
}


def get_provider(config: dict) -> LLMProvider:
    """Get the configured LLM provider."""
    provider_name = config.get('active_llm_provider', 'anthropic')

    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown LLM provider: {provider_name}")

    provider_config = config.get('llm_providers', {}).get(provider_name, {})
    return PROVIDERS[provider_name](provider_config)


__all__ = ['LLMProvider', 'AnthropicProvider', 'OllamaProvider', 'get_provider']
