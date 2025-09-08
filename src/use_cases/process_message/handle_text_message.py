from aiogram.types import Message
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.services.ai.model_selection_service import ModelSelectionService
from src.services.permission.permission_service import PermissionService
from src.use_cases.process_message.process_message import ProcessMessageUseCase
from src.services.ai.model_selection_service import ModelAccessStatus
from src.adapters.db.user_subs_repository import UserSubsRepository


class HandleTextMessageUseCase:
    def __init__(self,
                 redis: RedisCache,
                 model_selection_service: ModelSelectionService,
                 permission_service: PermissionService,
                 process_message_usecase: ProcessMessageUseCase):
        self.redis = redis
        self.model_selection_service = model_selection_service
        self.permission_service = permission_service
        self.process_message_usecase = process_message_usecase


    async def run(self, message: Message, bot: Bot, sended_message: Message, session: AsyncSession):
        user_subtype = await UserSubsRepository.get_subs_type(user_id=message.from_user.id,
                                                              session=session,
                                                              redis=self.redis)

        model = await self.model_selection_service.get_model(user_id=message.from_user.id,
                                                             text=message.text,
                                                             user_subtype=user_subtype,
                                                             session=session)

        if not model.status == ModelAccessStatus.OK:
            return

        await self.process_message_usecase.run(model_id=model.id,
                                               user_id=message.from_user.id,
                                               user_subtype=user_subtype,
                                               sended_message=sended_message,
                                               bot=bot,
                                               session=session,
                                               text=message.text)

