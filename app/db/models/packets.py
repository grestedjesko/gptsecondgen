from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship, Mapped
from app.db.base import Base


class PacketType(Base):
    __tablename__ = "packet_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=False)

    packets = relationship("Packet", back_populates="type")


class Packet(Base):
    __tablename__ = "packets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(ForeignKey("packet_types.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)

    price: Mapped[int] = mapped_column(Integer, nullable=False)
    stars_price: Mapped[int] = mapped_column(Integer, nullable=False)

    generation_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=False)

    type = relationship("PacketType", back_populates="packets")
    models = relationship("AiModelPacketConnection", back_populates="packet")
    user_packets = relationship("UserPackets", back_populates="packet")
    # requests using this packet are indirectly linked via UsageEvent.user_packet_id