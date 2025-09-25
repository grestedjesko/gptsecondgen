from sqlalchemy import Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class UsageSource:
    SUBSCRIPTION = "subscription"
    PACKET = "packet"
    FREE = "free"


class UsageEvent(Base):
    __tablename__ = "usage_events"
    __table_args__ = (
        Index("ix_usage_events_user_created", "user_id", "created_at"),
        Index("ix_usage_events_user_source_created", "user_id", "source", "created_at"),
        Index("ix_usage_events_subs_created", "subs_id", "created_at"),
        Index("ix_usage_events_user_packet_created", "user_packet_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("ai_requests.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)

    source: Mapped[str] = mapped_column(String(32), nullable=False)  # subscription|packet|free
    amount: Mapped[int] = mapped_column(Integer, nullable=False)      # списанные "генерации"

    # Денормализация для связки с источником (nullable: зависит от source)
    subs_id: Mapped[int | None] = mapped_column(ForeignKey("subs.id"), nullable=True)
    user_packet_id: Mapped[int | None] = mapped_column(ForeignKey("user_packets.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    request = relationship("AiRequest", back_populates="usage_events")
    user = relationship("User")
    subs = relationship("Subs")
    user_packet = relationship("UserPackets")


