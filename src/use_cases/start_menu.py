from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.user_model_repository import UserModelRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
from typing import Tuple
from aiogram.types import  InlineKeyboardMarkup
from app.config import Settings
from bot.keyboards.keyboards import Keyboard
from src.adapters.db.model_repository import ModelRepository
from config.texts import nosubs_text, nosubs_trial_text, subs_text


class StartMenuUseCase:
    def __init__(self, config: Settings, keyboard: Keyboard, redis: RedisCache):
        self.config = config
        self.keyboard = keyboard
        self.redis = redis

    async def run(self, user_id: int, session: AsyncSession) -> Tuple[str, InlineKeyboardMarkup]:
        """
        Возвращает текст и клавиатуру в зависимости от подписки пользователя.
        """
        trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)
        subtype_id = await UserSubsRepository.get_subs_type(user_id=user_id, session=session, redis=self.redis)

        if subtype_id == 0:
            text = nosubs_text if trial_used else nosubs_trial_text
        else:
            model_id = await UserModelRepository.get_selected_model_id(user_id=user_id, session=session)
            model = await ModelRepository.get_model_info(model_id=model_id, session=session, redis=self.redis)
            text = subs_text % model.name
        return text, self.keyboard.main_keyboard(has_subs=bool(subtype_id), trial_used=trial_used)