# adapters/ai_providers/openai_provider.py

from typing import Dict, Iterable, Optional, Tuple
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from src.adapters.ai_providers.base import ChatProvider


class OpenAIProvider(ChatProvider):
    name = "openai"

    def __init__(self, api_key: str, default_base_url: Optional[str] = None):
        """
        api_key — обязательно.
        default_base_url — будет использован, если base_url не передан в chat().
        """
        self.api_key = api_key
        self.default_base_url = default_base_url
        # Простой кэш клиентов по base_url, чтобы сохранять пула соединений httpx
        self._clients: Dict[Optional[str], AsyncOpenAI] = {}

    def _get_client(self, base_url: Optional[str]) -> AsyncOpenAI:
        """
        Возвращает кэшированный AsyncOpenAI для заданного base_url.
        При первом обращении создаёт новый клиент.
        """
        key = base_url or self.default_base_url
        if key not in self._clients:
            self._clients[key] = AsyncOpenAI(api_key=self.api_key, base_url=key)
        return self._clients[key]

    async def get_answer(
        self,
        *,
        prompt: str,
        messages: Iterable[ChatCompletionMessageParam],
        model: str,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> Tuple[str, Optional[int]]:
        """
        base_url — можно подставлять на каждый запрос (перекрывает default_base_url).
        """
        full_messages = [{"role": "system", "content": prompt}] + list(messages)

        client = self._get_client(base_url)
        print('full_messages', full_messages)

        resp = await client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,  # пробрасывается в httpx под капотом
        )

        text = resp.choices[0].message.content or ""
        total_tokens = resp.usage.total_tokens if resp.usage else None
        return text, total_tokens
