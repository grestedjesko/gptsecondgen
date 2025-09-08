import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from app.db.models import SubTypeLimits
import json

CACHE_TTL = 3600

class SubtypeLimitsRepository:
    @staticmethod
    async def get_all_limits_for_subtype(subtype_id: int, session: AsyncSession, redis: RedisCache) -> dict[int, dict]:
        cache_key = f"limits:{subtype_id}:all"
        cached = await redis.get(cache_key)
        if cached:
            print('return cached')
            return json.loads(cached)

        query = (
            sa.select(
                SubTypeLimits.ai_models_class,
                SubTypeLimits.daily_token_limit,
                SubTypeLimits.daily_question_limit
            )
            .where(SubTypeLimits.subtype_id == subtype_id)
        )

        result = await session.execute(query)
        rows = result.all()

        if not rows:
            return {}

        limits = {
            str(row.ai_models_class): {
                "token_limit": str(row.daily_token_limit),
                "question_limit": str(row.daily_question_limit)
            }
            for row in rows
        }

        await redis.set(cache_key, json.dumps(limits), ttl=CACHE_TTL)
        return limits

    @staticmethod
    async def get_limits(subtype_id: int, model_class_id: int, session: AsyncSession, redis: RedisCache) -> dict | None:
        all_limits = await SubtypeLimitsRepository.get_all_limits_for_subtype(
            subtype_id=subtype_id,
            session=session,
            redis=redis
        )
        return all_limits.get(str(model_class_id))