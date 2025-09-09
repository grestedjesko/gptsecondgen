from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AiModelsClass, AiModels, SubTypeLimits, SubType, Subs, AiRoles


async def seed_data(session: AsyncSession):
    session.add_all([
        AiRoles(id=1,
                user_id=1,
                name='Обычный',
                description='Эта роль бота призвана помогать вам в самых общих и разнообразных вопросах. Если у вас нет конкретного запроса, начните с этой роли. Она предоставит вам информацию и ответы на широкий спектр тем.',
                prompt='Промпт:',
                free_available=True
                ),
        AiRoles(id=2,
                user_id=1,
                name='Юрист',
                description='Роль юриста',
                prompt='Промпт:',
                free_available=False
                )
    ])
    # Классы моделей
    session.add_all([
        AiModelsClass(id=1, name="Легкие нейросети"),
        AiModelsClass(id=2, name="Обычные нейросети"),
        AiModelsClass(id=3, name="Умные нейросети"),
        AiModelsClass(id=4, name="DALL•E 3"),
        AiModelsClass(id=5, name="Midjourney 7")
    ])

    # Модели
    session.add_all([
        AiModels(id=1, name="GPT-5 nano", api_name="gpt-5-nano", api_provider='openai', api_link="https://api.aitunnel.ru/v1/", model_class_id=1),
        AiModels(id=2, name="ChatGPT 4.1", api_name="gpt-4.1", api_provider='openai', api_link="https://api.cometapi.com/v1/chat/completions", model_class_id=2),
        AiModels(id=3, name="DeepSeek V3", api_name="deepseek-v3", api_provider='openai', api_link="https://api.cometapi.com/v1/chat/completions", model_class_id=2),
        AiModels(id=4, name="o4 mini", api_name="o4-mini", api_provider='openai', api_link="https://api.cometapi.com/v1/chat/completions", model_class_id=3),
        AiModels(id=5, name="Perplexity", api_name="sonar", api_provider='openai', api_link="https://api.aitunnel.ru/v1/", model_class_id=3),
        AiModels(id=6, name="Claude 3.7", api_name="claude-3-7-sonnet-latest", api_provider='openai', api_link="https://api.cometapi.com/v1/messages", model_class_id=3),
        AiModels(id=7, name="Gemini 2.5 Pro", api_name="gemini-2.5-pro-preview-03-25", api_provider='openai', api_link="https://api.cometapi.com/v1/chat/completions", model_class_id=3),
        AiModels(id=8, name="DALL•E 3", api_name="gpt-4o-image", api_provider='openai', api_link="https://api.cometapi.com/v1/images/generations", model_class_id=4),
        AiModels(id=9, name="Midjourney", api_name="mj_fast_imagine", api_provider='openai', api_link="https://api.cometapi.com/mj/submit/imagine", model_class_id=5)
    ])

    # Подтипы
    session.add_all([
        SubType(id=0, name="free"),
        SubType(id=1, name="base")
    ])

    # ✅ Commit to ensure SubTypes are inserted and available for FK reference
    await session.commit()

    # Конфигурации подтипов
    session.add_all([
        SubTypeLimits(id=1, subtype_id=0, ai_models_class=1, daily_question_limit=10, daily_token_limit=10000),
        SubTypeLimits(id=2, subtype_id=0, ai_models_class=2, daily_question_limit=0, daily_token_limit=0),
        SubTypeLimits(id=3, subtype_id=0, ai_models_class=3, daily_question_limit=0, daily_token_limit=0),
        SubTypeLimits(id=4, subtype_id=0, ai_models_class=4, daily_question_limit=0, daily_token_limit=0),
        SubTypeLimits(id=5, subtype_id=0, ai_models_class=5, daily_question_limit=0, daily_token_limit=0),
        SubTypeLimits(id=6, subtype_id=1, ai_models_class=1, daily_question_limit=100, daily_token_limit=100000),
        SubTypeLimits(id=7, subtype_id=1, ai_models_class=2, daily_question_limit=70, daily_token_limit=100000),
        SubTypeLimits(id=8, subtype_id=1, ai_models_class=3, daily_question_limit=25, daily_token_limit=100000),
        SubTypeLimits(id=9, subtype_id=1, ai_models_class=4, daily_question_limit=15, daily_token_limit=100000),
        SubTypeLimits(id=10, subtype_id=1, ai_models_class=5, daily_question_limit=15, daily_token_limit=100000)
    ])

    # Подписки
    # base plans first
    session.add_all([
        Subs(id=2, name="Недельная", subtype_id=1, kind='BASE', base_sub_id=None, period=7, price=2, stars_price=2,
             is_visible=True),
        Subs(id=3, name="Месячная", subtype_id=1, kind='BASE', base_sub_id=None, period=30, price=3, stars_price=1,
             is_visible=True),
        Subs(id=4, name="Годовая", subtype_id=1, kind='BASE', base_sub_id=None, period=365, price=4, stars_price=4,
             is_visible=True),
    ])
    await session.flush()  # make sure rows exist in DB (still inside the same tx)

    # now the trial that references id=3
    session.add(
        Subs(id=1, name="5 дней за 1 рубль", subtype_id=1, kind='TRIAL',
             base_sub_id=3, period=7, price=1, stars_price=3, is_visible=True)
    )
    await session.commit()

