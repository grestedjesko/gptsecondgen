from aiogram.types import CallbackQuery
from aiogram.types import LabeledPrice
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.db.invoice_repository import InvoiceRepository
from src.adapters.db.payment_repository import PaymentRepository
from src.adapters.db.subs_repository import SubsRepository
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.payments.yookassa_api import YookassaAPI
from app.db.models.invoice import InvoiceReason, InvoiceStatus
from app.db.models.payments import PaymentProvider, PaymentStatus
from config.texts import subscribe_trial_text, base_subs_text, subscribe_text
from bot.keyboards.keyboards import Keyboard
from src.adapters.db.user_subs_repository import UserSubsRepository
from src.adapters.db.user_payment_methods_repository import UserPaymentMethodsRepository



class SubscriptionUseCase:
    def __init__(self, redis: RedisCache, keyboard: Keyboard, yookassa: YookassaAPI):
        self.redis = redis
        self.keyboard = keyboard
        self.yookassa = yookassa

    async def show_subs_menu(self, user_id: int, session: AsyncSession):
        text = base_subs_text
        trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)

        available_subs = []

        all_subs = await SubsRepository.get_all_subs(session=session, redis=self.redis)
        for sub in all_subs:
            if sub.id == 1 and trial_used:
                continue
            available_subs.append(sub)

        keyboard = Keyboard.subs_keyboard(available_subs=available_subs)

        return text, keyboard

    async def show_extend_subs_menu(self, user_id: int, session: AsyncSession):
        text = base_subs_text
        trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)

        available_subs = []

        all_subs = await SubsRepository.get_all_subs(session=session, redis=self.redis)
        for sub in all_subs:
            if sub.id == 1 and trial_used:
                continue
            available_subs.append(sub)

        keyboard = Keyboard.subs_extend_keyboard(available_subs=available_subs)

        return text, keyboard

    async def show_settings(self, user_id: int, session: AsyncSession):
        subs = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)
        will_renew = bool(subs and subs.will_renew)
        text = "Управление подпиской"
        kbd = Keyboard.subs_settings_keyboard(will_renew=will_renew)
        return text, kbd

    async def stop_renew(self, user_id: int, session: AsyncSession):
        # Получаем активную подписку пользователя
        user_subs = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)
        
        # Отключаем автопродление
        await UserSubsRepository.set_will_renew(user_id=user_id, will_renew=False, session=session)
        
        # Если у подписки есть привязанный способ оплаты, обнуляем payment_method_id в user_payment_methods
        if user_subs and user_subs.payment_method:
            print(f'Clearing payment_method_id for payment method {user_subs.payment_method} for user {user_id}')
            # Обнуляем payment_method_id в таблице user_payment_methods, но оставляем ссылку в user_subs
            await UserPaymentMethodsRepository.clear_payment_method_id(
                payment_method_id=user_subs.payment_method,
                session=session
            )
        
        await session.commit()
        return await self.show_settings(user_id=user_id, session=session)

    async def enable_renew(self, user_id: int, session: AsyncSession):
        await UserSubsRepository.set_will_renew(user_id=user_id, will_renew=True, session=session)
        await session.commit()
        return await self.show_settings(user_id=user_id, session=session)

    async def rebind_payment_method(self, call: CallbackQuery, session: AsyncSession):
        """Создает счет на 1 рубль для перепривязки способа оплаты"""
        user_id = call.from_user.id
        
        # Получаем активную подписку пользователя
        user_subs = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)
        if not user_subs:
            return "У вас нет активной подписки", self.keyboard.subs_settings_keyboard(will_renew=False)
        
        # Создаем счет на 1 рубль для перепривязки
        invoice = await InvoiceRepository.create(
            user_id=user_id,
            subs_id=user_subs.subs_id,
            session=session,
            reason=InvoiceReason.PAYMENT_METHOD_REBIND,
            status=InvoiceStatus.CREATED,
            user_subs_id=user_subs.id,
            message_id=call.message.message_id,
            cycle_index=None
        )
        print(f'Created rebind invoice: id={invoice.id}, user_subs_id={invoice.user_subs_id}, reason={invoice.reason}')
        
        # Создаем платеж через ЮKassa на 1 рубль
        gate_payment_id, link = self.yookassa.create_payment(
            amount=1,  # 1 рубль в копейках
            invoice_id=str(invoice.public_id),
            return_url='https://t.me/chatgpts_rubot'
        )
        print(f'Created YooKassa payment: id={gate_payment_id}, link={link}')
        
        payment_id = await PaymentRepository.create(
            invoice_id=invoice.id,
            provider_payment_id=gate_payment_id,
            amount=1,
            provider=PaymentProvider.GATEWAY,
            session=session,
            status=PaymentStatus.PENDING,
            currency='RUB'
        )
        print(f'Created payment record: id={payment_id}')
        
        text = "🔄 Возобновление подписки\n\nДля возобновления подписки необходимо оплатить 1 рубль. После успешной оплаты подписка будет возобновлена с новым способом оплаты."
        
        kbd = self.keyboard.payment_rebind_keyboard(link=link)
        return text, kbd

    async def generate_payment(self, call: CallbackQuery, subs_id: int, session: AsyncSession):
        user_id = call.from_user.id
        subs = await SubsRepository.get_subs_info(subs_id=subs_id, session=session)
        amount, stars_amount, period = subs.price, subs.stars_price, subs.period

        if subs_id == 1:
            text = subscribe_trial_text
        else:
            text = subscribe_text


        invoice = await InvoiceRepository.create(user_id=user_id,
                                                 subs_id=subs_id,
                                                 session=session,
                                                 reason=InvoiceReason.INITIAL,
                                                 status=InvoiceStatus.CREATED,
                                                 user_subs_id=None,
                                                 message_id=call.message.message_id,
                                                 cycle_index=0)

        gate_payment_id, link = self.yookassa.create_payment(amount=amount,
                                                             invoice_id=str(invoice.public_id),
                                                             return_url='https://t.me/chatgpts_rubot')

        await PaymentRepository.create(invoice_id=invoice.id,
                                       provider_payment_id=gate_payment_id,
                                       amount=amount,
                                       provider=PaymentProvider.GATEWAY,
                                       session=session,
                                       status=PaymentStatus.PENDING,
                                       currency='RUB')

        oferta_link = 'https://www.oferta.com'

        prices = [LabeledPrice(label="XTR", amount=stars_amount)]
        title = f"⭐Подписка на {period} дн."
        if period == 30:
            invoice_link = await call.bot.create_invoice_link(
                title=title,
                description=title,
                subscription_period=2592000,
                prices=prices,
                provider_token="",
                payload=str(invoice.public_id),
                currency="XTR"
            )
        else:
            invoice_link = await call.bot.create_invoice_link(
                title=title,
                description=title,
                prices=prices,
                provider_token="",
                payload=str(invoice.public_id),
                currency="XTR"
            )

        keyboard = Keyboard.payment_keyboard(amount=amount,
                                             stars_amount=stars_amount,
                                             invoice_link=invoice_link,
                                             payment_link=link,
                                             oferta_link=oferta_link)

        return text, keyboard

