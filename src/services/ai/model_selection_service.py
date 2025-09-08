from src.adapters.cache.redis_cache import RedisCache
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI
from src.adapters.db.model_repository import ModelRepository
from src.adapters.db.user_model_repository import UserModelRepository
from src.services.permission.permission_service import PermissionService
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
        self.id = model_id


class ModelSelectionService:
    def __init__(self, config, redis: RedisCache, permission_service: PermissionService):
        self.redis = redis
        self.permission_service = permission_service

        self.auto_model = config.auto_model
        self.auto_model_token = config.auto_model_token
        self.auto_model_provider = config.auto_model_provider
        self.auto_model_prompt = config.auto_model_prompt

    async def get_model(self, user_id: int, text: str, user_subtype: int, session: AsyncSession):
        model_id = await UserModelRepository.get_selected_model_id(user_id=user_id,
                                                                   session=session)

        if model_id == 0:
            model_id = await self.predict_model(prompt=text, session=session)

        allowed = await self.permission_service.check_limits(
            user_id=user_id,
            sub_type=user_subtype,
            model_id=model_id,
            session=session
        )
        if not allowed:
            return ModelAccessResult(status=ModelAccessStatus.LIMIT_EXCEEDED)

        return ModelAccessResult(status=ModelAccessStatus.OK, model_id=model_id)


    async def predict_model(self, prompt: str, session: AsyncSession):
            # todo convert names to model_ids
            # select available models

            client = OpenAI(api_key=self.auto_model_token,
                            base_url=self.auto_model_provider)
            response = client.chat.completions.create(
                model=self.auto_model,
                messages=[
                    {"role": "system", "content": self.auto_model_prompt},
                    {"role": "user", "content": prompt},
                ]
            )

            model = response.choices[0].message.content

            # todo: get model class by id/name
            # get limit by class
            # if not limit
            # return default model
            # else return model

            res = await ModelRepository.get_all_models_name(session=session, redis=self.redis)
            if model not in res:
                return 1
            else:
                return model