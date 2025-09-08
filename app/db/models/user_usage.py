from app.db.base import Base
from sqlalchemy import Integer, Date, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import date


class UserDailyUsage(Base):
    __tablename__ = "user_daily_usage"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    model_class: Mapped[int] = mapped_column(ForeignKey("ai_models_class.id"), primary_key=True)
    message_usage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_usage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = relationship("User")
    model_classes = relationship("AiModelsClass")


class UserWeeklyUsage(Base):
    __tablename__ = "user_weekly_usage"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    week_start: Mapped[date] = mapped_column(Date, primary_key=True)  # дата понедельника
    model_class: Mapped[int] = mapped_column(ForeignKey("ai_models_class.id"), primary_key=True)
    message_usage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_usage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = relationship("User")
    model_classes = relationship("AiModelsClass")
