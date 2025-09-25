import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import UserSelectedModels, AiModels

class UserModelRepository:
    @staticmethod
    async def get_selected_model_id(user_id: int, session: AsyncSession) -> int:
        """
        Получить ID выбранной пользователем модели
        """
        query = sa.select(UserSelectedModels.model_id).where(UserSelectedModels.user_id == user_id)
        result = await session.execute(query)
        model_id = result.scalar_one_or_none()
        return model_id or 1

    @staticmethod
    async def update_selected_model(model_id: int, user_id: int, session: AsyncSession):
        result = await session.execute(
            sa.select(UserSelectedModels).where(UserSelectedModels.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.model_id = model_id
        else:
            new_entry = UserSelectedModels(user_id=user_id, model_id=model_id)
            session.add(new_entry)

        await session.commit()
