from sqlalchemy import ForeignKey, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from app.db.base import Base


class UserTrialUsage(Base):
    __tablename__ = "user_trial_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    trial_sub_id: Mapped[int] = mapped_column(ForeignKey("subs.id"), nullable=False, index=True)

    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))   # если конвертировался в платный
    expired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))     # если истёк без конверсии

    user = relationship("User", back_populates="user_trial_usage")
    trial_plan = relationship("Subs", back_populates="user_trial_usage")