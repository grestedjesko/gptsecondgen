from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
import sqlalchemy as sa


class UserRepository:
    @staticmethod
    async def create_user(user: types.User, session: AsyncSession):
        """Регистрация пользователя"""
        query = sa.insert(User).values(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def get_by_id(user_id: int, session: AsyncSession) -> User | None:
        result = await session.execute(
            sa.select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_language(user_id: int, session: AsyncSession) -> str | None:
        """Получает сохраненный язык пользователя"""
        result = await session.execute(
            sa.select(User.language).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def set_user_language(user_id: int, language: str, session: AsyncSession):
        """Устанавливает язык пользователя"""
        await session.execute(
            sa.update(User)
            .where(User.user_id == user_id)
            .values(language=language)
        )
        await session.commit()
