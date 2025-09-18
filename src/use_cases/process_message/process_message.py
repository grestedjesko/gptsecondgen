from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message
from src.services.ai.model_selection_service import ModelSelectionService, ModelAccessStatus
from app.db.models.user_ai_context import MessageType
from src.adapters.db.dialog_repository import DialogRepository
from src.adapters.db.usage_repository import UsageRepository
from src.services.chat_history_service import ChatHistoryService
from src.services.ai.prompt_service import PromptService
from src.adapters.ai_providers.registry import ProviderRegistry
from src.adapters.db.model_repository import ModelRepository
from src.services.utils import get_week_start_date
from src.services.ai.data_classes import MessageDTO
from src.services.html_sanitizer import sanitize_to_telegram_html
import re

TELEGRAM_LIMIT = 4096


class ProcessMessageUseCase:
    def __init__(self,
                 ai_providers: ProviderRegistry,
                 prompt_service: PromptService,
                 chat_history_service: ChatHistoryService,
                 model_selection_service: ModelSelectionService,):
        self.chat_history = chat_history_service
        self.prompt_service = prompt_service
        self.ai_providers = ai_providers
        self.model_selection_service = model_selection_service

    async def run(
        self,
        query_messages: list[MessageDTO],
        user_id: int,
        user_subtype: int,
        sended_message: Message,
        bot_id: int,
        session: AsyncSession,
        model_id: int = None
    ):
        current_dialog = await DialogRepository.get_last(user_id=user_id, session=session)
        if not current_dialog:
            dialog_name = 'Dialog name'
            current_dialog = await DialogRepository.create(user_id=user_id,
                                                           name=dialog_name,
                                                           session=session)

        prompt = await self.prompt_service.get_prompt(user_id=user_id, session=session)

        chat_history = await self.chat_history.get_history(dialog_id=current_dialog.id,
                                                           bot_id=bot_id,
                                                           model_id=model_id,
                                                           session=session)

        new_messages = [self.chat_history.msg_to_completion_param(i, bot_id) for i in query_messages]

        messages_for_llm = chat_history + new_messages


        if not model_id:
            model = await self.model_selection_service.get_model(user_id=user_id,
                                                                 messages=messages_for_llm,
                                                                 user_subtype=user_subtype,
                                                                 session=session)

            if not model.status == ModelAccessStatus.OK:
                return

            model_id = model.model_id


        model_config = await ModelRepository.get_model_config(model_id=model_id, session=session)

        await sended_message.edit_text(f'🔄 [{model_config.name}] обрабатывает запрос, почти готово')

        ai_provider = self.ai_providers.get(name=model_config.api_provider)
        if not ai_provider:
            return await sended_message.edit_text('Ошибка провайдера')

        result_text, tokens_usage =  await ai_provider.get_answer(prompt=prompt,
                                                                  messages=messages_for_llm,
                                                                  model=model_config.api_name,
                                                                  base_url=model_config.api_link)

        safe_text = sanitize_to_telegram_html(result_text)

        if not result_text:
            return await sended_message.edit_text('Ошибка')

        await self.edit_long_message(sended_message, safe_text, parse_mode='html')

        result_message = [MessageDTO(text=result_text, author_id=user_id, message_type=MessageType.TEXT)]

        messages_to_save = query_messages + result_message

        last_id = await self.chat_history.save_messages(
            messages=messages_to_save,
            dialog_id=current_dialog.id,
            author_id=user_id,
            session=session,
        )

        print(last_id)

        if user_subtype == 0:
            await UsageRepository.add_week_usage(messages_used=1,
                                                 tokens_used=tokens_usage,
                                                 user_id=user_id,
                                                 model_class=model_config.ai_class,
                                                 week_start=await get_week_start_date(),
                                                 session=session)
        else:
            await UsageRepository.add_day_usage(messages_used=1,
                                                tokens_used=tokens_usage,
                                                user_id=user_id,
                                                model_class=model_config.ai_class,
                                                day=date.today(),
                                                session=session)

    async def edit_long_message(self, msg, text, parse_mode=None):
        # сначала пробуем как есть
        chunks = [text[i:i + TELEGRAM_LIMIT] for i in range(0, len(text), TELEGRAM_LIMIT)]
        if len(chunks) == 1:
            try:
                await msg.edit_text(text, parse_mode=parse_mode)
                return
            except Exception:
                pass
        plain = re.sub(r"<[^>]*>", "", text)
        chunks = [plain[i:i + TELEGRAM_LIMIT] for i in range(0, len(plain), TELEGRAM_LIMIT)]
        try:
            await msg.edit_text(chunks[0])
        except Exception as e:
            await msg.reply(chunks[0])
        for ch in chunks[1:]:
            await msg.reply(ch)
