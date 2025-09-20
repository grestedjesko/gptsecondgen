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
from config.i18n import get_text
from datetime import timedelta
from aiogram.types import User

class ProfileUseCase:
    def __init__(self, redis: RedisCache, config: Settings, keyboard: Keyboard):
        self.redis = redis
        self.config = config
        self.keyboard = keyboard

    async def run(self, user_id: int, session: AsyncSession, user: User):
        user_subs = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)
        if user_subs:
            subtype_id = user_subs.type
        else:
            subtype_id = 0


        limits_by_class = await SubtypeLimitsRepository.get_all_limits_for_subtype(
            subtype_id=subtype_id,
            session=session,
            redis=self.redis
        )

        if subtype_id == 0:
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

        limit_text = await self.build_limit_text(profile_limits=result, user=user)


        if subtype_id == 0:
            generation_renew_date = await get_new_week_start_date()
            text = get_text("profile_text_no_subs", user, limit_text=limit_text, generation_renew_date=generation_renew_date)
        else:
            generation_renew_date = datetime.today().date() + timedelta(days=1)
            generation_renew_date = datetime.strftime(generation_renew_date, "%d.%m.%Y 00:00")
            renewal_status = 'Активировано' if user_subs.will_renew else 'Не активировано ❌'
            period_end = datetime.strftime(user_subs.period_end, '%d.%m.%Y %H:%M')
            text = get_text("profile_text_subs", user, limit_text=limit_text, generation_renew_date=generation_renew_date, period_end=period_end, renewal_status=renewal_status)

        trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)
        kbd = self.keyboard.profile_menu(has_subs=bool(subtype_id), trial_used=trial_used, user=user)
        return text, kbd


    async def build_limit_text(self, profile_limits, user: User) -> str:
        light_remaining = profile_limits.get(self.config.light_class_id, {}).get("remaining_questions", 0)
        normal_remaining = profile_limits.get(self.config.normal_class_id, {}).get("remaining_questions", 0)
        smart_remaining = profile_limits.get(self.config.smart_class_id, {}).get("remaining_questions", 0)
        dalle_remaining = profile_limits.get(self.config.dalle_class_id, {}).get("remaining_questions", 0)
        mj_remaining = profile_limits.get(self.config.midjourney_class_id, {}).get("remaining_questions", 0)

        # Формируем текст
        return get_text("default_limit_text", user, 
            light_remaining=light_remaining,
            normal_remaining=normal_remaining,
            smart_remaining=smart_remaining,
            dalle_remaining=dalle_remaining,
            mj_remaining=mj_remaining
        )
