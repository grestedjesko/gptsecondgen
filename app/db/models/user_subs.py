from sqlalchemy import Integer, DateTime, Boolean, ForeignKey, Enum, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
import enum
from datetime import datetime
from typing import Optional


class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    PROCESS_RETRY = "process_retry"
    PAST_DUE = "past_due"         # не удалось списать, но окно ретраев ещё идёт
    CANCELED = "canceled"
    EXPIRED = "expired"           # естественно истекла без продления


class UserSubs(Base):
    __tablename__ = "user_subs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)

    subs_id: Mapped[int] = mapped_column(ForeignKey('subs.id'), nullable=False)
    type: Mapped[int] = mapped_column(ForeignKey('sub_types.id'), nullable=False)

    status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus, name="subscription_status"), default=SubscriptionStatus.ACTIVE)

    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    will_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    renews_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    payment_method: Mapped[int | None] = mapped_column(ForeignKey('user_payment_methods.id'), nullable=True)

    anchor_payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id", ondelete="SET NULL"), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)

    user = relationship("User", back_populates="subs")
    subs = relationship("Subs", back_populates="user_subs", foreign_keys=[subs_id])
    subtype = relationship("SubType", back_populates="user_subs")
    anchor_payment = relationship("Payment", back_populates="user_subs")
    invoices = relationship("Invoice", back_populates="user_subs")
    user_payment_methods = relationship("UserPaymentMethod", back_populates="user_subs")