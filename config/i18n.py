"""
Простая система локализации для Telegram бота
Поддерживает русский и английский языки с автоопределением языка клиента
"""

from typing import Dict, Any, Optional
from enum import Enum
from aiogram.types import User


class Language(Enum):
    """Поддерживаемые языки"""
    RU = "ru"
    EN = "en"


# Все тексты в одном месте для удобства
TEXTS = {
    Language.RU: {
        # Основные тексты
        "limit_exceeded": """Упс, у вас закончились запросы к данной нейросети

Запросы обновляются в 00:00 по МСК каждый день.

Сейчас вы можете использовать другую нейросеть или купить пакет запросов.

Отследить оставшиеся запросы по всем нейросетям можно в профиле""",

        "nosubs_trial_text": """👋 Привет! Просто напиши свой запрос в чат — я всё сделаю за тебя!

🆓 Пользуйся ботом бесплатно!
❗️ Хочешь больше возможностей? Подключи подписку всего за 1 рубль!

<b>Что я умею:</b>
🎙️ Понимаю голосовые
📸 Присылай фото с заданием — я тебе его решу
📝 Пишу посты, сочинения, заявления и любые тексты
📚 Помогаю с учебой и заданиями
🎨 Рисую картинки с помощью нейросетей Midjourney 7.0 и DALL·E 3
🧠 Могу быть твоим психологом или просто поговорить по душам

<b>В подписке — доступ к 7 самым мощным нейросетям мира!</b>
Они решают 99% задач, с которыми сталкивается человек.

<b>👇 Попробуй всего за 1 рубль 👇</b>""",

        "nosubs_text": """👋 Привет! Просто напиши свой запрос в чат — я всё сделаю за тебя!

🆓 Пользуйся ботом бесплатно!
❗️ Хочешь больше возможностей? Подключи подписку!

<b>Что я умею:</b>
🎙️ Понимаю голосовые
📸 Присылай фото с заданием — я тебе его решу
📝 Пишу посты, сочинения, заявления и любые тексты
📚 Помогаю с учебой и заданиями
🎨 Рисую картинки с помощью нейросетей Midjourney 7.0 и DALL·E 3
🧠 Могу быть твоим психологом или просто поговорить по душам

<b>В подписке — доступ к 7 самым мощным нейросетям мира!</b>
Они решают 99% задач, с которыми сталкивается человек.""",

        "subs_text": """👋️ Я — твой личный помощник, который всегда рядом. Отвечу на любой вопрос, помогу с делами, поддержу, вдохновлю и даже нарисую картинку.

⤷ Запиши голосовое — отвечу сразу
⤷ Пришли фото с заданием — решу за тебя
⤷ Напишу пост, сочинение, заявление — что угодно
⤷ Помогу с любой задачей или полностью сделаю работу
⤷ Нарисую картину через Midjourney 7.0 или DALL·E 3
⤷ Могу быть твоим психологом, слушателем или просто другом

⭐️ Сейчас в работе — нейросеть {model_name}

👇 Просто напиши в чат — и начнём!""",

        "support_link": "t.me/re_tail",

        "default_prompt": """После того как ты дал основной ответ пользователю, сформулируй один короткий уточняющий вопрос, который легко поддержит диалог.

Требования к вопросу:
– Учитывай всю историю диалога(предыдущие сообщения пользователя и свои ответы).
– Вопрос должен быть максимально релевантным интересу пользователя
– Вопрос должен быть очень лёгким для ответа: максимум "Да/Нет", выбрать из двух вариантов или дать короткий ответ.
– Избегай абстрактных или философских вопросов ("О чём ты мечтаешь?" — нельзя).
– Старайся подталкивать к следующему логичному действию ("Хотите ещё примеры?", "Нужно расписать подробнее?", "Показать другую версию?").
– Вопрос должен звучать живо, естественно и по-человечески.
– Если диалог выглядит завершённым, предложи новую тему, связанную с интересами пользователя.

Формат:
Твой основной ответ пользователю строго до 4000 символов

➡️ краткий, конкретный, простой вопрос, так же давая ответ не используй символы разметки.""",

        "model_subs_text": """🍓 Данная нейросеть доступна только пользователям с подпиской.

В Америке она стоит 2500 рублей, но вы можете ее попробовать по цене чашечки кофе! 

С подпиской я стану эффективнее в 10 (!) раз — малая часть того, что вы получите, если оформите ее: 
⭐️ Безлимитное количество запросов (такого нет ни у кого)
⭐️ Доступ ко всем нейронкам — o4 mini, Midjourney 7.0, ChatGPT 4.1, и DALL•E 3
⭐️ Обработка запросов голосовыми сообщениями и многое другое  

P.S. — с подпиской я реально гораздо круче 😎""",

        "select_role_text": """🤩 Выберите роль с которой хотите общаться

Описание: {description}

Созданные роли отображаются значком: ⭐️""",

        "create_role_subs_text": """🥹 Создание ролей доступно только пользователям с подпиской.

Уверен, что оно будет тебе очень полезно!

Давай попробуем!""",

        "default_limit_text": """
→ Легкие нейросети: {light_remaining}
   ∙ GPT-5 mini

→ Обычные нейросети: {normal_remaining}
   ∙ GPT 5
   ∙ DeepSeek V3

→ Умные нейросети: {smart_remaining} 
   ∙ o4 mini
   ∙ Perplexity
   ∙ Claude 3.7
   ∙ Gemini 2.5 Pro

→ DALL•E 3: {dalle_remaining}
→ Midjourney 7.0: {mj_remaining}
""",

        "profile_text_no_subs": """👤Ваш профиль:

Запросов осталось:
<blockquote>{limit_text}</blockquote>

Генерации возобновляются {generation_renew_date}

Подписка Premium: Не активирована ❌

Нажмите на одну из кнопок ниже, чтобы подробнее изучить возможности получения генераций ⬇️
""",

        "profile_text_subs": """👤Ваш профиль:

Запросов осталось:
<blockquote>
{limit_text}
</blockquote>


Генерации возобновляются {generation_renew_date} 

Подписка Premium: Активирована ✅ 
Срок истечения: {period_end}
Автопродление: {renewal_status}

Нажмите на одну из кнопок ниже, чтобы подробнее изучить возможности получения генераций ⬇️""",

        "subs_role_text": """🥹 Функционал ролей доступен только пользователям с подпиской.

Описание: {description}

Уверен, что он будет тебе очень полезен!

Давай попробуем!""",

        # Роли
        "ROLE_MSG_TITLE_LEN": "Название роли должно быть 2–64 символа. Введите другое:",
        "ROLE_MSG_TITLE_EXISTS": "Такая роль уже существует. Введите другое название:",
        "ROLE_MSG_ASK_DESC": "Опишите роль (10–600 символов):",
        "ROLE_MSG_DESC_LEN": "Описание должно быть 10–600 символов. Попробуйте ещё раз:",
        "ROLE_MSG_ASK_PROMPT": "Введите промпт роли (что она должна делать)",
        "ROLE_MSG_PROMPT_LEN": "Промпт должен быть 10–600 символов. Попробуйте ещё раз:",
        "ROLE_MSG_RESET": "Сессия создания роли сброшена. Запустите снова /create_role.",
        "ROLE_LIMIT_REACHED": "Вы уже создали максимум ролей (5). Удалите одну, чтобы создать новую.",
        "ROLE_ASK_TITLE": "Введите название роли:",
        "ROLE_CUSTOM_LIST": "Нажмите на роль для редактирования / удаления",
        "ROLE_SETTINGS_TITLE": "Описание роли",
        "ROLE_CANNOT_DELETE": "Нельзя удалить эту роль",

        "base_subs_text": """⭐️<b> Подписка Premium:</b>

<blockquote>⤷ Доступ к новейшим нейросетям — o4 mini, DeepSeek V3 и Perplexity;
⤷ Доступ к GPT-4o, DALL•E 3, Midjourney 7.0;
⤷ Безлимитный доступ на GPT-4o-MINI;
⤷ Решение задач по фото;
⤷ Ускоренные ответы;
⤷ Ответы с источниками поиска;
⤷ Обработка запросов голосовыми;
⤷ Распознавание фотографий;
⤷ Генерация изображений; 
⤷ Личная тех.поддержка 24/7</blockquote>

<blockquote>🍓 Лимиты: 
→ Легкие нейросети: 100
   ∙ GPT-4.1 mini 
→ Обычные нейросети: 70
   ∙ ChatGPT 4.1
   ∙ DeepSeek V3 
→ Умные нейросети: 25
   ∙ o4 mini
   ∙ Perplexity
   ∙ Claude 3.7
   ∙ Gemini 2.5 Pro 
→ DALL•E 3: 15
→ Midjourney 7.0: 15</blockquote>  
<i>Генерации возобновляются каждый день в 00:00 по МСК</i>""",

        "edit_roles_text": """В данном разделе вы можете настраивать роли под свои задачи.

Выберите роль которую хотите редактировать или нажмите кнопку «👤 Создать новую роль»:""",

        "subscribe_trial_text": """<b>Пожалуйста, выберите удобный метод оплаты:</b>

<blockquote>⚠️ Пробная подписка после истечения срока включает в себя автопродление на месяц: 849р
Нажимая «Оплатить», вы соглашаетесь с Правилами приема рекуррентных платежей. Вы сможете отменить подписку в любой момент.</blockquote>""",

        "subscribe_text": """<b>Пожалуйста, выберите удобный метод оплаты:</b>

<blockquote>⚠️ Переходя на окно оплаты вы подтверждаете ознакомление и согласие с регламентом действия рекуррентных платежей.</blockquote>""",

        # Кнопки
        "btn_select_ai": "🤖 Выбрать нейросеть",
        "btn_select_role": "🎭 Выбрать роль",
        "btn_buy_subs": "🔥 Купить подписку",
        "btn_trial_3_days": "🔥 3 дня за 1 рубль",
        "btn_profile": "👤 Профиль",
        "btn_support": "Тех. поддержка",
        "btn_back": "Назад",
        "btn_main_menu": "Главное меню",
        "btn_edit_roles": "Редактировать роли",
        "btn_create_role": "Создать роль",
        "btn_delete_role": "Удалить роль",
        "btn_settings_subs": "⚙️ Управление подпиской",
        "btn_free_tokens": "🆓 Бесплатные запросы",
        "btn_stop_renew": "⏹ Отключить автопродление",
        "btn_start_renew": "🔄 Включить автопродление",
        "btn_extend_subs": "🔥 Продлить подписку",
        "btn_cancel": "❌ Отмена",
        "btn_pay_card": "Картой | СБП | {amount}₽",
        "btn_pay_stars": "TG Stars | {stars} ⭐",
        "btn_oferta": "Оферта",
        "btn_pay_1_rub": "💳 Оплатить 1 рубль",
        "renewal_activated": "Активировано",
        "renewal_not_activated": "Не активировано ❌",
        "no_active_subscription": "У вас нет активной подписки",
        "payment_rebind_text": "🔄 Возобновление подписки\n\nДля возобновления подписки необходимо оплатить 1 рубль. После успешной оплаты подписка будет возобновлена с новым способом оплаты.",
        
        # AI Models
        "model_auto": "Автоопределение модели",
        "model_gpt5_nano": "GPT-5 nano",
        "model_chatgpt41": "ChatGPT 4.1",
        "model_deepseek_v3": "DeepSeek V3",
        "model_o4_mini": "o4 mini",
        "model_perplexity": "Perplexity",
        "model_claude37": "Claude 3.7",
        "model_gemini25": "Gemini 2.5 Pro",
        "model_dalle3": "DALL•E 3",
        "model_midjourney": "Midjourney",
        
        # AI Model Selection
        "selected_model_description": "Описание выбранной модели: {description}\n\nДоступные модели:",
        "available_models": "Доступные модели:",
        
        # AI Roles
        "role_default": "Обычный",
        "role_lawyer": "Юрист",
        
        # AI Role Descriptions
        "role_default_description": "Эта роль бота призвана помогать вам в самых общих и разнообразных вопросах. Если у вас нет конкретного запроса, начните с этой роли. Она предоставит вам информацию и ответы на широкий спектр тем.",
        "role_lawyer_description": "Роль юриста",
        
        # Subscription Plans
        "sub_weekly": "Недельная",
        "sub_monthly": "Месячная", 
        "sub_yearly": "Годовая",
        "sub_trial": "5 дней за 1 рубль",
    },
    
    Language.EN: {
        # Основные тексты
        "limit_exceeded": """Oops, you've run out of requests to this neural network

Requests are renewed at 00:00 MSK every day.

You can now use another neural network or buy a request package.

Track remaining requests for all neural networks in your profile""",

        "nosubs_trial_text": """👋 Hi! Just write your request in the chat — I'll do everything for you!

🆓 Use the bot for free!
❗️ Want more features? Subscribe for just 1 ruble!

<b>What I can do:</b>
🎙️ I understand voice messages
📸 Send me a photo with a task — I'll solve it for you
📝 I write posts, essays, applications and any texts
📚 I help with studies and assignments
🎨 I draw pictures using Midjourney 7.0 and DALL·E 3 neural networks
🧠 I can be your psychologist or just chat heart to heart

<b>With subscription — access to 7 most powerful neural networks in the world!</b>
They solve 99% of tasks that a person faces.

<b>👇 Try for just 1 ruble 👇</b>""",

        "nosubs_text": """👋 Hi! Just write your request in the chat — I'll do everything for you!

🆓 Use the bot for free!
❗️ Want more features? Subscribe!

<b>What I can do:</b>
🎙️ I understand voice messages
📸 Send me a photo with a task — I'll solve it for you
📝 I write posts, essays, applications and any texts
📚 I help with studies and assignments
🎨 I draw pictures using Midjourney 7.0 and DALL·E 3 neural networks
🧠 I can be your psychologist or just chat heart to heart

<b>With subscription — access to 7 most powerful neural networks in the world!</b>
They solve 99% of tasks that a person faces.""",

        "subs_text": """👋️ I'm your personal assistant who's always nearby. I'll answer any question, help with tasks, support, inspire and even draw a picture.

⤷ Record a voice message — I'll answer immediately
⤷ Send a photo with a task — I'll solve it for you
⤷ I'll write a post, essay, application — anything
⤷ I'll help with any task or do the work completely
⤷ I'll draw a picture through Midjourney 7.0 or DALL·E 3
⤷ I can be your psychologist, listener or just a friend

⭐️ Currently working — neural network {model_name}

👇 Just write in the chat — and let's start!""",

        "support_link": "t.me/re_tail",

        "default_prompt": """After you've given the main answer to the user, formulate one short clarifying question that will easily support the dialogue.

Question requirements:
– Consider the entire dialogue history (previous user messages and your responses).
– The question should be maximally relevant to the user's interest
– The question should be very easy to answer: maximum "Yes/No", choose from two options or give a short answer.
– Avoid abstract or philosophical questions ("What do you dream about?" — not allowed).
– Try to push towards the next logical action ("Want more examples?", "Need to elaborate?", "Show another version?").
– The question should sound lively, natural and human-like.
– If the dialogue looks completed, suggest a new topic related to the user's interests.

Format:
Your main answer to the user strictly up to 4000 characters

➡️ brief, specific, simple question, also when giving an answer don't use markup symbols.""",

        "model_subs_text": """🍓 This neural network is only available to users with a subscription.

In America it costs 2500 rubles, but you can try it for the price of a cup of coffee! 

With a subscription I'll become 10 (!) times more effective — a small part of what you'll get if you subscribe: 
⭐️ Unlimited number of requests (no one else has this)
⭐️ Access to all neural networks — o4 mini, Midjourney 7.0, ChatGPT 4.1, and DALL•E 3
⭐️ Processing requests with voice messages and much more  

P.S. — with a subscription I'm really much cooler 😎""",

        "select_role_text": """🤩 Choose the role you want to communicate with

Description: {description}

Created roles are displayed with the icon: ⭐️""",

        "create_role_subs_text": """🥹 Role creation is only available to users with a subscription.

I'm sure it will be very useful for you!

Let's try!""",

        "default_limit_text": """
→ Light neural networks: {light_remaining}
   ∙ GPT-5 mini

→ Regular neural networks: {normal_remaining}
   ∙ GPT 5
   ∙ DeepSeek V3

→ Smart neural networks: {smart_remaining} 
   ∙ o4 mini
   ∙ Perplexity
   ∙ Claude 3.7
   ∙ Gemini 2.5 Pro

→ DALL•E 3: {dalle_remaining}
→ Midjourney 7.0: {mj_remaining}
""",

        "profile_text_no_subs": """👤Your profile:

Requests remaining:
<blockquote>{limit_text}</blockquote>

Generations renew {generation_renew_date}

Premium subscription: Not activated ❌

Click one of the buttons below to learn more about generation options ⬇️
""",

        "profile_text_subs": """👤Your profile:

Requests remaining:
<blockquote>
{limit_text}
</blockquote>


Generations renew {generation_renew_date} 

Premium subscription: Activated ✅ 
Expiration date: {period_end}
Auto-renewal: {renewal_status}

Click one of the buttons below to learn more about generation options ⬇️""",

        "subs_role_text": """🥹 Role functionality is only available to users with a subscription.

Description: {description}

I'm sure it will be very useful for you!

Let's try!""",

        # Роли
        "ROLE_MSG_TITLE_LEN": "Role name should be 2–64 characters. Enter another:",
        "ROLE_MSG_TITLE_EXISTS": "Such a role already exists. Enter another name:",
        "ROLE_MSG_ASK_DESC": "Describe the role (10–600 characters):",
        "ROLE_MSG_DESC_LEN": "Description should be 10–600 characters. Try again:",
        "ROLE_MSG_ASK_PROMPT": "Enter the role prompt (what it should do)",
        "ROLE_MSG_PROMPT_LEN": "Prompt should be 10–600 characters. Try again:",
        "ROLE_MSG_RESET": "Role creation session reset. Start again with /create_role.",
        "ROLE_LIMIT_REACHED": "You've already created the maximum number of roles (5). Delete one to create a new one.",
        "ROLE_ASK_TITLE": "Enter role name:",
        "ROLE_CUSTOM_LIST": "Click on a role to edit / delete",
        "ROLE_SETTINGS_TITLE": "Role description",
        "ROLE_CANNOT_DELETE": "Cannot delete this role",

        "base_subs_text": """⭐️<b> Premium Subscription:</b>

<blockquote>⤷ Access to the latest neural networks — o4 mini, DeepSeek V3 and Perplexity;
⤷ Access to GPT-4o, DALL•E 3, Midjourney 7.0;
⤷ Unlimited access to GPT-4o-MINI;
⤷ Photo task solving;
⤷ Accelerated responses;
⤷ Responses with search sources;
⤷ Voice request processing;
⤷ Photo recognition;
⤷ Image generation; 
⤷ Personal tech support 24/7</blockquote>

<blockquote>🍓 Limits: 
→ Light neural networks: 100
   ∙ GPT-4.1 mini 
→ Regular neural networks: 70
   ∙ ChatGPT 4.1
   ∙ DeepSeek V3 
→ Smart neural networks: 25
   ∙ o4 mini
   ∙ Perplexity
   ∙ Claude 3.7
   ∙ Gemini 2.5 Pro 
→ DALL•E 3: 15
→ Midjourney 7.0: 15</blockquote>  
<i>Generations renew every day at 00:00 MSK</i>""",

        "edit_roles_text": """In this section you can configure roles for your tasks.

Choose the role you want to edit or click the "👤 Create new role" button:""",

        "subscribe_trial_text": """<b>Please choose a convenient payment method:</b>

<blockquote>⚠️ Trial subscription after expiration includes auto-renewal for a month: 849₽
By clicking "Pay", you agree to the Rules for accepting recurring payments. You can cancel your subscription at any time.</blockquote>""",

        "subscribe_text": """<b>Please choose a convenient payment method:</b>

<blockquote>⚠️ By proceeding to the payment window you confirm that you have read and agree to the regulations for recurring payments.</blockquote>""",

        # Кнопки
        "btn_select_ai": "🤖 Select AI",
        "btn_select_role": "🎭 Select Role",
        "btn_buy_subs": "🔥 Buy Subscription",
        "btn_trial_3_days": "🔥 3 days for 1 ruble",
        "btn_profile": "👤 Profile",
        "btn_support": "Tech Support",
        "btn_back": "Back",
        "btn_main_menu": "Main Menu",
        "btn_edit_roles": "Edit Roles",
        "btn_create_role": "Create Role",
        "btn_delete_role": "Delete Role",
        "btn_settings_subs": "⚙️ Subscription Management",
        "btn_free_tokens": "🆓 Free Requests",
        "btn_stop_renew": "⏹ Disable Auto-renewal",
        "btn_start_renew": "🔄 Enable Auto-renewal",
        "btn_extend_subs": "🔥 Extend Subscription",
        "btn_cancel": "❌ Cancel",
        "btn_pay_card": "Card | SBP | {amount}₽",
        "btn_pay_stars": "TG Stars | {stars} ⭐",
        "btn_oferta": "Terms",
        "btn_pay_1_rub": "💳 Pay 1 ruble",
        "renewal_activated": "Activated",
        "renewal_not_activated": "Not activated ❌",
        "no_active_subscription": "You don't have an active subscription",
        "payment_rebind_text": "🔄 Subscription Renewal\n\nTo renew your subscription, you need to pay 1 ruble. After successful payment, the subscription will be renewed with a new payment method.",
        
        # AI Models
        "model_auto": "Auto Model Selection",
        "model_gpt5_nano": "GPT-5 nano",
        "model_chatgpt41": "ChatGPT 4.1",
        "model_deepseek_v3": "DeepSeek V3",
        "model_o4_mini": "o4 mini",
        "model_perplexity": "Perplexity",
        "model_claude37": "Claude 3.7",
        "model_gemini25": "Gemini 2.5 Pro",
        "model_dalle3": "DALL•E 3",
        "model_midjourney": "Midjourney",
        
        # AI Model Selection
        "selected_model_description": "Selected model description: {description}\n\nAvailable models:",
        "available_models": "Available models:",
        
        # AI Roles
        "role_default": "Default",
        "role_lawyer": "Lawyer",
        
        # AI Role Descriptions
        "role_default_description": "This bot role is designed to help you with the most general and diverse questions. If you don't have a specific request, start with this role. It will provide you with information and answers on a wide range of topics.",
        "role_lawyer_description": "Lawyer role",
        
        # Subscription Plans
        "sub_weekly": "Weekly",
        "sub_monthly": "Monthly",
        "sub_yearly": "Yearly", 
        "sub_trial": "5 days for 1 ruble",
    }
}


def get_user_language(user: User) -> Language:
    """
    Определяет язык пользователя на основе его настроек Telegram
    
    Args:
        user: Объект пользователя Telegram
    
    Returns:
        Язык пользователя
    """
    print(user.language_code)
    print(user)
    if not user.language_code:
        return Language.RU
    
    # Извлекаем основной код языка
    main_code = user.language_code.split('-')[0].lower()
    
    # Специальная обработка для русских кодов
    if main_code in ['ru', 'be', 'uk', 'kk', 'ky', 'uz', 'tg']:
        return Language.RU
    
    # Специальная обработка для английских кодов
    if main_code in ['en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'sv', 'no', 'da', 'fi']:
        return Language.EN
    
    # По умолчанию русский
    return Language.RU


def get_text(key: str, user: User, **kwargs) -> str:
    """
    Получает переведенный текст для пользователя
    
    Args:
        key: Ключ текста
        user: Объект пользователя Telegram
        **kwargs: Параметры для форматирования строки
    
    Returns:
        Переведенный текст
    """
    language = get_user_language(user)
    text = TEXTS[language].get(key, key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            # Если форматирование не удалось, возвращаем текст как есть
            pass
    
    return text


def get_localized_model_name(model_name: str, user: User) -> str:
    """
    Получает локализованное название модели AI
    
    Args:
        model_name: Оригинальное название модели из базы данных
        user: Объект пользователя Telegram
    
    Returns:
        Локализованное название модели
    """
    # Маппинг оригинальных названий на ключи локализации
    model_mapping = {
        "Автоопределение модели": "model_auto",
        "GPT-5 nano": "model_gpt5_nano",
        "ChatGPT 4.1": "model_chatgpt41",
        "DeepSeek V3": "model_deepseek_v3",
        "o4 mini": "model_o4_mini",
        "Perplexity": "model_perplexity",
        "Claude 3.7": "model_claude37",
        "Gemini 2.5 Pro": "model_gemini25",
        "DALL•E 3": "model_dalle3",
        "Midjourney": "model_midjourney",
    }
    
    # Если есть маппинг, возвращаем локализованное название
    if model_name in model_mapping:
        return get_text(model_mapping[model_name], user)
    
    # Если маппинга нет, возвращаем оригинальное название
    return model_name


def get_localized_role_name(role_name: str, user: User) -> str:
    """
    Получает локализованное название роли AI
    
    Args:
        role_name: Оригинальное название роли из базы данных
        user: Объект пользователя Telegram
    
    Returns:
        Локализованное название роли
    """
    # Маппинг оригинальных названий на ключи локализации
    role_mapping = {
        "Обычный": "role_default",
        "Юрист": "role_lawyer",
    }
    
    # Если есть маппинг, возвращаем локализованное название
    if role_name in role_mapping:
        return get_text(role_mapping[role_name], user)
    
    # Если маппинга нет, возвращаем оригинальное название
    return role_name


def get_localized_role_description(role_name: str, user: User) -> str:
    """
    Получает локализованное описание роли AI
    
    Args:
        role_name: Оригинальное название роли из базы данных
        user: Объект пользователя Telegram
    
    Returns:
        Локализованное описание роли
    """
    # Маппинг оригинальных названий на ключи локализации описаний
    role_description_mapping = {
        "Обычный": "role_default_description",
        "Юрист": "role_lawyer_description",
    }
    
    # Если есть маппинг, возвращаем локализованное описание
    if role_name in role_description_mapping:
        return get_text(role_description_mapping[role_name], user)
    
    # Если маппинга нет, возвращаем оригинальное описание
    return role_name


def get_localized_subscription_name(sub_name: str, user: User) -> str:
    """
    Получает локализованное название тарифа подписки
    
    Args:
        sub_name: Оригинальное название тарифа из базы данных
        user: Объект пользователя Telegram
    
    Returns:
        Локализованное название тарифа
    """
    # Маппинг оригинальных названий на ключи локализации
    sub_mapping = {
        "Недельная": "sub_weekly",
        "Месячная": "sub_monthly",
        "Годовая": "sub_yearly",
        "5 дней за 1 рубль": "sub_trial",
    }
    
    # Если есть маппинг, возвращаем локализованное название
    if sub_name in sub_mapping:
        return get_text(sub_mapping[sub_name], user)
    
    # Если маппинга нет, возвращаем оригинальное название
    return sub_name


def get_text_by_language(key: str, language: Language, **kwargs) -> str:
    """
    Получает переведенный текст для конкретного языка
    
    Args:
        key: Ключ текста
        language: Язык
        **kwargs: Параметры для форматирования строки
    
    Returns:
        Переведенный текст
    """
    text = TEXTS[language].get(key, key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            # Если форматирование не удалось, возвращаем текст как есть
            pass
    
    return text
