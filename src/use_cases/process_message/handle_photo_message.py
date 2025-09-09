from aiogram.types import Message
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user_ai_context import MessageType
from src.adapters.s3.s3_client import S3Client
from src.adapters.db.user_model_repository import UserModelRepository
from src.adapters.cache.redis_cache import RedisCache
from src.services.permission.permission_service import PermissionService, PhotoPermissionStatus
from src.adapters.db.user_subs_repository import UserSubsRepository
from src.use_cases.process_message.process_message import ProcessMessageUseCase
from src.services.ai.data_classes import MessageDTO


class HandlePhotoMessageUseCase:
    def __init__(self,
                 redis: RedisCache,
                 s3client: S3Client,
                 permission_service: PermissionService,
                 process_message_usecase: ProcessMessageUseCase,):
        self.redis = redis
        self.s3 = s3client
        self.permission_service = permission_service
        self.process_message_usecase = process_message_usecase


    async def run(self, message: Message, sended_message: Message, bot: Bot, session: AsyncSession):
        default_image_model = 1
        user_subtype = await UserSubsRepository.get_subs_type(user_id=message.from_user.id, session=session, redis=self.redis)

        status = await self.permission_service.check_image_send_permission(sub_type=user_subtype)

        if status == PhotoPermissionStatus.NOT_ALLOWED_BY_TIER:
            await sended_message.edit_text('''На вашем тарифном плане нельзя загружать изображения. Оформите подписку''')
            return

        if status == PhotoPermissionStatus.DAILY_LIMIT_EXCEEDED:
            await sended_message.edit_text('На сегодня все доступные распознавания изображений закончились, оформите подписку чтобы убрать ограничения')
            return

        await sended_message.edit_text('🖼 Распознаю фото')
        await UserModelRepository.update_selected_model(user_id=message.from_user.id,
                                                        model_id=default_image_model,
                                                        session=session)

        file_id = message.photo[-1].file_id
        tg_file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(tg_file.file_path)

        key = f"uploads/{message.from_user.id}/{file_id}.jpg"
        image_link = await self.s3.upload_file(file_obj=file_bytes, file_key=key)

        parts: list[MessageDTO] = [
            MessageDTO(author_id=message.from_user.id, message_type=MessageType.IMAGE_URL, text=image_link)
        ]
        if message.caption:
            parts.append(
                MessageDTO(author_id=message.from_user.id, message_type=MessageType.TEXT, text=message.caption))

        await sended_message.edit_text('Пожалуйста, подождите немного')
        await self.process_message_usecase.run(query_messages=parts,
                                               model_id=default_image_model,
                                               user_id=message.from_user.id,
                                               sended_message=sended_message,
                                               bot_id=bot.id,
                                               session=session,
                                               user_subtype=user_subtype)