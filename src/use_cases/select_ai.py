from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.model_repository import ModelRepository
from src.adapters.db.user_model_repository import UserModelRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
from bot.keyboards.keyboards import Keyboard
from src.services.i18n_service import I18nService
from aiogram.types import User
from src.adapters.db.user_packets_repository import UserPacketsRepository
from app.config import Settings


class SelectAiModelUseCase:
    def __init__(self, redis: RedisCache, keyboard: Keyboard, config: Settings):
        self.config = config
        self.redis = redis
        self.keyboard = keyboard

    async def show_menu(self, user_id: int, session: AsyncSession, user: User):
        models = await ModelRepository.get_all_text_models_localized(session=session, 
                                                                     redis=self.redis, 
                                                                     user=user)

        selected = await UserModelRepository.get_selected_model_id(user_id=user_id,
                                                                   session=session)

        selected_model_info = await ModelRepository.get_model_info_localized(model_id=selected,
                                                                             session=session,
                                                                             redis=self.redis,
                                                                             user=user)


        return await self.generate_text_and_menu(description=selected_model_info.description,
                                                 models=models,
                                                 selected=selected,
                                                 user=user,
                                                 session=session)


    async def set(self, user_id: int, model_id: int, session: AsyncSession, user: User):
        if model_id in self.config.neiro_packet_models:
            neiro_packet = await UserPacketsRepository.get_packet(packet_type=1,
                                                                  user_id=user_id,
                                                                  session=session)
            if not neiro_packet:
                return await I18nService.get_text("model_subs_text", user, session), None 

        model_info = await ModelRepository.get_model_info_localized(model_id=model_id,
                                                                    session=session,
                                                                    redis=self.redis,
                                                                    user=user)
        if not model_info:
            return 'Неизвестная модель', None

        allowed = [1]

        if 1 not in allowed:
            trial_used = await UserSubsRepository.get_trial_used(user_id=user_id,
                                                                 session=session)
            kbd = await self.keyboard.model_subs_keyboard(trial_used=trial_used, user=user, session=session)
            return await I18nService.get_text("model_subs_text", user, session), kbd

        await UserModelRepository.update_selected_model(user_id=user_id,
                                                        model_id=model_id,
                                                        session=session)

        models = await ModelRepository.get_all_text_models_localized(session=session, redis=self.redis, user=user)

        return await self.generate_text_and_menu(description=model_info.description,
                                                 models=models, 
                                                 selected=model_id,
                                                 user=user,
                                                 session=session)


    async def generate_text_and_menu(self, description, models, selected, user: User, session: AsyncSession):
        if description:
            text = await I18nService.get_text("selected_model_description", user, session, description=description)
        else:
            text = await I18nService.get_text("available_models", user, session)

        kbd = await self.keyboard.select_ai_keyboard(ai_models_list=models,
                                                     neiro_packet_models=self.config.neiro_packet_models,
                                                     premium_models=self.config.premium_models,
                                                     selected=selected,
                                                     user=user,
                                                     session=session)
        return text, kbd