import sqlalchemy as sa
from sqlalchemy import String, ForeignKey, func, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from datetime import datetime
import enum


class Dialog(Base):
    __tablename__ = "dialogs"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    name = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    user = relationship("User", back_populates="dialogs")
    message = relationship("AiContext", back_populates="dialog")