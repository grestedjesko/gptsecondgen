import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.services.ai.data_classes import ModelConfig, ModelInfo
from config.i18n import get_localized_model_name
from src.services.i18n_service import I18nService
from app.db.models.ai_models import AiModelsType, AiModels
from aiogram.types import User

import json
from typing import Optional

CACHE_TTL = 1


class ModelRepository:
    @staticmethod
    async def get_all_text_models(session: AsyncSession, redis: RedisCache) -> list[tuple[int, str, int]]:
        """
        Возвращает список всех моделей с полями: (id, name)
        """
        cache_key = "models:all"
        cached = await redis.get(cache_key)
        if cached:
            pass
            #return json.loads(cached)

        query = sa.select(AiModels.id, AiModels.name).order_by(AiModels.id).where(AiModels.type == AiModelsType.TEXT)
        result = await session.execute(query)
        models = result.fetchall()

        models_list = [tuple(row) for row in models]

        await redis.set(cache_key, json.dumps(models_list), ttl=CACHE_TTL)
        return models_list

    @staticmethod
    async def get_all_text_models_localized(session: AsyncSession, redis: RedisCache, user: User) -> list[tuple[int, str, int]]:
        """
        Возвращает список всех моделей с локализованными названиями: (id, localized_name)
        """
        # Получаем оригинальные модели
        models = await ModelRepository.get_all_text_models(session, redis)
        
        # Получаем сохраненный язык пользователя
        saved_language = await I18nService.get_user_language(user.id, session)
        
        # Локализуем названия
        localized_models = []
        for model_id, original_name in models:
            localized_name = get_localized_model_name(original_name, user, saved_language)
            localized_models.append((model_id, localized_name))
        
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
    async def get_model_info_localized(model_id: int, session: AsyncSession, redis: RedisCache, user: User) -> ModelInfo | None:
        """
        Получает информацию о модели с локализованным названием
        """
        model_info = await ModelRepository.get_model_info(model_id, session, redis)
        if not model_info:
            return None
        
        saved_language = await I18nService.get_user_language(user.id, session)
        
        localized_name = get_localized_model_name(model_info.name, user, saved_language)
        
        return ModelInfo(
            name=localized_name,
            description=model_info.description
        )
 
 


    @staticmethod
    async def get_model_config(model_id: int, session: AsyncSession) -> ModelConfig | None:
        stmt = (
            sa.select(
                AiModels.id,
                AiModels.name,
                AiModels.api_name,
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
            api_provider=row.api_provider,
            api_link=row.api_link
        )
