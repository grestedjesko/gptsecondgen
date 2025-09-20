from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User
from bot.keyboards.keyboards import Keyboard
from config.i18n import Language
from src.adapters.db.user_repository import UserRepository
from src.services.i18n_service import I18nService


class SettingsUseCase:
    def __init__(self, keyboard: Keyboard):
        self.keyboard = keyboard

    async def run(self, user_id: int, session: AsyncSession, user: User):
        """Показывает главное меню настроек"""
        # Получаем сохраненный язык пользователя
        saved_language = await UserRepository.get_user_language(user_id, session)
        
        # Определяем текущий язык
        current_language = Language.RU if saved_language == 'ru' else Language.EN
        language_name = "🇷🇺 Русский" if current_language == Language.RU else "🇺🇸 English"
        
        text = await I18nService.get_text("settings_title", user, session) + "\n\n"
        text += await I18nService.get_text("settings_language_current", user, session, language=language_name)
        
        kbd = self.keyboard.settings_keyboard(user, saved_language)
        return text, kbd

    async def show_language_selection(self, user_id: int, session: AsyncSession, user: User):
        """Показывает меню выбора языка"""
        text = await I18nService.get_text("settings_language", user, session)
        kbd = self.keyboard.language_selection_keyboard(user)
        return text, kbd

    async def change_language(self, user_id: int, language: str, session: AsyncSession, user: User):
        """Изменяет язык пользователя"""
        # Сохраняем язык в базе данных
        await UserRepository.set_user_language(user_id, language, session)
        
        # Определяем название языка для отображения
        language_name = "🇷🇺 Русский" if language == 'ru' else "🇺🇸 English"
        
        text = await I18nService.get_text_with_language("language_changed", user, language, language=language_name)
        kbd = self.keyboard.settings_keyboard(user, saved_language=language)
        return text, kbd
