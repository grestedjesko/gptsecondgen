# 🌍 Система локализации бота

## Описание

Реализована простая и эффективная система локализации для Telegram бота с поддержкой русского и английского языков. Система автоматически определяет язык пользователя на основе его настроек Telegram.

## Структура

### Основной файл: `config/i18n.py`

Содержит:
- Все тексты на русском и английском языках в одном месте
- Функции для определения языка пользователя
- Функции для получения переведенных текстов

## Использование

### 1. Получение текста для пользователя

```python
from config.i18n import get_text
from aiogram.types import User

# Простой текст
text = get_text("btn_profile", user)

# Текст с параметрами
text = get_text("subs_text", user, model_name="GPT-4")
```

### 2. Определение языка пользователя

```python
from config.i18n import get_user_language, Language

language = get_user_language(user)
if language == Language.RU:
    print("Пользователь говорит по-русски")
```

### 3. Получение текста по языку

```python
from config.i18n import get_text_by_language, Language

text = get_text_by_language("btn_profile", Language.EN)
```

## Поддерживаемые языки

### Русский (Language.RU)
- Коды: `ru`, `be`, `uk`, `kk`, `ky`, `uz`, `tg`
- Используется по умолчанию для неизвестных языков

### Английский (Language.EN)  
- Коды: `en`, `es`, `fr`, `de`, `it`, `pt`, `nl`, `sv`, `no`, `da`, `fi`
- Для западноевропейских языков

## Добавление новых текстов

1. Откройте файл `config/i18n.py`
2. Найдите словарь `TEXTS`
3. Добавьте новый ключ в оба языка:

```python
TEXTS = {
    Language.RU: {
        # ... существующие тексты ...
        "new_text_key": "Новый текст на русском",
    },
    Language.EN: {
        # ... существующие тексты ...
        "new_text_key": "New text in English",
    }
}
```

## Добавление параметров в тексты

Используйте фигурные скобки для параметров:

```python
"welcome_message": "Привет, {name}! Добро пожаловать в бот!"
```

Затем используйте:

```python
text = get_text("welcome_message", user, name="Иван")
```

## Тестирование

Запустите тест для проверки работы локализации:

```bash
python3 test_simple_i18n.py
```

## Интеграция в код

### В use cases:

```python
from config.i18n import get_text

class MyUseCase:
    async def run(self, user: User, session: AsyncSession):
        text = get_text("my_text_key", user, param1="value1")
        return text
```

### В клавиатурах:

```python
from config.i18n import get_text

def my_keyboard(self, user: User):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=get_text("btn_my_button", user),
        callback_data="my_callback"
    ))
    return builder.as_markup()
```

### В обработчиках:

```python
from config.i18n import get_text

@router.message(Command('start'))
async def start_handler(message: Message):
    text = get_text("welcome_message", message.from_user)
    await message.answer(text)
```

## Преимущества новой системы

1. **Простота** - все тексты в одном файле
2. **Удобство** - легко найти и изменить любой текст
3. **Надежность** - корректное определение языка пользователя
4. **Производительность** - минимальные накладные расходы
5. **Расширяемость** - легко добавить новые языки

## Миграция со старой системы

Старая система с `localization_service` была заменена на новую. Все вызовы автоматически обновлены:

- `localization_service.get_text_for_user(key, user)` → `get_text(key, user)`
- `localization_service.get_text_for_user(key, user, **kwargs)` → `get_text(key, user, **kwargs)`

## Поддержка

При возникновении проблем:
1. Проверьте, что импорт `from config.i18n import get_text` присутствует
2. Убедитесь, что ключ текста существует в словаре `TEXTS`
3. Проверьте корректность параметров в тексте
4. Запустите тест для диагностики
