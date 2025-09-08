from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery
from src.adapters.db.invoice_repository import InvoiceRepository
from src.adapters.db.payment_repository import PaymentRepository
from src.adapters.db.subs_repository import SubsRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.payments import PaymentProvider
from app.db.models.payments import PaymentStatus
from src.services.subscription import SubscriptionService
from datetime import datetime
from app.db.models.invoice import InvoiceStatus

router = Router()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, session: AsyncSession):
    sp = message.successful_payment

    invoice_public_id = sp.invoice_payload
    if not invoice_public_id:
        return

    amount = sp.total_amount
    tg_charge_id = sp.telegram_payment_charge_id
    is_recurring = sp.is_recurring
    is_first_reccuring = sp.is_first_recurring

    invoice = await InvoiceRepository.get_by_public_id(public_id=invoice_public_id, session=session)

    subs = await SubsRepository.get_subs_info(subs_id=invoice.subs_id, session=session)
    if not subs:
        raise ValueError(f"Тариф с id={invoice.subs_id} не найден")

    if amount < subs.stars_price * 0.9:
        print('error price')
        return

    payment_id = await PaymentRepository.create(invoice_id=invoice.id,
                                                provider=PaymentProvider.TELEGRAM_STARS,
                                                provider_payment_id=tg_charge_id,
                                                amount=amount,
                                                status=PaymentStatus.SUCCEEDED,
                                                currency='XTR',
                                                completed_at=datetime.now(),
                                                session=session)

    await SubscriptionService.give_or_extend_subscription(subs=subs,
                                                          user_id=invoice.user_id,
                                                          will_renew=is_recurring,
                                                          anchor_payment_id=payment_id,
                                                          session=session)
    invoice.status = InvoiceStatus.PAID
    await session.commit()