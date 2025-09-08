from sqlalchemy import String, Integer, Text, BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class AiRoles(Base):
    __tablename__ = "ai_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    free_available: Mapped[bool] = mapped_column(Boolean, default=False)

    user_roles = relationship("UserRoles", back_populates="role")