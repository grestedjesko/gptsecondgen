import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import UserSubs, UserTrialUsage
from datetime import datetime
from src.adapters.cache.redis_cache import RedisCache
from app.db.models.user_subs import SubscriptionStatus

CACHE_TTL = 1  # 1 час

class UserSubsRepository:
    @staticmethod
    async def get_by_id(subs_id: int, session: AsyncSession) -> UserSubs:
        result = await session.execute(sa.select(UserSubs).where(UserSubs.user_id == subs_id))
        return result.scalar_one_or_none()


    @staticmethod
    async def get_subs_type(user_id: int, session: AsyncSession, redis: RedisCache) -> int:
        cache_key = f"user_subs_type:{user_id}"
        cached = await redis.get(cache_key)
        if cached is not None:
            print(cached)
            return int(cached)  # значение — int, а не JSON

        query = (sa.select(UserSubs.type)
                 .where(UserSubs.user_id == user_id)
                 .order_by(UserSubs.period_end.desc()))
        res = await session.execute(query)
        subs_type = res.one_or_none()

        value = subs_type[0] if subs_type else 0

        await redis.set(cache_key, str(value), ttl=CACHE_TTL)
        return value


    @staticmethod
    async def get_subs_by_user_id(user_id: int, session: AsyncSession):
        query = (sa.select(UserSubs)
                 .where(UserSubs.user_id == user_id,
                        UserSubs.status == SubscriptionStatus.ACTIVE,
                        UserSubs.period_end > datetime.now())
                 .order_by(UserSubs.period_end.desc()))
        res = await session.execute(query)
        subs = res.scalars().first()
        return subs


    @staticmethod
    async def get_trial_used(user_id: int, session: AsyncSession):
        stmt = sa.select(sa.exists().where(
            UserTrialUsage.user_id == user_id
        ))
        result = await session.execute(stmt)
        return result.scalar()


    @staticmethod
    async def get_subs_by_status_and_type(user_id: int, type: int, status: SubscriptionStatus,
                                              session: AsyncSession):
        stmt = sa.select(UserSubs).where(
            UserSubs.user_id == user_id,
            UserSubs.type == type,
            UserSubs.status == status,
        ).order_by(UserSubs.created_at.desc())  # Сортировка по дате в убывающем порядке
        result = await session.execute(stmt)
        result = result.scalars().first()  # Возвращаем первую запись из отсортированных
        return result


    @staticmethod
    async def add(user_id: int,
                  subs_id: int,
                  subs_type: int,
                  status: SubscriptionStatus,
                  period_start: datetime,
                  period_end: datetime,
                  will_renew: bool,
                  renews_at: datetime,
                  anchor_payment_id: int,
                  session: AsyncSession,
                  payment_method: int | None = None):
        subs = UserSubs(user_id=user_id,
                        subs_id=subs_id,
                        type=subs_type,
                        status=status,
                        period_start=period_start,
                        period_end=period_end,
                        will_renew=will_renew,
                        renews_at=renews_at,
                        anchor_payment_id=anchor_payment_id,
                        payment_method=payment_method)
        session.add(subs)

    @staticmethod
    async def renew_subscription(user_subs_id: int,
                                 will_renew: bool,
                                 anchor_payment_id: int,
                                 period_start: datetime,
                                 period_end: datetime,
                                 renews_at: datetime,
                                 session: AsyncSession):
        stmt = sa.update(UserSubs).values(status=SubscriptionStatus.ACTIVE,
                                          will_renew=will_renew,
                                          period_start=period_start,
                                          anchor_payment_id=anchor_payment_id,
                                          renews_at=renews_at,
                                          period_end=period_end,).where(UserSubs.id == user_subs_id)

        await session.execute(stmt)

    @staticmethod
    async def update_payment_method(user_subs_id: int,
                                    payment_method_id: int,
                                    session: AsyncSession):
        stmt = sa.update(UserSubs).values(payment_method=payment_method_id).where(UserSubs.id == user_subs_id)
        await session.execute(stmt)

    @staticmethod
    async def set_will_renew(user_id: int, will_renew: bool, session: AsyncSession):
        stmt = (sa.update(UserSubs)
                .values(will_renew=will_renew)
                .where(UserSubs.user_id == user_id, UserSubs.status == SubscriptionStatus.ACTIVE))
        await session.execute(stmt)

    @staticmethod
    async def get_active_subs(now: datetime, session: AsyncSession):
        stmt = sa.select(UserSubs).where(
            UserSubs.period_end <= now,
            UserSubs.status == SubscriptionStatus.ACTIVE
        )
        result = await session.execute(stmt)
        active_subs = result.scalars().all()
        return active_subs

    @staticmethod
    async def get_past_due_subs(now: datetime, session: AsyncSession):
        stmt = sa.select(UserSubs).where(
            UserSubs.period_end <= now,
            UserSubs.status.in_([SubscriptionStatus.PAST_DUE])
        )
        result = await session.execute(stmt)
        past_due_subs = result.scalars().all()
        return past_due_subs
