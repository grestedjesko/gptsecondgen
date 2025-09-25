from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.cache.redis_cache import RedisCache
from src.services.usage_counter_service import UsageCounterService
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
        counter = UsageCounterService(self.redis, self.subs_config.free_weekly_limit)
        if sub_type == 0:
            used = await counter.get_free_used_this_week(user_id)
            return used < self.subs_config.free_weekly_limit
        else:
            used = await counter.get_subscription_used_today(user_id)
            # subscription daily limit should come from active plan; fallback to config
            return used < self.subs_config.subs_daily_limit

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
