import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import UserPackets


class UserPacketsRepository:
    @staticmethod
    async def get_packet(packet_type: int, user_id: int, session: AsyncSession):
        query = sa.select(UserPackets).where(UserPackets.user_id == user_id, UserPackets.type == packet_type)
        result = await session.execute(query)
        return result.scalar_one_or_none()