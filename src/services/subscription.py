from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.db.user_subs_repository import UserSubsRepository
from app.db.models.user_subs import SubscriptionStatus
from datetime import datetime, timedelta
from app.db.models import Subs

class SubscriptionService:
    @staticmethod
    async def give_or_extend_subscription(subs: Subs,
                                          user_id: int,
                                          session: AsyncSession,
                                          saved_payment_method: int = None,
                                          anchor_payment_id: int = None,
                                          will_renew: bool = False):
        user_subs = await UserSubsRepository.get_subs_by_status_and_type(user_id=user_id,
                                                                         type=subs.subtype_id,
                                                                         status=SubscriptionStatus.ACTIVE,
                                                                         session=session)
        if not user_subs:
            user_subs = await UserSubsRepository.get_subs_by_status_and_type(user_id=user_id,
                                                                             type=subs.subtype_id,
                                                                             status=SubscriptionStatus.PAST_DUE,
                                                                             session=session)

        if user_subs:
            if user_subs.will_renew and not will_renew:
                will_renew = True
                anchor_payment_id = anchor_payment_id
            else:
                anchor_payment_id = user_subs.anchor_payment_id

            period_start = datetime.now()
            period_end = user_subs.period_end + timedelta(days=subs.period)

            renews_at = period_end

            await UserSubsRepository.renew_subscription(user_subs_id=user_subs.id,
                                                        period_start=period_start,
                                                        period_end=period_end,
                                                        will_renew=will_renew,
                                                        renews_at=renews_at,
                                                        anchor_payment_id=anchor_payment_id,
                                                        session=session)

            if saved_payment_method:
                await UserSubsRepository.update_payment_method(payment_method_id=saved_payment_method,
                                                               user_subs_id=user_subs.id,
                                                               session=session)

        else:
            period_start = datetime.now()
            period_end = datetime.now() + timedelta(days=subs.period)
            renews_at = period_end

            await UserSubsRepository.add(user_id=user_id,
                                         subs_id=subs.id,
                                         subs_type=subs.subtype_id,
                                         status=SubscriptionStatus.ACTIVE,
                                         period_start=period_start,
                                         period_end=period_end,
                                         will_renew=will_renew,
                                         renews_at=renews_at,
                                         anchor_payment_id=anchor_payment_id,
                                         payment_method=saved_payment_method,
                                         session=session)