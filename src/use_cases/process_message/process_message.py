from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import Bot
from aiogram.types import Message

from src.adapters.db.usage_repository import UsageRepository
from src.services.chat_history_service import ChatHistoryService
from src.services.ai.prompt_service import PromptService
from src.adapters.ai_providers.registry import ProviderRegistry
from src.adapters.db.model_repository import ModelRepository
from src.services.utils import get_week_start_date


class ProcessMessageUseCase:
    def __init__(self,
                 ai_providers: ProviderRegistry,
                 prompt_service: PromptService,
                 chat_history_service: ChatHistoryService,):
        self.chat_history = chat_history_service
        self.prompt_service = prompt_service
        self.ai_providers = ai_providers

    async def run(
        self,
        model_id: int,
        user_id: int,
        user_subtype: int,
        sended_message: Message,
        bot: Bot,
        session: AsyncSession,
        text: str
    ):
        await self.chat_history.save_message(
            user_id=user_id,
            author_id=user_id,
            text=text,
            session=session,
            model_id=model_id
        )

        prompt = await self.prompt_service.get_prompt(user_id=user_id, session=session)

        chat_history = await self.chat_history.get_history(user_id=user_id,
                                                           bot_id=bot.id,
                                                           model_id=model_id,
                                                           session=session)

        model_config = await ModelRepository.get_model_config(model_id=model_id, session=session)

        await sended_message.edit_text(f'🔄 [{model_config.name}] обрабатывает запрос, почти готово')

        ai_provider = self.ai_providers.get(name=model_config.api_provider)
        if not ai_provider:
            return await sended_message.edit_text('Ошибка провайдера')

        result_text, tokens_usage =  await ai_provider.get_answer(prompt=prompt,
                                                                  messages=chat_history,
                                                                  model=model_config.api_name,
                                                                  base_url=model_config.api_link)
        print(result_text)
        await sended_message.edit_text(result_text)

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

        if result_text:
            await self.chat_history.save_message(
                user_id=user_id,
                author_id=bot.id,
                text=result_text,
                session=session,
                model_id=model_id
            )