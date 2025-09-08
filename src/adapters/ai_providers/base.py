from abc import ABC, abstractmethod
from typing import Iterable
from openai.types.chat import ChatCompletionMessageParam


class ChatProvider(ABC):
    name: str  # для выбора по имени

    @abstractmethod
    async def get_answer(self, prompt: str, messages: Iterable[ChatCompletionMessageParam], model: str, base_url: str) -> str:
        """Асинхронный генератор чанков текста"""
        ...
