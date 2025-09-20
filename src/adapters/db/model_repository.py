import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AiModels, SubTypeLimits
from src.adapters.cache.redis_cache import RedisCache
from src.services.ai.data_classes import ModelConfig, ModelInfo
from config.i18n import get_localized_model_name
from aiogram.types import User

import json
from typing import Optional

CACHE_TTL = 1


class ModelRepository:
    @staticmethod
    async def get_all_models(session: AsyncSession, redis: RedisCache) -> list[tuple[int, str, int]]:
        """
        Возвращает список всех моделей с полями: (id, name, model_class_id)
        """
        cache_key = "models:all"
        cached = await redis.get(cache_key)
        if cached:
            pass
            #return json.loads(cached)

        query = sa.select(AiModels.id, AiModels.name, AiModels.model_class_id).order_by(AiModels.id)
        result = await session.execute(query)
        models = result.fetchall()

        models_list = [tuple(row) for row in models]

        await redis.set(cache_key, json.dumps(models_list), ttl=CACHE_TTL)
        return models_list

    @staticmethod
    async def get_all_models_localized(session: AsyncSession, redis: RedisCache, user: User) -> list[tuple[int, str, int]]:
        """
        Возвращает список всех моделей с локализованными названиями: (id, localized_name, model_class_id)
        """
        # Получаем оригинальные модели
        models = await ModelRepository.get_all_models(session, redis)
        
        # Локализуем названия
        localized_models = []
        for model_id, original_name, model_class_id in models:
            localized_name = get_localized_model_name(original_name, user)
            localized_models.append((model_id, localized_name, model_class_id))
        
        return localized_models


    @staticmethod
    async def get_all_models_id(session: AsyncSession, redis: RedisCache) -> list[tuple[int, str]]:
        """
        Возвращает список моделей с полями: (id, name)
        """
        cache_key = "models:names"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        query = sa.select(AiModels.id)
        result = await session.execute(query)
        ids = result.fetchall()

        await redis.set(cache_key, json.dumps(ids), ttl=CACHE_TTL)
        return ids


    @staticmethod
    async def get_model_name_by_id(model_id: int, session: AsyncSession, redis: RedisCache) -> str | None:
        """
        Возвращает имя модели по её ID. Использует кэш.
        """
        cache_key = f"model:name:{model_id}"
        cached = await redis.get(cache_key)
        if cached:
            return cached  # имя — это просто строка

        query = sa.select(AiModels.name).where(AiModels.id == model_id)
        result = await session.execute(query)
        name_row = result.scalar_one_or_none()

        if name_row:
            await redis.set(cache_key, name_row, ttl=CACHE_TTL)

        return name_row


    @staticmethod
    async def get_model_info(model_id: int, session: AsyncSession, redis: RedisCache) -> ModelInfo | None:
        cache_key = f"model:{model_id}:info"

        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)  # bytes/str -> dict
            return ModelInfo(**data)

        stmt = sa.select(
            AiModels.model_class_id,
            AiModels.name,
            AiModels.description,
        ).where(AiModels.id == model_id)

        result = await session.execute(stmt)
        mapping = result.mappings().one_or_none()
        if mapping is None:
            return None

        payload = dict(mapping)  # dict -> JSON for cache
        await redis.set(cache_key, json.dumps(payload), ttl=CACHE_TTL)

        return ModelInfo(**payload)  # return dot-access object


    @staticmethod
    async def get_allowed_classes(subtype_id: int, session: AsyncSession, redis: RedisCache):
        cache_key = f"subtype:{subtype_id}:allowed_classes"
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        result = await session.execute(
            sa.select(SubTypeLimits.ai_models_class)
            .where(
                SubTypeLimits.subtype_id == subtype_id,
                SubTypeLimits.daily_token_limit > 0,
                SubTypeLimits.daily_question_limit > 0
            )
        )
        allowed = result.scalars().all()

        await redis.set(cache_key, json.dumps(allowed), ttl=CACHE_TTL)
        return allowed


    @staticmethod
    async def get_model_class_by_id(model_id: int, session: AsyncSession, redis: RedisCache) -> int | None:
        """
        Возвращает ID класса модели (model_class_id) по ID модели. Использует кэш.
        """
        cache_key = f"model:{model_id}:class_id"
        cached = await redis.get(cache_key)
        if cached:
            return int(cached)

        query = sa.select(AiModels.model_class_id).where(AiModels.id == model_id)
        result = await session.execute(query)
        class_id = result.scalar_one_or_none()

        if class_id is not None:
            await redis.set(cache_key, str(class_id), ttl=CACHE_TTL)

        return class_id


    @staticmethod
    async def get_model_config(model_id: int, session: AsyncSession) -> ModelConfig | None:
        stmt = (
            sa.select(
                AiModels.id,
                AiModels.name,
                AiModels.api_name,
                AiModels.model_class_id,
                AiModels.api_provider,
                AiModels.api_link
            )
            .where(AiModels.id == model_id)
        )
        result = await session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        return ModelConfig(
            id=row.id,
            name=row.name,
            api_name=row.api_name,
            ai_class=row.model_class_id,
            api_provider=row.api_provider,
            api_link=row.api_link
        )

    @staticmethod
    async def get_allowed_models(allowed_classes: Optional[list[int]], session: AsyncSession):
        query = sa.select(AiModels.id).where(AiModels.model_class_id.in_(allowed_classes), AiModels.id != 1)
        result = await session.execute(query)
        allowed_model_ids = [row[0] for row in result.fetchall()]
        return allowed_model_ids