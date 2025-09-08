from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.model_repository import ModelRepository
from src.adapters.db.user_model_repository import UserModelRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
from bot.keyboards.keyboards import Keyboard
from config.texts import model_subs_text


class SelectAiModelUseCase:
    def __init__(self, redis: RedisCache, keyboard: Keyboard):
        self.redis = redis
        self.keyboard = keyboard

    async def show_menu(self, user_id: int, session: AsyncSession):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                         session=session,
                                                         redis=self.redis)

        models = await ModelRepository.get_all_models(session=session, redis=self.redis)

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
                                                 selected=selected)


    async def set(self, user_id: int, model_id: int, session: AsyncSession):
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
            kbd = Keyboard.model_subs_keyboard(trial_used=trial_used)
            return model_subs_text, kbd

        await UserModelRepository.update_selected_model(user_id=user_id,
                                                        model_id=model_id,
                                                        session=session)

        models = await ModelRepository.get_all_models(session=session, redis=self.redis)

        return await self.generate_text_and_menu(description=model_info.description,
                                                 models=models,
                                                 allowed=allowed,
                                                 selected=model_id)


    async def generate_text_and_menu(self, description, models, allowed, selected):
        text = f'Описание выбранной модели: {description}'
        if description:
            text += '\n\nДоступные модели:'
        else:
            text = 'Доступные модели:'

        kbd = self.keyboard.select_ai_keyboard(ai_models_list=models,
                                               allowed_classes=allowed,
                                               selected=selected)
        return text, kbd