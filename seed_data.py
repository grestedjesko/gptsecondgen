from tkinter import Pack
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import (AiModels,
                           SubType, 
                           Subs,
                           AiRoles, 
                           AiModelSubsConnection, 
                           AiModelPacketConnection,
                           PacketType, 
                           Packet)
from app.db.models.ai_models import AiModelsType


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
    
    session.add_all([
        AiModels(id=1, name="Авто", 
                 type=AiModelsType.TEXT, 
                 api_name="auto", 
                 api_provider='', 
                 api_link="", 
                 generation_cost=1),
        
        AiModels(id=2, name="GPT-5 mini", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-5-nano", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
                
        AiModels(id=3, name="GPT-4o mini", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o-mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=4, name="Gemini 2.5 Flash (New)", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=5, name="DeepSeek-V3.1", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=6, name="DeepSeek-V3.1 Thinking", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=7, name="GPT-5", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-5", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=8, name="GPT-4.1", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=9, name="OpenAI o4-mini", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=10, name="OpenAI o3", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=11, name="Claude 4 Sonnet", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=12, name="Claude 4 Thinking", 
                 type=AiModelsType.TEXT, 
                 api_name="gpt-4o mini", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=13, name="GPT Images", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=14, name="Gemini Images", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=15, name="Midjourney", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=16, name="FLUX", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=17, name="DALL•E 3", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=18, name="Набор аватарок", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=19, name="Замена лиц", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=20, name="Увеличение Х2/Х4", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=21, name="Удаление фона", 
                 type=AiModelsType.IMAGE, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=22, name="Veo 3", 
                 type=AiModelsType.VIDEO, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=23, name="Kling AI", 
                 type=AiModelsType.VIDEO, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=24, name="Hailuo 02", 
                 type=AiModelsType.VIDEO, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=25, name="Pika 2.2", 
                 type=AiModelsType.VIDEO, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=26, name="Pika Effects", 
                 type=AiModelsType.VIDEO, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        
        AiModels(id=27, name="Pika Characters", 
                 type=AiModelsType.VIDEO, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=28, name="Suno", 
                 type=AiModelsType.MUSIC, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),

        AiModels(id=29, name="Suno Pro", 
                 type=AiModelsType.MUSIC, 
                 api_name="gpt-images", 
                 api_provider='openai',
                 api_link="",
                 generation_cost=1),
        ]),
        
    session.add_all([
        SubType(id=0, name='Бесплатная', is_visible=False),
        SubType(id=1, name='Premium', is_visible=True, daily_query_limit=100),
    ])
 
    await session.commit()

    session.add_all([
        Subs(id=2, name="Недельная", subtype_id=1, kind='BASE', base_sub_id=None, period=7, price=2, stars_price=2,
             is_visible=True),
        Subs(id=3, name="Месячная", subtype_id=1, kind='BASE', base_sub_id=None, period=30, price=3, stars_price=1,
             is_visible=True),
        Subs(id=4, name="Годовая", subtype_id=1, kind='BASE', base_sub_id=None, period=365, price=4, stars_price=4,
             is_visible=True),
    ])
    await session.flush()  

    session.add(
        Subs(id=1, name="5 дней за 1 рубль", subtype_id=1, kind='TRIAL',
             base_sub_id=3, period=7, price=1, stars_price=3, is_visible=True)
    )
    await session.commit()

    session.add_all([
        PacketType(id=1, name="Нейро+", description="", is_visible=True),
        PacketType(id=2, name="Midjourney / Flux", description="", is_visible=True),
        PacketType(id=3, name="Видео", description="", is_visible=True),
        PacketType(id=4, name="Suno", description="", is_visible=True),
    ])
    await session.commit()

    session.add_all([
        Packet(id=1, type_id=1, name="50 запросов", price=200, stars_price=200, generation_limit=50),
        Packet(id=2, type_id=1, name="100 запросов", price=350, stars_price=350, generation_limit=100),
        Packet(id=3, type_id=1, name="200 запросов", price=600, stars_price=600, generation_limit=200),
        Packet(id=4, type_id=1, name="500 запросов", price=1200, stars_price=1200, generation_limit=500),

        Packet(id=5, type_id=2, name="50 генераций", price=200, stars_price=200, generation_limit=100),
        Packet(id=6, type_id=2, name="100 генераций", price=350, stars_price=350, generation_limit=100),
        Packet(id=7, type_id=2, name="200 генераций", price=600, stars_price=600, generation_limit=200),
        Packet(id=8, type_id=2, name="500 генераций", price=1200, stars_price=1200, generation_limit=500),

        Packet(id=9, type_id=3, name="2 генерации", price=150, stars_price=150, generation_limit=100),
        Packet(id=10, type_id=3, name="10 генераций", price=500, stars_price=500, generation_limit=100),
        Packet(id=11, type_id=3, name="20 генераций", price=900, stars_price=900, generation_limit=200),
        Packet(id=12, type_id=3, name="50 генераций", price=2000, stars_price=2000, generation_limit=500),

        Packet(id=13, type_id=4, name="20 генераций", price=200, stars_price=200, generation_limit=100),
        Packet(id=14, type_id=4, name="50 генераций", price=450, stars_price=450, generation_limit=100),
        Packet(id=15, type_id=4, name="100 генераций", price=800, stars_price=800, generation_limit=200),
    ])
    