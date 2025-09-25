from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from datetime import datetime


class UserPackets(Base):
    __tablename__ = "user_packets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False, index=True)
    type: Mapped[int] = mapped_column(ForeignKey('packets.id'), nullable=False, index=True)

    # remaining generations in the packet; does not auto-reset
    remaining_generations: Mapped[int] = mapped_column(Integer, nullable=False)

    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="packets")
    packet = relationship("Packet", back_populates="user_packets")


