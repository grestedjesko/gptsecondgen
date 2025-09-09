import sqlalchemy as sa
from sqlalchemy import BigInteger, Text, ForeignKey, func,  Enum, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from datetime import datetime
import enum

class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE_URL = "image_url"
    FILE_URL = "file_url"


class AiContext(Base):
    __tablename__ = "ai_context"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_type: Mapped[str] = mapped_column(
        Enum(MessageType, name="message_type_enum"),
        nullable=False,
        default=MessageType.TEXT,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())

    user = relationship("User", back_populates="ai_context")