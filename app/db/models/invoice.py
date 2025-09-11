from sqlalchemy import (
    String, func, Integer, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.base import Base
import enum
from sqlalchemy import Enum as SAEnum
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from uuid6 import uuid7

class InvoiceStatus(enum.Enum):
    CREATED  = "created"     # выставлен, ждём оплату
    PAID     = "paid"        # закрыт оплатой
    FAILED   = "failed"      # попытки исчерпаны / хардфейл
    EXPIRED  = "expired"     # истёк срок без оплаты/события
    CANCELED = "canceled"    # отменили явно

class InvoiceReason(enum.Enum):
    INITIAL = "initial"
    RENEWAL = "renewal"

class Invoice(Base):
    """
    ЕДИНЫЙ счёт за конкретный период подписки.
    Его public_id прокидываем в Stars и/или эквайринг.
    """
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                 unique=True,
                                                 nullable=False,
                                                 default=uuid7)

    user_id = mapped_column(ForeignKey("users.user_id"), nullable=False)
    subs_id = mapped_column(ForeignKey("subs.id"),  nullable=False)

    user_subs_id = mapped_column(ForeignKey("user_subs.id"), nullable=True)
    cycle_index = mapped_column(Integer, nullable=True)

    reason: Mapped[InvoiceReason] = mapped_column(SAEnum(InvoiceReason, name='invoice_reason'),
                                                  default=InvoiceReason.INITIAL, nullable=False)

    status: Mapped[InvoiceStatus] = mapped_column(SAEnum(InvoiceStatus, name="invoice_status"),
                                                  default=InvoiceStatus.CREATED, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="invoices")
    subs = relationship("Subs", back_populates="invoices")
    user_subs = relationship("UserSubs", back_populates="invoices", foreign_keys=[user_subs_id])
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")