from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy import func
from app.db.models import Payment
from app.db.models.payments import PaymentProvider, PaymentStatus
from datetime import datetime


class PaymentRepository:
    @staticmethod
    async def create(invoice_id: int,
                     provider_payment_id: str,
                     amount: int,
                     provider: PaymentProvider,
                     session: AsyncSession,
                     status: PaymentStatus = PaymentStatus.PENDING,
                     completed_at: datetime = None,
                     currency: str = 'RUB'):

        payment = Payment(invoice_id=invoice_id,
                          provider=provider,
                          provider_payment_id=provider_payment_id,
                          amount=amount,
                          status=status,
                          currency=currency,
                          completed_at=completed_at)
        session.add(payment)
        await session.flush()
        await session.commit()
        return payment.id


    @staticmethod
    async def update_payment_message_id(payment_id: int, payment_message_id: int, session: AsyncSession):
        await session.execute(sa.update(Payment)
                              .where(Payment.id == payment_id)
                              .values(payment_message_id=payment_message_id))
        await session.commit()

    @staticmethod
    async def set_payment_completed(payment_id: int, session: AsyncSession):
        await session.execute(sa.update(Payment)
                              .where(Payment.id == payment_id)
                              .values(status='completed',
                                      completed_at=datetime.now()))
        await session.commit()

    @staticmethod
    async def get(provider_payment_id: str, session: AsyncSession):
        result = await session.execute(sa.select(Payment).where(Payment.provider_payment_id == provider_payment_id))
        payment = result.scalar_one_or_none()
        return payment

    @staticmethod
    async def count_payments_retries(invoice_id: int, session: AsyncSession):
        query = sa.select(func.count()).filter(Payment.invoice_id == invoice_id, Payment.status == PaymentStatus.CANCELED)
        result = await session.execute(query)
        count = result.scalar()
        return count

    @staticmethod
    async def get_payment_provider(anchor_payment_id: int, session: AsyncSession):
        result = await session.execute(sa.select(Payment.provider).where(Payment.id == anchor_payment_id))
        anchor_payment_provider = result.scalar_one_or_none()
        return anchor_payment_provider