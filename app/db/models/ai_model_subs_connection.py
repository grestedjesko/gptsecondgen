from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class AiModelSubsConnection(Base):
    __tablename__ = "ai_model_subs_connection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subs_id: Mapped[int] = mapped_column(ForeignKey("subs.id"), nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"), nullable=False, index=True)

    subs = relationship("Subs", back_populates="models")
    model = relationship("AiModels")