from dataclasses import dataclass

from app.db.models.user_ai_context import MessageType


@dataclass
class MessageDTO:
    text: str
    author_id: int
    message_type: MessageType

@dataclass
class Result:
    result: str


@dataclass
class ModelConfig:
    id: int
    name: str
    api_name: str
    ai_class: str
    api_provider: str
    api_link: str


@dataclass
class ModelInfo:
    model_class_id: int
    name: str
    description: str