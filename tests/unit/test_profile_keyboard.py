import pytest
from bot.keyboards.keyboards import Keyboard


class TestProfileKeyboard:
    """Тесты для клавиатуры профиля"""
    
    def test_profile_menu_with_subs(self):
        """Тест клавиатуры профиля для пользователя с подпиской"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        # Тест для пользователя с подпиской
        markup = keyboard.profile_menu(has_subs=True, trial_used=True)
        
        # Проверяем, что есть кнопка управления подпиской
        assert any(btn.text == '⚙️ Управление подпиской' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что есть кнопка продления подписки
        assert any(btn.text == '🔄 Продлить подписку' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что есть кнопка бесплатных запросов
        assert any(btn.text == '🆓 Бесплатные запросы' for btn in markup.inline_keyboard[1])
        
        # Проверяем, что есть кнопка "Назад"
        assert any(btn.text == 'Назад' for btn in markup.inline_keyboard[2])
    
    def test_profile_menu_without_subs_trial_used(self):
        """Тест клавиатуры профиля для пользователя без подписки (триал использован)"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        # Тест для пользователя без подписки, триал использован
        markup = keyboard.profile_menu(has_subs=False, trial_used=True)
        
        # Проверяем, что есть кнопка покупки подписки
        assert any(btn.text == '🔥 Купить подписку' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что НЕТ кнопки продления подписки
        assert not any(btn.text == '🔄 Продлить подписку' for btn in markup.inline_keyboard[0])
    
    def test_profile_menu_without_subs_trial_not_used(self):
        """Тест клавиатуры профиля для пользователя без подписки (триал не использован)"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        # Тест для пользователя без подписки, триал не использован
        markup = keyboard.profile_menu(has_subs=False, trial_used=False)
        
        # Проверяем, что есть кнопка триала
        assert any(btn.text == '🔥 3 дня за 1 рубль' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что НЕТ кнопки продления подписки
        assert not any(btn.text == '🔄 Продлить подписку' for btn in markup.inline_keyboard[0])
    
    def test_subs_extend_keyboard(self):
        """Тест клавиатуры продления подписки"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        # Создаем мок-объекты подписок
        class MockSub:
            def __init__(self, id, name):
                self.id = id
                self.name = name
        
        available_subs = [
            MockSub(1, "Базовый"),
            MockSub(2, "Премиум")
        ]
        
        markup = keyboard.subs_extend_keyboard(available_subs=available_subs)
        
        # Проверяем, что есть кнопки подписок
        assert any(btn.text == 'Базовый' for btn in markup.inline_keyboard[0])
        assert any(btn.text == 'Премиум' for btn in markup.inline_keyboard[1])
        
        # Проверяем, что кнопка "Назад" ведет в профиль
        back_btn = next(btn for btn in markup.inline_keyboard[2] if btn.text == 'Назад')
        assert back_btn.callback_data == 'profile'

