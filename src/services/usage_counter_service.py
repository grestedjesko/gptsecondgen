from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.usage_events_repository import UsageEventsRepository
from app.db.models import UserPackets, AiModels


def start_of_week(dt: datetime) -> datetime:
    # Monday as start of week
    return (dt - timedelta(days=dt.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)


class UsageCounterService:
    def __init__(self, redis: RedisCache, free_weekly_limit: int):
        self.redis = redis
        self.free_weekly_limit = free_weekly_limit

    @staticmethod
    def _daily_key(user_id: int, today: datetime) -> str:
        return f"usage:sub:daily:{user_id}:{today.strftime('%Y%m%d')}"

    @staticmethod
    def _weekly_key(user_id: int, week: datetime) -> str:
        year_week = week.strftime('%G%V')  # ISO year+week
        return f"usage:free:weekly:{user_id}:{year_week}"

    async def try_consume_subscription(self,
                                       session: AsyncSession,
                                       request_id: int,
                                       user_id: int,
                                       subs_id: int,
                                       model: AiModels,
                                       subs_daily_limit: int) -> bool:
        today = datetime.utcnow()
        key = self._daily_key(user_id, today)
        cost = model.generation_cost

        new_val = await self.redis.incr_if_enough(key, subs_daily_limit, cost)
        if new_val == -1:
            return False

        await UsageEventsRepository.add_event(session=session,
                                              request_id=request_id,
                                              user_id=user_id,
                                              source='subscription',
                                              amount=cost,
                                              subs_id=subs_id)
        return True

    async def try_consume_packet(self,
                                 session: AsyncSession,
                                 request_id: int,
                                 user_id: int,
                                 user_packet_id: int,
                                 model: AiModels) -> bool:
        cost = model.generation_cost

        # lock the packet row
        result = await session.execute(sa.select(UserPackets).where(UserPackets.id == user_packet_id).with_for_update())
        user_packet = result.scalar_one_or_none()
        if user_packet is None or user_packet.remaining_generations < cost:
            return False

        user_packet.remaining_generations -= cost
        await UsageEventsRepository.add_event(session=session,
                                              request_id=request_id,
                                              user_id=user_id,
                                              source='packet',
                                              amount=cost,
                                              user_packet_id=user_packet_id)
        return True

    async def try_consume_free(self,
                               session: AsyncSession,
                               request_id: int,
                               user_id: int,
                               model: AiModels) -> bool:
        week = start_of_week(datetime.utcnow())
        key = self._weekly_key(user_id, week)
        cost = model.generation_cost

        new_val = await self.redis.incr_if_enough(key, self.free_weekly_limit, cost)
        if new_val == -1:
            return False

        await UsageEventsRepository.add_event(session=session,
                                              request_id=request_id,
                                              user_id=user_id,
                                              source='free',
                                              amount=cost)
        return True

    # ---------- Read-only helpers ----------
    async def get_subscription_used_today(self, user_id: int) -> int:
        today = datetime.utcnow()
        key = self._daily_key(user_id, today)
        val = await self.redis.get(key)
        try:
            return int(val) if val is not None else 0
        except ValueError:
            return 0

    async def get_free_used_this_week(self, user_id: int) -> int:
        week = start_of_week(datetime.utcnow())
        key = self._weekly_key(user_id, week)
        val = await self.redis.get(key)
        try:
            return int(val) if val is not None else 0
        except ValueError:
            return 0

    async def get_packets_remaining_total(self, session: AsyncSession, user_id: int) -> int:
        result = await session.execute(sa.select(sa.func.coalesce(sa.func.sum(UserPackets.remaining_generations), 0))
                                       .where(UserPackets.user_id == user_id))
        return int(result.scalar_one())


