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
from app.db.models.user_ai_context import MessageType

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
            # в кэш пишем value ('text' / 'image_url' / 'file_url')
            "message_type": (
                msg.message_type.value if isinstance(msg.message_type, MessageType) else str(msg.message_type)
            ),
        }

    @staticmethod
    def _dict_to_msg(d: dict) -> MessageDTO:
        mt = d.get("message_type")
        # из строки -> Enum (бросит ValueError, если мусор)
        if isinstance(mt, str):
            mt = MessageType(mt)
        return MessageDTO(text=d["text"], author_id=d["author_id"], message_type=mt)


    async def save_message(
        self,
        dialog_id: int,
        author_id: int,
        text: str,
        session: AsyncSession,
        message_type: MessageType = MessageType.TEXT,
        model_id: int = 1
    ):
        await ChatHistoryRepository.save_message(session=session,
                                                 dialog_id=dialog_id,
                                                 author_id=author_id,
                                                 text=text,
                                                 message_type=message_type)

        await session.commit()

        key = ChatHistoryService._build_cache_key(dialog_id, model_id)
        entry = ChatHistoryService._msg_to_dict(MessageDTO(text=text, author_id=author_id, message_type=message_type))
        await self.redis.lpush(key, json.dumps(entry))
        await self.redis.ltrim(key, 0, HISTORY_LIMIT - 1)
        await self.redis.expire(key, CACHE_TTL_SECONDS)


    async def save_messages(self,
                            messages: list[MessageDTO],
                            dialog_id: int,
                            author_id: int,
                            session: AsyncSession,):
        for message in messages:
            public_id = await ChatHistoryRepository.save_message(
                dialog_id=dialog_id,
                author_id=author_id,
                text=message.text,
                message_type=message.message_type,
                session=session,
            )
        await session.commit()
        return public_id


    async def get_history(
        self,
        dialog_id: int,
        bot_id: int,
        model_id: int,
        session: AsyncSession
    ) -> list[ChatCompletionUserMessageParam | ChatCompletionAssistantMessageParam]:
        print('get history')

        key = ChatHistoryService._build_cache_key(dialog_id, model_id)

        cached = await self.redis.lrange(key, 0, HISTORY_LIMIT - 1)
        cached = False
        if cached:
            messages = [ChatHistoryService._dict_to_msg(json.loads(item)) for item in reversed(cached)]
        else:
            history_messages = await ChatHistoryRepository.load_history(session=session,
                                                                        dialog_id=dialog_id,
                                                                        limit=HISTORY_LIMIT)

            messages = []
            image_count = 0

            for history_message in history_messages:
                if model_id != 1 and history_message.message_type == MessageType.IMAGE_URL:
                    continue

                if history_message.message_type == MessageType.IMAGE_URL:
                    if image_count >= 2:
                        continue
                    image_count += 1

                messages.append(history_message)

            for msg in messages:
                await self.redis.lpush(key, json.dumps(self._msg_to_dict(msg)))
            await self.redis.ltrim(key, 0, HISTORY_LIMIT - 1)
            await self.redis.expire(key, CACHE_TTL_SECONDS)

        return [
            ChatHistoryService.msg_to_completion_param(msg, bot_id)
            for msg in messages
        ]

    @staticmethod
    def msg_to_completion_param(msg: MessageDTO, bot_id: int):
        print('msg to completion')
        print(msg.message_type)
        if msg.author_id != bot_id:
            if msg.message_type == MessageType.IMAGE_URL:
                return ChatCompletionUserMessageParam(
                    role="user",
                    content=[
                        {"type": "image_url", "image_url": {"url": msg.text}}
                    ]
                )
            elif msg.message_type == MessageType.FILE_URL:
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
