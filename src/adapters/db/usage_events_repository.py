from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from datetime import datetime
from app.db.models import UsageEvent


class UsageEventsRepository:
    @staticmethod
    async def add_event(session: AsyncSession,
                        request_id: int,
                        user_id: int,
                        source: str,
                        amount: int,
                        subs_id: int | None = None,
                        user_packet_id: int | None = None,
                        created_at: datetime | None = None):
        created_at = created_at or datetime.utcnow()
        event = UsageEvent(
            request_id=request_id,
            user_id=user_id,
            source=source,
            amount=amount,
            subs_id=subs_id,
            user_packet_id=user_packet_id,
            created_at=created_at,
        )
        session.add(event)
        # caller commits


