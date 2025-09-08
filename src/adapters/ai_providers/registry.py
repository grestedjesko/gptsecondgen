from typing import Dict
from src.adapters.ai_providers.base import ChatProvider
from src.adapters.ai_providers.openai_provider import OpenAIProvider

class ProviderRegistry:
    def __init__(self, tokens: dict):
        self._providers: Dict[str, ChatProvider] = {
            'openai': OpenAIProvider(api_key=tokens['openai']),
        }

    def register(self, name: str, provider: ChatProvider):
        self._providers[name] = provider

    def get(self, name: str) -> ChatProvider:
        try:
            return self._providers[name]
        except KeyError:
            raise ValueError(f"Provider '{name}' is not registered.")
