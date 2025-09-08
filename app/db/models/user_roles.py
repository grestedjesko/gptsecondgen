from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserRoles(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("ai_roles.id"), nullable=False)

    user = relationship("User", back_populates="current_role")
    role = relationship("AiRoles", back_populates="user_roles")
