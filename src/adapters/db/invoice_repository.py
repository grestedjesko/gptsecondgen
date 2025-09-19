import uuid6
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from app.db.models import Invoice
from app.db.models.invoice import InvoiceReason, InvoiceStatus


class InvoiceRepository:
    @staticmethod
    async def create(user_id: int,
                     subs_id: int,
                     session: AsyncSession,
                     reason: InvoiceReason = InvoiceReason.INITIAL,
                     status: InvoiceStatus = InvoiceStatus.CREATED,
                     user_subs_id: int = None,
                     cycle_index: int = 0,
                     message_id: int = None,):

        uuid = str(uuid6.uuid7())
        invoice = Invoice(public_id=uuid,
                          user_id=user_id,
                          subs_id=subs_id,
                          reason=reason,
                          status=status,
                          user_subs_id=user_subs_id,
                          cycle_index=cycle_index,
                          message_id=message_id)
        session.add(invoice)
        await session.flush()
        await session.commit()
        return invoice

    @staticmethod
    async def get(invoice_id: int, session: AsyncSession):
        result = await session.execute(sa.select(Invoice).where(Invoice.id == invoice_id))
        invoice = result.scalar_one_or_none()
        return invoice


    @staticmethod
    async def get_by_public_id(public_id: str, session: AsyncSession):
        result = await session.execute(sa.select(Invoice).where(Invoice.public_id == public_id))
        invoice = result.scalar_one_or_none()
        return invoice


    @staticmethod
    async def get_last_invoice(user_subs_id: int, session: AsyncSession):
        stmt = sa.select(Invoice).where(Invoice.user_subs_id == user_subs_id).order_by(Invoice.created_at.desc())
        result = await session.execute(stmt)
        last_subs_invoice = result.scalars().first()
        return last_subs_invoice
