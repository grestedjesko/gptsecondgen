from typing import Optional

from src.adapters.cache.redis_cache import RedisCache
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI, AsyncOpenAI
from src.adapters.db.model_repository import ModelRepository
from src.adapters.db.user_model_repository import UserModelRepository
from src.services.permission.permission_service import PermissionService
from src.adapters.ai_providers.registry import ProviderRegistry
from enum import Enum

class ModelAccessStatus(Enum):
    OK = "ok"
    NO_MODEL_SELECTED = "no_model_selected"
    LIMIT_EXCEEDED = "limit_exceeded"
    PREDICTED = "predicted"


class ModelAccessResult:
    def __init__(self,
                 status: ModelAccessStatus,
                 model_id: int | None = None,):
        self.status = status
        self.model_id = model_id


class ModelSelectionService:
    def __init__(self,
                 config,
                 ai_providers: ProviderRegistry,
                 redis: RedisCache,
                 permission_service: PermissionService):
        self.redis = redis
        self.permission_service = permission_service
        self.ai_providers = ai_providers

        self.auto_model = config.auto_model
        self.auto_model_token = config.auto_model_token
        self.auto_model_provider = config.auto_model_provider


    async def get_model(self, user_id: int, user_subtype: int, messages: Optional[list[dict]], session: AsyncSession):

        allowed_classes = await ModelRepository.get_allowed_classes(subtype_id=user_subtype,
                                                                    session=session,
                                                                    redis=self.redis)

        allowed_model_ids = await ModelRepository.get_allowed_models(allowed_classes=allowed_classes, session=session)
        model_id = await UserModelRepository.get_selected_model_id(user_id=user_id, session=session)

        if model_id == 1:
            if len(allowed_model_ids) == 1:
                model_id =  allowed_model_ids[0]
            else:
                model_id = await self.select_model_based_on_prompt(messages, allowed_model_ids)

        if not model_id:
            return ModelAccessResult(status=ModelAccessStatus.NO_MODEL_SELECTED)

        if model_id in allowed_model_ids:
            return ModelAccessResult(status=ModelAccessStatus.OK, model_id=model_id)

        if allowed_model_ids:
            allowed_model_ids.sort(reverse=True)
            return ModelAccessResult(status=ModelAccessStatus.OK, model_id=allowed_model_ids[0])

        return ModelAccessResult(status=ModelAccessStatus.LIMIT_EXCEEDED)


    async def select_model_based_on_prompt(self, messages: Optional[list[dict]], allowed_model_ids: list[int]):
        client = AsyncOpenAI(api_key=self.auto_model_token, base_url=self.auto_model_provider)

        available_models = {
            2: "повседневные задачи, простая математика",
            3: "кодинг",
            4: "сложный кодинг",
            5: "интернет-поиск, доклады",
            6: "научные исследования, поэтапные, много источников",
            8: "сложная математика, генерация фото"
        }

        available_model_descriptions = {key: value for key, value in available_models.items() if
                                        key in allowed_model_ids}
        prompt_description = "\n".join([f"- {value}: {key}" for key, value in available_model_descriptions.items()])
        full_prompt = f"Ты — классификатор. Выбери айди модели, более подходящей под тип запроса пользователя. Отвечай одной цифрой согласно инструкции:\n{prompt_description}"

        full_messages = [{"role": "system", "content": full_prompt}] + list(messages)
        print(full_prompt)
        response = await client.chat.completions.create(
            model=self.auto_model,
            messages=full_messages,
            timeout=30
        )

        model_classification = response.choices[0].message.content

        if "2" in model_classification:
            return 2
        elif "3" in model_classification:
            return 3
        elif "4" in model_classification:
            return 4
        elif "5" in model_classification:
            return 5
        elif "6" in model_classification:
            return 6
        elif "8" in model_classification:
            return 8

        return 1