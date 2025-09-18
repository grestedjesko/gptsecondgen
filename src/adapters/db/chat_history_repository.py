from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AiContext
from app.db.models.user_ai_context import MessageType
from src.services.ai.data_classes import MessageDTO
import sqlalchemy as sa


class ChatHistoryRepository:
    @staticmethod
    async def save_message(session: AsyncSession, dialog_id: int, author_id: int, text: str, message_type: MessageType):
        stmt = (
            sa.insert(AiContext)
            .values(
                dialog_id=dialog_id,
                author_id=author_id,
                text=text,
                message_type=message_type,
            )
            .returning(AiContext.public_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one()  # id вставленной записи


    @staticmethod
    async def load_history(session: AsyncSession, dialog_id: int, limit: int = 10) -> list[MessageDTO]:
        query = (
            sa.select(AiContext.text, AiContext.author_id, AiContext.message_type)
            .where(AiContext.dialog_id == dialog_id, AiContext.is_deleted == False)
            .order_by(AiContext.created_at)
            .limit(limit)
        )
        result = await session.execute(query)
        rows = result.all()

        return [
            MessageDTO(
                text=text,
                author_id=author_id,
                message_type=message_type,
            )
            for (text, author_id, message_type) in rows
        ]