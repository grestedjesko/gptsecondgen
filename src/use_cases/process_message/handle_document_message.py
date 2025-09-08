from aiogram.types import Message
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.s3.s3_client import S3Client
from src.adapters.db.user_model_repository import UserModelRepository
from src.adapters.cache.redis_cache import RedisCache
from src.services.chat_history_service import ChatHistoryService
from src.services.permission.permission_service import PermissionService, PhotoPermissionStatus
from src.adapters.db.user_subs_repository import UserSubsRepository
from src.use_cases.process_message.process_message import ProcessMessageUseCase


class HandleDocumentMessageUseCase:
    def __init__(self,
                 redis: RedisCache,
                 s3client: S3Client,
                 chat_history: ChatHistoryService,
                 permission_service: PermissionService,
                 process_message_usecase: ProcessMessageUseCase,):
        self.redis = redis
        self.s3 = s3client
        self.chat_history = chat_history
        self.permission_service = permission_service
        self.process_message_usecase = process_message_usecase


    async def run(self, message: Message, sended_message: Message, bot: Bot, session: AsyncSession):
        default_image_model = 1
        user_subtype = await UserSubsRepository.get_subs_type(user_id=message.from_user.id, session=session, redis=self.redis)

        status = await self.permission_service.check_image_send_permission(sub_type=user_subtype)

        if status == PhotoPermissionStatus.NOT_ALLOWED_BY_TIER:
            await sended_message.edit_text('''На вашем тарифном плане нельзя загружать документы. Оформите подписку''')
            return

        if status == PhotoPermissionStatus.DAILY_LIMIT_EXCEEDED:
            await sended_message.edit_text('На сегодня все доступные распознавания докуентов закончились, оформите подписку чтобы убрать ограничения')
            return

        await sended_message.edit_text('📂 Открываю документ...')
        await UserModelRepository.update_selected_model(user_id=message.from_user.id,
                                                        model_id=default_image_model,
                                                        session=session)

        file_id = message.document.file_id
        tg_file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(tg_file.file_path)
        filename = getattr(message.document, "file_name", None)
        mime_type = message.document.mime_type

        key = f"uploads/{message.from_user.id}/{file_id}.pdf"
        pdf_link = await self.s3.upload_file(file_obj=file_bytes,
                                             file_key=key,
                                             filename=filename,
                                             mime_type=mime_type)

        chat_history = ChatHistoryService(self.redis)
        await chat_history.save_message(
            user_id=message.from_user.id,
            author_id=message.from_user.id,
            text=pdf_link,
            session=session,
            message_type="file_url",
            model_id=default_image_model
        )

        text = message.caption if message.caption else None

        await sended_message.edit_text('Пожалуйста, подождите немного')
        await self.process_message_usecase.run(model_id=default_image_model,
                                               user_id=message.from_user.id,
                                               sended_message=sended_message,
                                               bot=bot,
                                               session=session,
                                               text=text,
                                               user_subtype=user_subtype)
