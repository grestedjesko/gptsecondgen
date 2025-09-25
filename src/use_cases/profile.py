from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.db.user_subs_repository import UserSubsRepository
from app.config import Settings
from bot.keyboards.keyboards import Keyboard
from datetime import datetime
from src.adapters.cache.redis_cache import RedisCache
from src.services.i18n_service import I18nService
from datetime import timedelta
from aiogram.types import User
from src.services.usage_counter_service import UsageCounterService
from sqlalchemy import select
from app.db.models import AiModelSubsConnection, AiModelPacketConnection, AiModels, UserPackets

class ProfileUseCase:
    def __init__(self, redis: RedisCache, config: Settings, keyboard: Keyboard):
        self.redis = redis
        self.config = config
        self.keyboard = keyboard

    async def run(self, user_id: int, session: AsyncSession, user: User):
        user_subs = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)
        has_sub = bool(user_subs)


        # Unified remaining counts
        counter = UsageCounterService(self.redis, self.config.free_weekly_limit)
        available_models: list[str] = []
        if has_sub:
            used = await counter.get_subscription_used_today(user_id)
            remaining = max(self.config.subs_daily_limit - used, 0)
            # models from subscription
            rows = await session.execute(
                select(AiModels.name)
                .join(AiModelSubsConnection, AiModelSubsConnection.model_id == AiModels.id)
                .where(AiModelSubsConnection.subs_id == user_subs.subs_id)
            )
            available_models = [r[0] for r in rows.fetchall()]
            limit_text = await I18nService.get_text("default_limit_text", user, session,
                light_remaining=remaining,
                normal_remaining=remaining,
                smart_remaining=remaining,
                dalle_remaining=remaining,
                mj_remaining=remaining
            )
        else:
            used = await counter.get_free_used_this_week(user_id)
            remaining = max(self.config.free_weekly_limit - used, 0)
            # models from owned packets
            rows = await session.execute(
                select(AiModels.name)
                .join(AiModelPacketConnection, AiModelPacketConnection.model_id == AiModels.id)
                .where(UserPackets.user_id == user_id, UserPackets.remaining_generations > 0)
            )
            available_models = list({r[0] for r in rows.fetchall()})
            limit_text = await I18nService.get_text("default_limit_text", user, session,
                light_remaining=remaining,
                normal_remaining=remaining,
                smart_remaining=remaining,
                dalle_remaining=remaining,
                mj_remaining=remaining
            )


        if not has_sub:
            # next week start (assume helper removed; show +7d Monday 00:00 simplified)
            today = datetime.today()
            next_monday = today + timedelta(days=(7 - today.weekday()))
            generation_renew_date = datetime.strftime(next_monday.replace(hour=0, minute=0, second=0, microsecond=0), "%d.%m.%Y %H:%M")
            text = await I18nService.get_text("profile_text_no_subs", user, session, limit_text=limit_text, generation_renew_date=generation_renew_date)
        else:
            generation_renew_date = datetime.today().date() + timedelta(days=1)
            generation_renew_date = datetime.strftime(generation_renew_date, "%d.%m.%Y 00:00")
            renewal_status = await I18nService.get_text("renewal_activated", user, session) if user_subs.will_renew else await I18nService.get_text("renewal_not_activated", user, session)
            period_end = datetime.strftime(user_subs.period_end, '%d.%m.%Y %H:%M')
            text = await I18nService.get_text("profile_text_subs", user, session, limit_text=limit_text, generation_renew_date=generation_renew_date, period_end=period_end, renewal_status=renewal_status)

        trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)
        # Extend keyboard or text later to list available_models if needed
        kbd = await self.keyboard.profile_menu(has_subs=has_sub, trial_used=trial_used, user=user, session=session)
        return text, kbd


    async def build_limit_text(self, profile_limits, user: User, session: AsyncSession) -> str:
        light_remaining = profile_limits.get(self.config.light_class_id, {}).get("remaining_questions", 0)
        normal_remaining = profile_limits.get(self.config.normal_class_id, {}).get("remaining_questions", 0)
        smart_remaining = profile_limits.get(self.config.smart_class_id, {}).get("remaining_questions", 0)
        dalle_remaining = profile_limits.get(self.config.dalle_class_id, {}).get("remaining_questions", 0)
        mj_remaining = profile_limits.get(self.config.midjourney_class_id, {}).get("remaining_questions", 0)

        # Формируем текст
        return await I18nService.get_text("default_limit_text", user, session,
            light_remaining=light_remaining,
            normal_remaining=normal_remaining,
            smart_remaining=smart_remaining,
            dalle_remaining=dalle_remaining,
            mj_remaining=mj_remaining
        )
