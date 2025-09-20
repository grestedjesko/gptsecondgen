from src.adapters.ai_providers.registry import ProviderRegistry
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.payments.yookassa_api import YookassaAPI
from bot.keyboards.keyboards import Keyboard
from src.services.ai.model_selection_service import ModelSelectionService
from src.services.ai.prompt_service import PromptService
from src.services.chat_history_service import ChatHistoryService
from src.services.permission.permission_service import PermissionService
from src.services.whisper_service import WhisperService
from src.use_cases.handle_payment import HandlePaymentUseCase
from src.use_cases.process_message.handle_document_message import HandleDocumentMessageUseCase
from src.use_cases.process_message.handle_voice_message import HandleVoiceMessageUseCase
from src.use_cases.select_ai import SelectAiModelUseCase
from src.use_cases.role import RoleUseCase
from src.use_cases.start_menu import StartMenuUseCase
from src.use_cases.profile import ProfileUseCase
from src.use_cases.process_message.process_message import ProcessMessageUseCase
from src.use_cases.process_message.handle_text_message import HandleTextMessageUseCase
from src.use_cases.process_message.handle_photo_message import HandlePhotoMessageUseCase
from src.use_cases.subscription import SubscriptionUseCase
from src.use_cases.settings import SettingsUseCase
from app.config import Settings
from src.adapters.s3.s3_client import S3Client


class UseCases:
    def __init__(self,
                 redis: RedisCache,
                 config: Settings,
                 ai_providers: ProviderRegistry,
                 prompt_service: PromptService,
                 model_selection_service: ModelSelectionService,
                 permission_service: PermissionService,
                 whisper: WhisperService,
                 yookassa: YookassaAPI):
        keyboard = Keyboard(
            support_link=config.support_link,
            webapp_url=config.webapp_url
        )

        self.start_menu = StartMenuUseCase(
            config=config,
            keyboard=keyboard,
            redis=redis
        )

        self.profile = ProfileUseCase(redis=redis,
                                      config=config,
                                      keyboard=keyboard)

        self.select_ai = SelectAiModelUseCase(redis=redis, keyboard=keyboard)
        self.role = RoleUseCase(redis=redis, keyboard=keyboard)

        chat_history_service = ChatHistoryService(redis=redis)

        self.process_message = ProcessMessageUseCase(chat_history_service=chat_history_service,
                                                     ai_providers=ai_providers,
                                                     prompt_service=prompt_service,
                                                     model_selection_service=model_selection_service,)

        self.handle_text_message = HandleTextMessageUseCase(redis=redis,
                                                            permission_service=permission_service,
                                                            process_message_usecase=self.process_message)

        s3_client = S3Client(
            access_key=config.s3_access_key,
            secret_key=config.s3_secret_key,
            endpoint_url=config.s3_endpoint_url,
            bucket_name=config.s3_bucket_name,
            domain_name=config.s3_domain,
            region_name=config.s3_region
        )

        self.handle_photo_message = HandlePhotoMessageUseCase(redis=redis,
                                                              s3client=s3_client,
                                                              permission_service=permission_service,
                                                              process_message_usecase=self.process_message)

        self.handle_document_message = HandleDocumentMessageUseCase(redis=redis,
                                                                    s3client=s3_client,
                                                                    permission_service=permission_service,
                                                                    process_message_usecase=self.process_message)

        self.handle_voice_message = HandleVoiceMessageUseCase(redis=redis,
                                                              whisper=whisper,
                                                              permission_service=permission_service,
                                                              process_message_usecase=self.process_message)

        self.subscription = SubscriptionUseCase(redis=redis,
                                                keyboard=keyboard,
                                                yookassa=yookassa)

        self.settings = SettingsUseCase(keyboard=keyboard)

        self.handle_payment = HandlePaymentUseCase()