from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.model_repository import ModelRepository
from src.adapters.db.user_model_repository import UserModelRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
from bot.keyboards.keyboards import Keyboard
from config.i18n import get_text
from aiogram.types import User


class SelectAiModelUseCase:
    def __init__(self, redis: RedisCache, keyboard: Keyboard):
        self.redis = redis
        self.keyboard = keyboard

    async def show_menu(self, user_id: int, session: AsyncSession, user: User):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                         session=session,
                                                         redis=self.redis)

        models = await ModelRepository.get_all_models_localized(session=session, redis=self.redis, user=user)

        allowed = await ModelRepository.get_allowed_classes(subtype_id=subtype,
                                                            session=session,
                                                            redis=self.redis)

        selected = await UserModelRepository.get_selected_model_id(user_id=user_id,
                                                                   session=session)

        selected_model_info = await ModelRepository.get_model_info(model_id=selected,
                                                                   session=session,
                                                                   redis=self.redis)


        return await self.generate_text_and_menu(description=selected_model_info.description,
                                                 models=models,
                                                 allowed=allowed,
                                                 selected=selected,
                                                 user=user)


    async def set(self, user_id: int, model_id: int, session: AsyncSession, user: User):
        subtype_id = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                            session=session,
                                                            redis=self.redis)

        model_info = await ModelRepository.get_model_info(model_id=model_id,
                                                          session=session,
                                                          redis=self.redis)
        if not model_info:
            return 'Неизвестная модель', None

        allowed = await ModelRepository.get_allowed_classes(subtype_id=subtype_id,
                                                            session=session,
                                                            redis=self.redis)

        if model_info.model_class_id not in allowed:
            trial_used = await UserSubsRepository.get_trial_used(user_id=user_id,
                                                                 session=session)
            kbd = Keyboard.model_subs_keyboard(trial_used=trial_used, user=user)
            return get_text("model_subs_text", user), kbd

        await UserModelRepository.update_selected_model(user_id=user_id,
                                                        model_id=model_id,
                                                        session=session)

        models = await ModelRepository.get_all_models_localized(session=session, redis=self.redis, user=user)

        return await self.generate_text_and_menu(description=model_info.description,
                                                 models=models,
                                                 allowed=allowed,
                                                 selected=model_id,
                                                 user=user)


    async def generate_text_and_menu(self, description, models, allowed, selected, user: User):
        if description:
            text = get_text("selected_model_description", user, description=description)
        else:
            text = get_text("available_models", user)

        kbd = self.keyboard.select_ai_keyboard(ai_models_list=models,
                                               allowed_classes=allowed,
                                               selected=selected,
                                               user=user)
        return text, kbd