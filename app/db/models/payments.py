from sqlalchemy import (
    String, DECIMAL, func, Integer, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship, mapped_column
from app.db.base import Base
import enum
from sqlalchemy import Enum as SAEnum


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class PaymentProvider(enum.Enum):
    GATEWAY = "gateway"      # ЮKassa / другой эквайринг
    TELEGRAM_STARS = "tg_stars"


class Payment(Base):
    __tablename__ = "payments"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id = mapped_column(ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)

    provider = mapped_column(SAEnum(PaymentProvider, name="payment_provider"), nullable=False)
    provider_payment_id = mapped_column(String(255), nullable=True, index=True)  # id в ЮKassa / TG charge_id

    status = mapped_column(SAEnum(PaymentStatus, name="payment_status"),
                           default=PaymentStatus.PENDING,
                           nullable=False)

    amount = mapped_column(DECIMAL(8, 2), nullable=False)
    currency = mapped_column(String(8), nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(),
                               onupdate=func.now(), nullable=False)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)

    failure_code = mapped_column(String(64), nullable=True)
    failure_reason = mapped_column(String(512), nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
    user_subs = relationship("UserSubs", back_populates="anchor_payment")
