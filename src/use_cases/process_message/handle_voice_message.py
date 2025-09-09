from aiogram.types import Message
from src.services.ai.data_classes import MessageDTO
from src.use_cases.process_message.process_message import ProcessMessageUseCase
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.permission.permission_service import PermissionService
from src.services.whisper_service import WhisperService
from src.adapters.cache.redis_cache import RedisCache
from src.services.ai.model_selection_service import ModelSelectionService
from src.adapters.db.user_subs_repository import UserSubsRepository
from src.services.ai.model_selection_service import ModelAccessStatus
from src.services.permission.permission_service import VoicePermissionStatus
from app.db.models.user_ai_context import MessageType


class HandleVoiceMessageUseCase:
    def __init__(self,
                 redis: RedisCache,
                 whisper: WhisperService,
                 model_selection_service: ModelSelectionService,
                 permission_service: PermissionService,
                 process_message_usecase: ProcessMessageUseCase):
        self.redis = redis
        self.whisper = whisper
        self.model_selection_service = model_selection_service
        self.permission_serivce = permission_service
        self.process_message_usecase = process_message_usecase

    async def run(self, message: Message, sended_message: Message, bot: Bot, session: AsyncSession):
        voice = message.voice

        user_subtype = await UserSubsRepository.get_subs_type(user_id=message.from_user.id, session=session, redis=self.redis)

        result = await self.permission_serivce.check_voice_availability(
            voice_duration=voice.duration,
            sub_type=user_subtype
        )

        if result.status == VoicePermissionStatus.NOT_ALLOWED_BY_TIER:
            await message.answer("Голосовые сообщения недоступны на вашем тарифе. Оформите подписку.")
            return

        if result.status == VoicePermissionStatus.TOO_LONG:
            await message.answer(
                f"Максимальная длительность голосового сообщения — {result.limit_seconds} секунд. "
                f"Ваше сообщение — {voice.duration} секунд. Укоротите его или обновите подписку."
            )
            return

        await sended_message.edit_text('🎙 Слушаю голосовое сообщение ...')
        text = await self.whisper.transcribe_voice(message, bot)

        model = await self.model_selection_service.get_model(user_id=message.from_user.id,
                                                             text=text,
                                                             session=session,
                                                             user_subtype=user_subtype)
        if not model.status == ModelAccessStatus.OK:
            return

        print(text)
        await sended_message.edit_text('Пожалуйста, подождите немного')

        user_id = message.from_user.id
        current_message = [MessageDTO(author_id=user_id, message_type=MessageType.TEXT, text=text)]

        await self.process_message_usecase.run(query_messages=current_message,
                                               model_id=model.id,
                                               user_id=message.from_user.id,
                                               sended_message=sended_message,
                                               bot_id=bot.id,
                                               session=session,
                                               user_subtype=user_subtype)