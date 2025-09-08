from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy.inspection import inspect
from app.db.models import Subs
import json
from src.adapters.cache.redis_cache import RedisCache
from src.services.utils import json_serializer

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
    async def get_subs_type(subs_id: int, session: AsyncSession):
        stmt = sa.select(Subs.subtype_id).where(Subs.id == subs_id)
        result = await session.execute(stmt)
        subs_type = result.fetchone()
        return subs_type