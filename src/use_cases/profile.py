from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.db.usage_repository import UsageRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
from src.adapters.db.subtype_repository import SubtypeLimitsRepository
from app.config import Settings
from bot.keyboards.keyboards import Keyboard
from src.services.utils import get_week_start_date, get_new_week_start_date
from datetime import datetime
from src.adapters.cache.redis_cache import RedisCache
from collections import defaultdict
from config.texts import (default_limit_text,
                          profile_text_no_subs,
                          profile_text_subs)

class ProfileUseCase:
    def __init__(self, redis: RedisCache, config: Settings, keyboard: Keyboard):
        self.redis = redis
        self.config = config
        self.keyboard = keyboard

    async def run(self, user_id: int, session: AsyncSession):
        subs_info = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)
        limits_by_class = await SubtypeLimitsRepository.get_all_limits_for_subtype(
            subtype_id=subs_info.subtype_id,
            session=session,
            redis=self.redis
        )

        if subs_info.subtype_id == 0:
            week_start = await get_week_start_date()
            usage_rows = await UsageRepository.get_all_week_usage(
                user_id=user_id,
                week_start=week_start,
                session=session
            )
        else:
            usage_rows = await UsageRepository.get_all_usage(
                user_id=user_id,
                day=datetime.today().date(),
                session=session
            )

        # { model_class_id: used_count }
        usage_by_class = defaultdict(int)
        for model_class_id, used_count in usage_rows:
            usage_by_class[model_class_id] = used_count or 0

        result = {}
        for model_class_id, limit_data in limits_by_class.items():
            used = usage_by_class.get(model_class_id, 0)
            questions_limit = int(limit_data["question_limit"])
            remaining_questions = max(questions_limit - used, 0)

            model_class_id = int(model_class_id)
            result[model_class_id] = {
                "limit_questions": questions_limit,
                "remaining_questions": remaining_questions,
            }

        limit_text = await self.build_limit_text(profile_limits=result)

        generation_renew_date = await get_new_week_start_date()

        if subs_info.subtype_id == 0:
            text = profile_text_no_subs % (limit_text, generation_renew_date)
        else:
            renewal_status = 'Активировано' if subs_info.auto_renewal else 'Не активировано ❌'
            text = profile_text_subs % (limit_text, subs_info.end_date, renewal_status)

        trial_used = subs_info.trial
        kbd = self.keyboard.profile_menu(has_subs=bool(subs_info.subtype_id), trial_used=trial_used)
        return text, kbd


    async def build_limit_text(self, profile_limits) -> str:
        light_remaining = profile_limits.get(self.config.light_class_id, {}).get("remaining_questions", 0)
        normal_remaining = profile_limits.get(self.config.normal_class_id, {}).get("remaining_questions", 0)
        smart_remaining = profile_limits.get(self.config.smart_class_id, {}).get("remaining_questions", 0)
        dalle_remaining = profile_limits.get(self.config.dalle_class_id, {}).get("remaining_questions", 0)
        mj_remaining = profile_limits.get(self.config.midjourney_class_id, {}).get("remaining_questions", 0)

        # Формируем текст
        return default_limit_text % (
            light_remaining,
            normal_remaining,
            smart_remaining,
            dalle_remaining,
            mj_remaining
        )
