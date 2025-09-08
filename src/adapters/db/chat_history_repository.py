from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AiContext
from src.services.ai.data_classes import MessageDTO
import sqlalchemy as sa


class ChatHistoryRepository:
    @staticmethod
    async def save_message(session: AsyncSession, user_id: int, author_id: int, text: str, message_type: str):
        await session.execute(
            sa.insert(AiContext).values(
                user_id=user_id,
                author_id=author_id,
                text=text,
                message_type=message_type
            )
        )
        await session.commit()

    @staticmethod
    async def load_history(session: AsyncSession, user_id: int, limit: int = 10) -> list[MessageDTO]:
        query = (
            sa.select(AiContext.text, AiContext.author_id, AiContext.message_type)
            .where(AiContext.user_id == user_id, AiContext.is_deleted == False)
            .order_by(AiContext.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        return result.all()  # Вернем raw-список

    @staticmethod
    async def clear_history(session: AsyncSession, user_id: int) -> None:
        await session.execute(
            sa.update(AiContext).values(is_deleted=True).where(AiContext.user_id == user_id))
        await session.commit()
