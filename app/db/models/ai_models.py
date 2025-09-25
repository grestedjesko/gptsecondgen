from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from enum import Enum
from sqlalchemy import Enum as SAEnum

class AiModelsType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    MUSIC = "music"


class AiModels(Base):
    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(SAEnum(AiModelsType), nullable=False) 

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    api_name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_provider: Mapped[int] = mapped_column(String(255), nullable=False)
    api_link: Mapped[str] = mapped_column(String(255), nullable=False)
    generation_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    selected_by_users = relationship("UserSelectedModels", back_populates="model")
    requests = relationship("AiRequest", back_populates="model")


