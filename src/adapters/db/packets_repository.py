import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.packets import PacketType


class PacketsRepository:
    @staticmethod
    async def get_all_packet_types(session: AsyncSession):
        result = await session.execute(sa.select(PacketType).where(PacketType.is_visible == True))
        return result.scalars().all()