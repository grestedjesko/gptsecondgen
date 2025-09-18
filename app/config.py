from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    tg_token: str
    redis_url: str
    provider_default: str = "openai"

    openai_key: str
    perplexity_key: str
    aitunnel_key: str

    s3_access_key: str
    s3_secret_key: str
    s3_endpoint_url: str
    s3_bucket_name: str
    s3_domain: str
    s3_region: str

    db_url: str

    support_link: str
    webapp_url: str

    auto_model: str
    auto_model_token: Optional[str]
    auto_model_provider: Optional[str]

    light_class_id: int = 1
    normal_class_id: int = 2
    smart_class_id: int = 3
    dalle_class_id: int = 4
    midjourney_class_id: int = 5

    yookassa_shop_id: str
    yookassa_secret_key: str


    class Config:
        env_file = ".env"
