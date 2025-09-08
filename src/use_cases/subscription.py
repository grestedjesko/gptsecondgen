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

