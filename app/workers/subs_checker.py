from app.db.models import UserSubs
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.payments import PaymentProvider, PaymentStatus
from app.db.models.user_subs import SubscriptionStatus
from app.db.models.invoice import InvoiceReason, InvoiceStatus
from datetime import datetime, timedelta
from src.adapters.payments.yookassa_api import YookassaAPI
from src.adapters.db.subs_repository import SubsRepository
from src.adapters.db.payment_repository import PaymentRepository
from src.adapters.db.user_payment_methods_repository import UserPaymentMethodsRepository
from src.adapters.db.invoice_repository import InvoiceRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
import pytz


class SubscriptionChecker:
    @staticmethod
    async def renew_subscription(user_subs: UserSubs, session: AsyncSession, yookassa_api: YookassaAPI):
        if not user_subs.will_renew:
            user_subs.status = SubscriptionStatus.CANCELED
            await session.commit()
            return

        if user_subs.status == SubscriptionStatus.ACTIVE:
            if not user_subs.payment_method:
                user_subs.status = SubscriptionStatus.EXPIRED
                await session.commit()
                return

            user_subs.status = SubscriptionStatus.PAST_DUE

            await SubscriptionChecker.process_subs_payment(user_subs=user_subs,
                                                           session=session,
                                                           yookassa_api=yookassa_api)
        await session.commit()

    @staticmethod
    async def process(session: AsyncSession, yookassa_api: YookassaAPI):
        now = datetime.now(pytz.utc)

        past_due_subs = await UserSubsRepository.get_past_due_subs(now=now, session=session)
        for subs in past_due_subs:
            anchor_payment_provider = await PaymentRepository.get_payment_provider(
                anchor_payment_id=subs.anchor_payment_id,
                session=session
            )

            if anchor_payment_provider == PaymentProvider.TELEGRAM_STARS:
                if subs.renews_at + timedelta(days=7) <= now:
                    subs.status = SubscriptionStatus.EXPIRED
            else:
                if not subs.renews_at:
                    subs.status = SubscriptionStatus.EXPIRED
                    continue

                if subs.renews_at < now:
                    await SubscriptionChecker.process_subs_payment(user_subs=subs,
                                                                   session=session,
                                                                   yookassa_api=yookassa_api)
            await session.commit()

        active_subs = await UserSubsRepository.get_active_subs(now=now, session=session)
        for subs in active_subs:
            await SubscriptionChecker.renew_subscription(user_subs=subs,
                                                         session=session,
                                                         yookassa_api=yookassa_api)



    @staticmethod
    async def process_subs_payment(user_subs: UserSubs,
                                   session: AsyncSession,
                                   yookassa_api: YookassaAPI):
        last_subs_invoice = await InvoiceRepository.get_last_invoice(user_subs_id=user_subs.id,
                                                                     session=session)

        cycle_index = last_subs_invoice.cycle_index + 1 if last_subs_invoice else 1

        invoice = await InvoiceRepository.create(user_id=user_subs.user_id,
                                                 subs_id=user_subs.subs_id,
                                                 user_subs_id=user_subs.id,
                                                 cycle_index=cycle_index,
                                                 reason=InvoiceReason.RENEWAL,
                                                 status=InvoiceStatus.CREATED,
                                                 session=session)
        invoice_id = invoice.id

        subs = await SubsRepository.get_subs_info(subs_id=user_subs.subs_id, session=session)
        amount = subs.price

        payment_method_id = await UserPaymentMethodsRepository.get_payment_method_id(
            payment_method_id=user_subs.payment_method,
            session=session
        )

        gate_payment_id = yookassa_api.create_recurrent_payment(
            amount=amount,
            payment_method_id=payment_method_id,
            return_url='https://t.me/chatgpts_rubot',
            invoice_id=invoice_id
        )

        payment = await PaymentRepository.create(invoice_id=invoice_id,
                                                 provider_payment_id=gate_payment_id,
                                                 amount=amount,
                                                 provider=PaymentProvider.GATEWAY,
                                                 session=session,
                                                 status=PaymentStatus.PENDING,
                                                 currency='RUB')

        print('создан платеж ')