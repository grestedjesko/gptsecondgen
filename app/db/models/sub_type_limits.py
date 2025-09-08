from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from app.db.base import Base


class SubTypeLimits(Base):
    __tablename__ = "sub_type_limits"

    id = mapped_column(Integer, primary_key=True)
    subtype_id = mapped_column(ForeignKey("sub_types.id"), nullable=False)

    ai_models_class = mapped_column(ForeignKey("ai_models_class.id"), nullable=False)
    daily_token_limit = mapped_column(Integer, nullable=False)
    daily_question_limit = mapped_column(Integer, nullable=False)

    subtype = relationship("SubType", back_populates="config")
    models_class = relationship("AiModelsClass", back_populates="subs_type")