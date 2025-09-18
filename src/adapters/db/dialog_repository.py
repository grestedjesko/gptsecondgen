from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from app.db.models import Dialog

class DialogRepository:
    @staticmethod
    async def get_last(user_id: int, session: AsyncSession):
        stmt = (sa.select(Dialog).where(Dialog.user_id == user_id, Dialog.is_active == True)
                .order_by(Dialog.created_at).limit(1))
        result = await session.execute(stmt)
        dialog = result.scalar_one_or_none()
        return dialog

    @staticmethod
    async def create(user_id: int, name: str, session: AsyncSession):
        dialog = Dialog(user_id=user_id, name=name)
        session.add(dialog)
        await session.flush()
        await session.commit()
        return dialog

    @staticmethod
    async def end(dialog_id: int, user_id: int, session: AsyncSession):
        stmt = sa.update(Dialog).values(is_active=False).where(Dialog.user_id == user_id,
                                                               Dialog.id == dialog_id)
        await session.execute(stmt)
