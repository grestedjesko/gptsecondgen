from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.usage_repository import UsageRepository
from src.adapters.db.subtype_repository import SubtypeLimitsRepository
from datetime import datetime
from config.subs import SubscriptionConfig
from src.adapters.db.model_repository import ModelRepository
from src.services.permission.permission_result import (
    VoicePermissionStatus,
    VoicePermissionResult,
    PhotoPermissionStatus
)
from src.services.utils import get_week_start_date



class PermissionService:
    def __init__(self, subs_config: SubscriptionConfig, redis: RedisCache):
        self.redis = redis
        self.subs_config = subs_config

    async def check_limits(self,
                           user_id: int,
                           sub_type: int,
                           model_id: int,
                           session: AsyncSession):
        model_class = await ModelRepository.get_model_class_by_id(model_id=model_id,
                                                                  session=session,
                                                                  redis=self.redis)
        print('subtype ', sub_type)
        if sub_type == 0:
            week_start = await get_week_start_date()
            usage = await UsageRepository.get_week_usage(user_id=user_id,
                                                         model_class=model_class,
                                                         week_start=week_start,
                                                         session=session)
            token_used, message_used = usage

        else:
            usage = await UsageRepository.get_usage(user_id=user_id,
                                                    model_class=model_class,
                                                    day=datetime.now().date(),
                                                    session=session)
            token_used, message_used = usage

        limits = await SubtypeLimitsRepository.get_limits(subtype_id=sub_type,
                                                          model_class_id=model_class,
                                                          session=session,
                                                          redis=self.redis)
        message_limit = int(limits.get('question_limit', 0))
        token_limit = int(limits.get('token_limit', 0))

        return message_used < message_limit and token_used < token_limit

    async def check_voice_availability(self,
                                       voice_duration: int,
                                       sub_type: int) -> VoicePermissionResult:
        settings = self.subs_config.get(sub_type)

        if not settings.can_send_voice:
            return VoicePermissionResult(status=VoicePermissionStatus.NOT_ALLOWED_BY_TIER)

        if voice_duration > settings.voice_limit_seconds:
            return VoicePermissionResult(
                status=VoicePermissionStatus.TOO_LONG,
                limit_seconds=settings.voice_limit_seconds
            )

        return VoicePermissionResult(status=VoicePermissionStatus.ALLOWED)

    async def check_image_send_permission(self, sub_type: int) -> PhotoPermissionStatus:
        settings = self.subs_config.get(sub_type)
        if settings.can_send_images:
            return PhotoPermissionStatus.ALLOWED
        return PhotoPermissionStatus.NOT_ALLOWED_BY_TIER

    async def check_use_roles_permission(self, sub_type: int) -> bool:
        settings = self.subs_config.get(sub_type)
        return settings.can_use_roles

    async def check_file_send_permission(self, sub_type: int) -> bool:
        settings = self.subs_config.get(sub_type)
        return settings.can_send_files

    async def check_miniapp_answers_permission(self, sub_type: int) -> bool:
        settings = self.subs_config.get(sub_type)
        return settings.can_get_miniapp_answers

    async def check_doc_answers_permission(self, sub_type: int) -> bool:
        settings = self.subs_config.get(sub_type)
        return settings.can_get_doc_answers

    async def check_image_generation_permission(self, sub_type: int) -> bool:
        settings = self.subs_config.get(sub_type)
        return settings.can_generate_images

    async def check_file_generation_permission(self, sub_type: int) -> bool:
        settings = self.subs_config.get(sub_type)
        return settings.generate_images_file
