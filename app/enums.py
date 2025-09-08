import enum



class YookassaPaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    WAITING_FOR_CAPTURE = "waiting_for_capture"
    CANCELED = "canceled"