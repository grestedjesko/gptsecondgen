from src.adapters.payments.yookassa_api import YookassaAPI
from app.config import Settings
from app.db.base import create_engine_and_session
from src.adapters.cache.redis_cache import RedisCache
from faster_whisper import WhisperModel

from config.subs import SubscriptionConfig
from src.services.ai.prompt_service import PromptService
from src.services.permission.permission_service import PermissionService
from src.services.whisper_service import WhisperService
from src.use_cases.usecases import UseCases
from src.services.ai.model_selection_service import ModelSelectionService
from src.adapters.ai_providers.registry import ProviderRegistry


def setup_di(di, config: Settings):
    engine, session_factory = create_engine_and_session(config)

    di.register("config", lambda: config)
    redis = RedisCache(config.redis_url)
    di.register("redis", lambda: redis)
    di.register("session_factory", lambda: session_factory)
    di.register("engine", lambda: engine)

    #whisper_model = WhisperModel("large", device="cuda", compute_type="float16")
    whisper_model = WhisperModel("large", device="cpu")
    whisper = WhisperService(model=whisper_model)

    di.register("whisper_service", lambda: WhisperService(whisper_model))

    permission_service = PermissionService(redis=redis,
                                           subs_config=SubscriptionConfig())

    model_selection_service = ModelSelectionService(config=config,
                                                    ai_providers=ProviderRegistry,
                                                    redis=redis,
                                                    permission_service=permission_service)

    di.register("model_selection_service", lambda: model_selection_service)

    tokens = {'openai': config.openai_key}
    ai_providers = ProviderRegistry(tokens=tokens)
    di.register("ai_providers", lambda: ProviderRegistry(tokens=tokens))

    prompt_service = PromptService()

    yookassa = YookassaAPI(shop_id=config.yookassa_shop_id,
                           secret_key=config.yookassa_secret_key)

    usecases = UseCases(redis=redis,
                        config=config,
                        ai_providers=ai_providers,
                        prompt_service=prompt_service,
                        model_selection_service=model_selection_service,
                        permission_service=permission_service,
                        whisper=whisper,
                        yookassa=yookassa)

    di.register("usecases", lambda: usecases)
