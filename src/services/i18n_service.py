from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User
from config.i18n import get_text as original_get_text
from src.adapters.db.user_repository import UserRepository


class I18nService:
    """Сервис для работы с интернационализацией с учетом сохраненного языка пользователя"""
    
    @staticmethod
    async def get_text(key: str, user: User, session: AsyncSession, **kwargs) -> str:
        """
        Получает переведенный текст для пользователя с учетом сохраненного языка
        
        Args:
            key: Ключ текста
            user: Объект пользователя Telegram
            session: Сессия базы данных
            **kwargs: Параметры для форматирования строки
        
        Returns:
            Переведенный текст
        """
        # Получаем сохраненный язык пользователя
        saved_language = await UserRepository.get_user_language(user.id, session)
        
        # Используем оригинальную функцию get_text с сохраненным языком
        return original_get_text(key, user, saved_language, **kwargs)
    
    @staticmethod
    async def get_text_with_language(key: str, user: User, saved_language: str, **kwargs) -> str:
        """
        Получает переведенный текст для пользователя с указанным языком
        
        Args:
            key: Ключ текста
            user: Объект пользователя Telegram
            saved_language: Сохраненный язык пользователя
            **kwargs: Параметры для форматирования строки
        
        Returns:
            Переведенный текст
        """
        return original_get_text(key, user, saved_language, **kwargs)
    
    @staticmethod
    async def get_user_language(user_id: int, session: AsyncSession) -> str | None:
        """
        Получает сохраненный язык пользователя из базы данных
        
        Args:
            user_id: ID пользователя
            session: Сессия базы данных
        
        Returns:
            Сохраненный язык пользователя или None
        """
        from src.adapters.db.user_repository import UserRepository
        return await UserRepository.get_user_language(user_id, session)
