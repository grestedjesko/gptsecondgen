import pytest
from unittest.mock import Mock, AsyncMock
from bot.keyboards.keyboards import Keyboard


class TestSubscriptionRenewal:
    """Тесты для функциональности возобновления подписки"""
    
    def test_subs_settings_keyboard_with_renewal_disabled(self):
        """Тест клавиатуры настроек подписки с выключенным продлением"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        # Тест для пользователя с выключенным продлением
        markup = keyboard.subs_settings_keyboard(will_renew=False)
        
        # Проверяем, что есть кнопка возобновления подписки
        assert any(btn.text == '🔄 Возобновить подписку' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что НЕТ кнопки отключения автопродления
        assert not any(btn.text == '⏹ Отключить автопродление' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что есть кнопка "Назад"
        assert any(btn.text == 'Назад' for btn in markup.inline_keyboard[1])
    
    def test_subs_settings_keyboard_with_renewal_enabled(self):
        """Тест клавиатуры настроек подписки с включенным продлением"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        # Тест для пользователя с включенным продлением
        markup = keyboard.subs_settings_keyboard(will_renew=True)
        
        # Проверяем, что есть кнопка отключения автопродления
        assert any(btn.text == '⏹ Отключить автопродление' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что НЕТ кнопки возобновления подписки
        assert not any(btn.text == '🔄 Возобновить подписку' for btn in markup.inline_keyboard[0])
        
        # Проверяем, что есть кнопка "Назад"
        assert any(btn.text == 'Назад' for btn in markup.inline_keyboard[1])
    
    
    def test_payment_rebind_keyboard(self):
        """Тест клавиатуры для возобновления подписки"""
        keyboard = Keyboard(support_link="https://t.me/support", webapp_url="https://app.example.com")
        
        test_link = "https://yookassa.ru/pay/test_link"
        markup = keyboard.payment_rebind_keyboard(link=test_link)
        
        # Проверяем, что есть кнопка оплаты
        pay_btn = next(btn for btn in markup.inline_keyboard[0] if btn.text == '💳 Оплатить 1 рубль')
        assert pay_btn.url == test_link
        
        # Проверяем, что есть кнопка "Назад" в настройки подписки
        back_btn = next(btn for btn in markup.inline_keyboard[1] if btn.text == 'Назад')
        assert back_btn.callback_data == 'settings_subs'
    
    def test_invoice_reason_enum(self):
        """Тест нового типа причины счета"""
        from app.db.models.invoice import InvoiceReason
        
        # Проверяем, что новый тип существует
        assert hasattr(InvoiceReason, 'PAYMENT_METHOD_REBIND')
        assert InvoiceReason.PAYMENT_METHOD_REBIND.value == "payment_method_rebind"
        
        # Проверяем все возможные значения
        expected_values = ["initial", "renewal", "payment_method_rebind"]
        actual_values = [reason.value for reason in InvoiceReason]
        assert set(expected_values) == set(actual_values)
