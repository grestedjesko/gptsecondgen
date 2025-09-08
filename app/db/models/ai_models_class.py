from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class AiModelsClass(Base):
    __tablename__ = "ai_models_class"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    models = relationship("AiModels", back_populates="model_class")
    subs_type = relationship("SubTypeLimits", back_populates="models_class")
    daily_usage = relationship("UserDailyUsage", back_populates="model_classes")
    weekly_usage = relationship("UserWeeklyUsage", back_populates="model_classes")
