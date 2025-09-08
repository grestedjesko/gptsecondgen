import json
from typing import Literal

from src.adapters.cache.redis_cache import RedisCache
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.ai.data_classes import MessageDTO
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)
from src.adapters.db.chat_history_repository import ChatHistoryRepository

CACHE_TTL_SECONDS = 60 * 60 * 24 * 7
HISTORY_LIMIT = 10


class ChatHistoryService:
    def __init__(self, redis: RedisCache):
        self.redis = redis

    @staticmethod
    def _build_cache_key(user_id: int, model_id: int) -> str:
        return f"chat:history:{user_id}:{model_id}"

    @staticmethod
    def _msg_to_dict(msg: MessageDTO) -> dict:
        return {
            "text": msg.text,
            "author_id": msg.author_id,
            "message_type": msg.message_type,
        }

    @staticmethod
    def _dict_to_msg(d: dict) -> MessageDTO:
        return MessageDTO(**d)

    async def save_message(
        self,
        user_id: int,
        author_id: int,
        text: str,
        session: AsyncSession,
        message_type: Literal["text", "image_url"] = "text",
        model_id: int = 1
    ):
        await ChatHistoryRepository.save_message(session=session,
                                                 user_id=user_id,
                                                 author_id=author_id,
                                                 text=text,
                                                 message_type=message_type)

        key = ChatHistoryService._build_cache_key(user_id, model_id)
        entry = ChatHistoryService._msg_to_dict(MessageDTO(text=text, author_id=author_id, message_type=message_type))
        await self.redis.lpush(key, json.dumps(entry))
        await self.redis.ltrim(key, 0, HISTORY_LIMIT - 1)
        await self.redis.expire(key, CACHE_TTL_SECONDS)

    async def get_history(
        self,
        user_id: int,
        bot_id: int,
        model_id: int,
        session: AsyncSession
    ) -> list[ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam]:
        key = ChatHistoryService._build_cache_key(user_id, model_id)

        cached = await self.redis.lrange(key, 0, HISTORY_LIMIT - 1)

        if cached:
            # Парсим из Redis
            print('get cached')
            messages = [ChatHistoryService._dict_to_msg(json.loads(item)) for item in reversed(cached)]
        else:
            raw_messages = await ChatHistoryRepository.load_history(session=session,
                                                                    user_id=user_id,
                                                                    limit=HISTORY_LIMIT)

            messages = []
            image_count = 0
            for text, author_id, message_type in raw_messages:
                if model_id != 1 and message_type == "image_url":
                    continue

                if message_type == "image_url":
                    if image_count >= 2:
                        continue
                    image_count += 1

                messages.append(MessageDTO(author_id=author_id, message_type=message_type, text=text))

            messages = list(reversed(messages))

            for msg in reversed(messages):
                await self.redis.lpush(key, json.dumps(self._msg_to_dict(msg)))
            await self.redis.ltrim(key, 0, HISTORY_LIMIT - 1)
            await self.redis.expire(key, CACHE_TTL_SECONDS)

        return [
            ChatHistoryService._msg_to_completion_param(msg, bot_id)
            for msg in messages
        ]

    @staticmethod
    def _msg_to_completion_param(msg: MessageDTO, bot_id: int):
        if msg.author_id != bot_id:
            if msg.message_type == "image_url":
                return ChatCompletionUserMessageParam(
                    role="user",
                    content=[
                        {"type": "image_url", "image_url": {"url": msg.text}}
                    ]
                )
            elif msg.message_type == "file_url":
                filename = msg.text.split("/")[-1]
                return ChatCompletionUserMessageParam(
                    role="user",
                    content=[
                        {"type": "file", "file": {"filename": filename, "file_data": msg.text}}
                    ]
                )
            else:
                return ChatCompletionUserMessageParam(role="user", content=msg.text)
        return ChatCompletionAssistantMessageParam(role="assistant", content=msg.text)
