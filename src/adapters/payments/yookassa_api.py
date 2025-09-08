import base64
import requests
import uuid
from typing import Dict, Any, Tuple
from yookassa import Payment
import enum

class YookassaCancelationReasons(enum.Enum):
    INSUFFICIENT_FUNDS = "insufficient_funds"
    INTERNAL_TIMEOUT = "internal_timeout"
    PAYMENT_METHOD_LIMIT_EXCEEDED = "payment_method_limit_exceeded"

    _3D_SECURE_FAILED = "3d_secure_failed"
    CALL_ISSUER = "call_issuer"
    CANCELED_BY_MERCHANT = "canceled_by_merchant"
    CARD_EXPIRED = "card_expired"
    COUNTRY_FORBIDDEN = "country_forbidden"
    DEAL_EXPIRED = "deal_expired"
    EXPIRED_ON_CAPTURE = "expired_on_capture"
    EXPIRED_ON_CONFIRMATION = "expired_on_confirmation"
    FRAUD_SUSPECTED = "fraud_suspected"
    GENERAL_DECLINE = "general_decline"
    IDENTIFICATION_REQUIRED = "identification_required"
    INVALID_CARD_NUMBER = "invalid_card_number"
    INVALID_CSC = "invalid_csc"
    ISSUER_UNAVAILABLE = "issuer_unavailable"
    PAYMENT_METHOD_RESTRICTED = "payment_method_restricted"
    PERMISSION_REVOKED = "permission_revoked"
    UNSUPPORTED_MOBILE_OPERATOR = "unsupported_mobile_operator"


class YookassaAPI:
    def __init__(self, shop_id: str, secret_key: str):
        self.SHOP_ID = shop_id
        self.SECRET_KEY = secret_key
        self.BASE_URL = "https://api.yookassa.ru/v3"

    def get_auth_header(self):
        print('создаем платеж')
        auth_header = base64.b64encode(f"{self.SHOP_ID}:{self.SECRET_KEY}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4()),
            "Authorization": f"Basic {auth_header}"
        }
        return headers


    def create_payment(
            self,
            amount: float,
            return_url: str,
            invoice_id: int,
    ) -> Tuple[str, str]:
        url = f"{self.BASE_URL}/payments"
        headers = self.get_auth_header()
        data = {
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "save_payment_method": "true",
            "metadata": {
                "invoice_id": invoice_id
            }
        }

        response = requests.post(url, json=data, headers=headers)

        try:
            response_data = response.json()
        except ValueError:
            raise Exception("YooKassa вернула некорректный JSON")

        if response.status_code != 200:
            raise Exception(f"Ошибка от YooKassa: {response_data.get('description', 'Unknown error')}")

        confirmation = response_data.get('confirmation')
        confirmation_url = confirmation.get('confirmation_url') if confirmation else None
        payment_id = response_data.get('id')
        if not confirmation_url or not payment_id:
            raise Exception("Ошибка создания платежа: не получен confirmation_url или id")
        return payment_id, confirmation_url

    def get_payment_info(self, payment_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/payments/{payment_id}"
        headers = {
            "Content-Type": "application/json",
        }
        auth = (self.SHOP_ID, self.SECRET_KEY)

        response = requests.get(url, headers=headers, auth=auth)
        try:
            return response.json()
        except ValueError:
            return {
                "error": "Invalid JSON response",
                "status_code": response.status_code,
                "text": response.text
            }

    def create_recurrent_payment(self,
                                 amount: int,
                                 payment_method_id: str,
                                 return_url: str,
                                 invoice_id: int):
        print('create recurrent payment')
        url = f"{self.BASE_URL}/payments"
        headers = self.get_auth_header()
        data = {
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "capture": True,
            "payment_method_id": payment_method_id,
            "metadata": {
                "invoice_id": invoice_id
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
        }

        response = requests.post(url, json=data, headers=headers)

        try:
            response_data = response.json()
        except ValueError:
            raise Exception("YooKassa вернула некорректный JSON")
        print(response_data)
        payment_id = response_data.get('id')
        return payment_id

