from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy.inspection import inspect
from app.db.models import Subs
import json
from src.adapters.cache.redis_cache import RedisCache
from src.services.utils import json_serializer
from config.i18n import get_localized_subscription_name
from aiogram.types import User

CACHE_TTL = 1  # 1 час


class SubsRepository:
    @staticmethod
    async def get_subs_info(subs_id: int, session: AsyncSession):
        print('select subs info')
        stmt = sa.select(Subs).where(Subs.id == subs_id)
        result = await session.execute(stmt)
        subs = result.scalar_one_or_none()
        return subs

    @staticmethod
    async def get_all_subs(session: AsyncSession, redis: RedisCache):
        cache_key = "all_subs"
        cached = await redis.get(cache_key)
        if cached:
            print(cached)
            subs_data = json.loads(cached)
            return [Subs(**data) for data in subs_data]

        stmt = sa.select(Subs).order_by(Subs.id)
        result = await session.execute(stmt)
        subs = result.scalars().all()

        # Просто достаём колонки без лишних проверок
        subs_data = [
            {c.key: getattr(sub, c.key) for c in inspect(Subs).mapper.column_attrs}
            for sub in subs
        ]

        # сериализация через наш универсальный json_serializer
        await redis.set(cache_key, json.dumps(subs_data, default=json_serializer), ttl=CACHE_TTL)

        return subs

    @staticmethod
    async def get_all_subs_localized(session: AsyncSession, redis: RedisCache, user: User):
        """
        Возвращает все тарифы с локализованными названиями
        """
        # Получаем оригинальные тарифы
        subs = await SubsRepository.get_all_subs(session, redis)
        
        # Создаем копии с локализованными названиями
        localized_subs = []
        for sub in subs:
            # Создаем копию объекта с локализованным названием
            localized_sub = Subs(
                id=sub.id,
                name=get_localized_subscription_name(sub.name, user),
                subtype_id=sub.subtype_id,
                kind=sub.kind,
                base_sub_id=sub.base_sub_id,
                period=sub.period,
                price=sub.price,
                stars_price=sub.stars_price,
                is_visible=sub.is_visible
            )
            localized_subs.append(localized_sub)
        
        return localized_subs

    @staticmethod
    async def get_subs_type(subs_id: int, session: AsyncSession):
        stmt = sa.select(Subs.subtype_id).where(Subs.id == subs_id)
        result = await session.execute(stmt)
        subs_type = result.fetchone()
        return subs_type