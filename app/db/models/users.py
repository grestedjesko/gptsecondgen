from sqlalchemy import BigInteger, String, func, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    utm: Mapped[str] = mapped_column(String(255), nullable=True)

    selected_model = relationship("UserSelectedModels", back_populates="user")
    current_role = relationship("UserRoles", back_populates="user")
    subs = relationship("UserSubs", back_populates="user")
    daily_usage = relationship("UserDailyUsage", back_populates="user")
    weekly_usage = relationship("UserWeeklyUsage", back_populates="user")
    user_trial_usage = relationship("UserTrialUsage", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
    user_payment_methods = relationship("UserPaymentMethod", back_populates="user")
    dialogs = relationship("Dialog", back_populates="user")