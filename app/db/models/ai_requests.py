from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class AiRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True, nullable=False)
    model_id: Mapped[int] = mapped_column(ForeignKey("ai_models.id"), index=True, nullable=False)
    dialog_id: Mapped[int | None] = mapped_column(ForeignKey("dialogs.id"), index=True, nullable=True)

    # text, image, video, music (дублируем тип запроса для удобства аналитики)
    request_type: Mapped[str] = mapped_column(String(32), nullable=False)

    # провайдер/имя модели на момент запроса (денормализация для аудита)
    model_api_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_api_provider: Mapped[str] = mapped_column(String(255), nullable=False)

    # сырые полезные данные запроса/ответа (универсально для текста/медиа)
    request_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    response_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # учетные метрики (опционально)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # сколько генераций стоил запрос (с учетом AiModels.generation_cost)
    generations_cost: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")  # success|error|canceled
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_request_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="requests")
    model = relationship("AiModels", back_populates="requests")
    dialog = relationship("Dialog")
    usage_events = relationship("UsageEvent", back_populates="request")


