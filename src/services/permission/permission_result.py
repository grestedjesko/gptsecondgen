from enum import Enum

class VoicePermissionStatus(Enum):
    ALLOWED = "allowed"
    NOT_ALLOWED_BY_TIER = "not_allowed_by_tier"
    TOO_LONG = "too_long"


class VoicePermissionResult:
    def __init__(
        self,
        status: VoicePermissionStatus,
        limit_seconds: int | None = None
    ):
        self.status = status
        self.limit_seconds = limit_seconds


class PhotoPermissionStatus(Enum):
    ALLOWED = "allowed"
    NOT_ALLOWED_BY_TIER = "not_allowed_by_tier"
    DAILY_LIMIT_EXCEEDED = "daily_limit_exceeded"