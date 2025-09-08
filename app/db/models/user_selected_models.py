from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class UserSelectedModels(Base):
    __tablename__ = "user_selected_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False, unique=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"), nullable=False)

    user = relationship("User", back_populates="selected_model")
    model = relationship("AiModels", back_populates="selected_by_users")
