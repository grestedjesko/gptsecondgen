import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.use_cases.subscription import SubscriptionUseCase
from src.adapters.cache.redis_cache import RedisCache
from bot.keyboards.keyboards import Keyboard
from src.adapters.payments.yookassa_api import YookassaAPI


class TestPaymentMethodDeletion:
    """Тесты для удаления способа оплаты при отключении автопродления"""
    
    @pytest.mark.asyncio
    async def test_stop_renew_with_payment_method(self):
        """Тест отключения автопродления с удалением способа оплаты"""
        # Мок объекты
        mock_redis = Mock(spec=RedisCache)
        mock_keyboard = Mock(spec=Keyboard)
        mock_yookassa = Mock(spec=YookassaAPI)
        
        # Создаем use case
        use_case = SubscriptionUseCase(
            redis=mock_redis,
            keyboard=mock_keyboard,
            yookassa=mock_yookassa
        )
        
        # Мок сессии
        mock_session = AsyncMock()
        
        # Мок подписки с привязанным способом оплаты
        mock_user_subs = Mock()
        mock_user_subs.id = 123
        mock_user_subs.payment_method = 456
        
        # Мок репозиториев
        with patch('src.use_cases.subscription.UserSubsRepository') as mock_user_subs_repo, \
             patch('src.use_cases.subscription.UserPaymentMethodsRepository') as mock_payment_methods_repo:
            
            # Настраиваем моки
            mock_user_subs_repo.get_subs_by_user_id.return_value = mock_user_subs
            mock_user_subs_repo.set_will_renew = AsyncMock()
            mock_payment_methods_repo.clear_payment_method_id = AsyncMock()
            
            # Мок для show_settings
            mock_keyboard.subs_settings_keyboard.return_value = Mock()
            with patch.object(use_case, 'show_settings', return_value=("text", "keyboard")):
                # Вызываем метод
                result = await use_case.stop_renew(user_id=789, session=mock_session)
                
                # Проверяем результат
                assert result == ("text", "keyboard")
                
                # Проверяем, что были вызваны нужные методы
                mock_user_subs_repo.get_subs_by_user_id.assert_called_once_with(
                    user_id=789, session=mock_session
                )
                mock_user_subs_repo.set_will_renew.assert_called_once_with(
                    user_id=789, will_renew=False, session=mock_session
                )
                mock_payment_methods_repo.clear_payment_method_id.assert_called_once_with(
                    payment_method_id=456, session=mock_session
                )
    
    @pytest.mark.asyncio
    async def test_stop_renew_without_payment_method(self):
        """Тест отключения автопродления без способа оплаты"""
        # Мок объекты
        mock_redis = Mock(spec=RedisCache)
        mock_keyboard = Mock(spec=Keyboard)
        mock_yookassa = Mock(spec=YookassaAPI)
        
        # Создаем use case
        use_case = SubscriptionUseCase(
            redis=mock_redis,
            keyboard=mock_keyboard,
            yookassa=mock_yookassa
        )
        
        # Мок сессии
        mock_session = AsyncMock()
        
        # Мок подписки без способа оплаты
        mock_user_subs = Mock()
        mock_user_subs.id = 123
        mock_user_subs.payment_method = None
        
        # Мок репозиториев
        with patch('src.use_cases.subscription.UserSubsRepository') as mock_user_subs_repo, \
             patch('src.use_cases.subscription.UserPaymentMethodsRepository') as mock_payment_methods_repo:
            
            # Настраиваем моки
            mock_user_subs_repo.get_subs_by_user_id.return_value = mock_user_subs
            mock_user_subs_repo.set_will_renew = AsyncMock()
            mock_payment_methods_repo.clear_payment_method_id = AsyncMock()
            
            # Мок для show_settings
            with patch.object(use_case, 'show_settings', return_value=("text", "keyboard")):
                # Вызываем метод
                result = await use_case.stop_renew(user_id=789, session=mock_session)
                
                # Проверяем результат
                assert result == ("text", "keyboard")
                
                # Проверяем, что payment_method_id НЕ был обнулен
                mock_payment_methods_repo.clear_payment_method_id.assert_not_called()
                
                # Проверяем, что автопродление было отключено
                mock_user_subs_repo.set_will_renew.assert_called_once_with(
                    user_id=789, will_renew=False, session=mock_session
                )
    
    @pytest.mark.asyncio
    async def test_stop_renew_without_subs(self):
        """Тест отключения автопродления без активной подписки"""
        # Мок объекты
        mock_redis = Mock(spec=RedisCache)
        mock_keyboard = Mock(spec=Keyboard)
        mock_yookassa = Mock(spec=YookassaAPI)
        
        # Создаем use case
        use_case = SubscriptionUseCase(
            redis=mock_redis,
            keyboard=mock_keyboard,
            yookassa=mock_yookassa
        )
        
        # Мок сессии
        mock_session = AsyncMock()
        
        # Мок репозиториев
        with patch('src.use_cases.subscription.UserSubsRepository') as mock_user_subs_repo, \
             patch('src.use_cases.subscription.UserPaymentMethodsRepository') as mock_payment_methods_repo:
            
            # Настраиваем моки - нет активной подписки
            mock_user_subs_repo.get_subs_by_user_id.return_value = None
            mock_user_subs_repo.set_will_renew = AsyncMock()
            mock_payment_methods_repo.delete_by_id = AsyncMock()
            
            # Мок для show_settings
            with patch.object(use_case, 'show_settings', return_value=("text", "keyboard")):
                # Вызываем метод
                result = await use_case.stop_renew(user_id=789, session=mock_session)
                
                # Проверяем результат
                assert result == ("text", "keyboard")
                
                # Проверяем, что payment_method_id НЕ был обнулен
                mock_payment_methods_repo.clear_payment_method_id.assert_not_called()
                
                # Проверяем, что автопродление было отключено
                mock_user_subs_repo.set_will_renew.assert_called_once_with(
                    user_id=789, will_renew=False, session=mock_session
                )
