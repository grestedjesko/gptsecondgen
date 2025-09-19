import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.use_cases.handle_payment import HandlePaymentUseCase
from app.db.models.invoice import InvoiceReason, InvoiceStatus
from app.db.models.payments import PaymentStatus, PaymentProvider


class TestWebhookRebind:
    """Тесты для обработки webhook'а при перепривязке способа оплаты"""
    
    @pytest.mark.asyncio
    async def test_webhook_rebind_payment_success(self):
        """Тест успешной обработки webhook'а для перепривязки"""
        # Мок данные webhook'а
        webhook_data = {
            'object': {
                'id': 'test_payment_id',
                'status': 'succeeded',
                'amount': {'value': '1.00'},
                'payment_method': {
                    'saved': True,
                    'id': 'pm_test_id',
                    'title': 'Test Card'
                }
            }
        }
        
        # Мок сессии
        mock_session = AsyncMock()
        
        # Мок бота
        mock_bot = Mock()
        mock_bot.edit_message_text = AsyncMock()
        
        # Мок репозиториев
        with patch('src.use_cases.handle_payment.PaymentRepository') as mock_payment_repo, \
             patch('src.use_cases.handle_payment.InvoiceRepository') as mock_invoice_repo, \
             patch('src.use_cases.handle_payment.UserPaymentMethodsRepository') as mock_payment_methods_repo, \
             patch('src.use_cases.handle_payment.UserSubsRepository') as mock_user_subs_repo, \
             patch('src.use_cases.handle_payment.SubsRepository') as mock_subs_repo:
            
            # Настраиваем моки
            mock_payment = Mock()
            mock_payment.invoice_id = 1
            mock_payment.amount = 1
            mock_payment_repo.get.return_value = mock_payment
            
            mock_invoice = Mock()
            mock_invoice.id = 1
            mock_invoice.user_id = 123
            mock_invoice.subs_id = 1
            mock_invoice.reason = InvoiceReason.PAYMENT_METHOD_REBIND
            mock_invoice.user_subs_id = 456
            mock_invoice.message_id = 789
            mock_invoice_repo.get.return_value = mock_invoice
            
            mock_subs = Mock()
            mock_subs.id = 1
            mock_subs.subtype_id = 1
            mock_subs_repo.get_subs_info.return_value = mock_subs
            
            mock_payment_methods_repo.save.return_value = 999
            
            # Вызываем обработчик
            result = await HandlePaymentUseCase.handle_payment(
                data=webhook_data,
                session=mock_session,
                bot=mock_bot
            )
            
            # Проверяем результат
            assert result == 200
            
            # Проверяем, что были вызваны нужные методы
            mock_payment_methods_repo.save.assert_called_once()
            mock_user_subs_repo.update_payment_method.assert_called_once()
            mock_user_subs_repo.set_will_renew.assert_called_once_with(
                user_id=123,
                will_renew=True,
                session=mock_session
            )
            mock_bot.edit_message_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_webhook_rebind_payment_non_recurring(self):
        """Тест обработки webhook'а для нерекуррентного способа оплаты"""
        # Мок данные webhook'а
        webhook_data = {
            'object': {
                'id': 'test_payment_id',
                'status': 'succeeded',
                'amount': {'value': '1.00'},
                'payment_method': {
                    'saved': False,
                    'id': 'pm_test_id',
                    'title': 'Test Card'
                }
            }
        }
        
        # Мок сессии
        mock_session = AsyncMock()
        
        # Мок бота
        mock_bot = Mock()
        mock_bot.edit_message_text = AsyncMock()
        
        # Мок репозиториев
        with patch('src.use_cases.handle_payment.PaymentRepository') as mock_payment_repo, \
             patch('src.use_cases.handle_payment.InvoiceRepository') as mock_invoice_repo, \
             patch('src.use_cases.handle_payment.UserPaymentMethodsRepository') as mock_payment_methods_repo, \
             patch('src.use_cases.handle_payment.UserSubsRepository') as mock_user_subs_repo, \
             patch('src.use_cases.handle_payment.SubsRepository') as mock_subs_repo:
            
            # Настраиваем моки
            mock_payment = Mock()
            mock_payment.invoice_id = 1
            mock_payment.amount = 1
            mock_payment_repo.get.return_value = mock_payment
            
            mock_invoice = Mock()
            mock_invoice.id = 1
            mock_invoice.user_id = 123
            mock_invoice.subs_id = 1
            mock_invoice.reason = InvoiceReason.PAYMENT_METHOD_REBIND
            mock_invoice.user_subs_id = 456
            mock_invoice.message_id = 789
            mock_invoice_repo.get.return_value = mock_invoice
            
            mock_subs = Mock()
            mock_subs.id = 1
            mock_subs.subtype_id = 1
            mock_subs_repo.get_subs_info.return_value = mock_subs
            
            # Вызываем обработчик
            result = await HandlePaymentUseCase.handle_payment(
                data=webhook_data,
                session=mock_session,
                bot=mock_bot
            )
            
            # Проверяем результат
            assert result == 200
            
            # Проверяем, что способ оплаты НЕ был сохранен
            mock_payment_methods_repo.save.assert_not_called()
            
            # Проверяем, что автопродление НЕ было включено
            mock_user_subs_repo.set_will_renew.assert_not_called()
            
            # Проверяем, что сообщение было отправлено
            mock_bot.edit_message_text.assert_called_once()
