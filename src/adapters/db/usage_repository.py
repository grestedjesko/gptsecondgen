from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import UserDailyUsage, UserWeeklyUsage
import sqlalchemy as sa
from datetime import date
from sqlalchemy.dialects.postgresql import insert as pg_insert

class UsageRepository:
    @staticmethod
    async def get_all_usage(user_id: int, day: date, session: AsyncSession):
        usage_result = await session.execute(sa.select(UserDailyUsage.model_class,
                                                       UserDailyUsage.message_usage)
                                             .where(UserDailyUsage.user_id == user_id,
                                                    UserDailyUsage.date == day))
        current_usage = usage_result.fetchall()
        return current_usage


    @staticmethod
    async def get_all_week_usage(user_id: int, week_start: date, session: AsyncSession):
        usage_result = await session.execute(sa.select(UserWeeklyUsage.model_class,
                                                       UserWeeklyUsage.message_usage)
                                             .where(UserWeeklyUsage.user_id == user_id,
                                                    UserWeeklyUsage.week_start == week_start))
        current_usage = usage_result.fetchall()
        return current_usage


    @staticmethod
    async def get_usage(user_id: int, model_class: int, day: date, session: AsyncSession):
        usage_result = await session.execute(sa.select(UserDailyUsage.tokens_usage,
                                                       UserDailyUsage.message_usage)
                                             .where(UserDailyUsage.user_id == user_id,
                                                    UserDailyUsage.date == day,
                                                    UserDailyUsage.model_class == model_class))

        current_usage = usage_result.fetchone()
        if not current_usage:
            return 0, 0

        tokens_used, messages_used = current_usage
        return tokens_used, messages_used

    @staticmethod
    async def get_week_usage(user_id: int, model_class: int, week_start: date, session: AsyncSession):
        usage_result = await session.execute(sa.select(UserWeeklyUsage.tokens_usage,
                                                       UserWeeklyUsage.message_usage)
                                             .where(UserWeeklyUsage.user_id == user_id,
                                                    UserWeeklyUsage.week_start == week_start,
                                                    UserWeeklyUsage.model_class == model_class))

        current_usage = usage_result.fetchone()
        if not current_usage:
            return 0, 0
        tokens_used, messages_used = current_usage
        return tokens_used, messages_used

    @staticmethod
    async def add_day_usage(user_id: int,
                            model_class: int,
                            day: date,
                            session: AsyncSession,
                            messages_used: int = 0,
                            tokens_used: int = 0):
        stmt = pg_insert(UserDailyUsage).values(
            user_id=user_id,
            date=day,
            model_class=model_class,
            message_usage=messages_used,
            tokens_usage=tokens_used,
        ).on_conflict_do_update(
            index_elements=[UserDailyUsage.user_id, UserDailyUsage.date, UserDailyUsage.model_class],
            set_={
                "message_usage": UserDailyUsage.message_usage + messages_used,
                "tokens_usage": UserDailyUsage.tokens_usage + tokens_used,
            },
        )
        await session.execute(stmt)

    @staticmethod
    async def add_week_usage(user_id: int,
                             model_class: int,
                             week_start: date,
                             session: AsyncSession,
                             messages_used: int = 0,
                             tokens_used: int = 0):
        stmt = pg_insert(UserWeeklyUsage).values(
            user_id=user_id,
            week_start=week_start,
            model_class=model_class,
            message_usage=messages_used,
            tokens_usage=tokens_used,
        ).on_conflict_do_update(
            index_elements=[UserWeeklyUsage.user_id, UserWeeklyUsage.week_start, UserWeeklyUsage.model_class],
            set_={
                "message_usage": UserWeeklyUsage.message_usage + messages_used,
                "tokens_usage": UserWeeklyUsage.tokens_usage + tokens_used,
            },
        )
        await session.execute(stmt)