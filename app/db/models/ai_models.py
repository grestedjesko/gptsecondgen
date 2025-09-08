from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class AiModels(Base):
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    api_name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_provider: Mapped[int] = mapped_column(String(255), nullable=False)
    model_class_id: Mapped[int] = mapped_column(ForeignKey("ai_models_class.id"), nullable=False)
    api_link: Mapped[str] = mapped_column(String(255), nullable=False)

    model_class = relationship("AiModelsClass", back_populates="models")
    selected_by_users = relationship("UserSelectedModels", back_populates="model")


