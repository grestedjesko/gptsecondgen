from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base


class AiModelPacketConnection(Base):
    __tablename__ = "ai_model_packet_connection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    packet_id: Mapped[int] = mapped_column(ForeignKey("packets.id"), nullable=False, index=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"), nullable=False, index=True)

    packet = relationship("Packet", back_populates="models")
    model = relationship("AiModels")


