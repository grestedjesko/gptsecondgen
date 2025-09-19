from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.db.subs_repository import SubsRepository
from src.adapters.db.invoice_repository import InvoiceRepository
from src.adapters.db.payment_repository import PaymentRepository
from src.adapters.db.user_payment_methods_repository import UserPaymentMethodsRepository
from src.adapters.db.user_subs_repository import UserSubsRepository
from src.adapters.payments.yookassa_api import YookassaCancelationReasons
from app.db.models.payments import PaymentStatus
from app.db.models.user_subs import SubscriptionStatus
from app.enums import YookassaPaymentStatus
from src.services.subscription import SubscriptionService
from app.db.models.invoice import InvoiceReason, InvoiceStatus
from datetime import timedelta
from aiogram import Bot


class HandlePaymentUseCase:
    @staticmethod
    async def handle_payment(data, session: AsyncSession, bot: Bot):
        print(f'Received webhook: {data}')
        payment_data = data.get('object', {})
        payment_status = payment_data.get('status')
        yookassa_payment_id = payment_data.get('id')
        amount = payment_data.get('amount')
        value = amount.get('value')
        print(f'Payment status: {payment_status}, amount: {value}')
        if payment_status == YookassaPaymentStatus.WAITING_FOR_CAPTURE.value:
            return 200

        if payment_status == YookassaPaymentStatus.CANCELED.value:
            cancelation_details = payment_data.get('cancelation_details')
            reason = cancelation_details.get('reason')

            norm_cancel_reasons_list = [
                YookassaCancelationReasons.INSUFFICIENT_FUNDS.value,
                YookassaCancelationReasons.INTERNAL_TIMEOUT.value,
                YookassaCancelationReasons.PAYMENT_METHOD_LIMIT_EXCEEDED.value
            ]

            payment = await PaymentRepository.get(provider_payment_id=yookassa_payment_id, session=session)
            if not payment:
                return 400

            invoice = await InvoiceRepository.get(invoice_id=payment.invoice_id, session=session)
            if not invoice:
                return 400

            user_subs = await UserSubsRepository.get_by_id(subs_id=invoice.user_subs_id, session=session)

            if reason not in norm_cancel_reasons_list:
                if user_subs:
                    user_subs.status = SubscriptionStatus.EXPIRED
                    await session.commit()
                return

            payment.status = PaymentStatus.CANCELED

            if not user_subs:
                await session.commit()
                return

            count_retries = await PaymentRepository.count_payments_retries(invoice_id=payment.invoice_id,
                                                                           session=session)
            intervals = [
                (0, 12), (0, 10), (0, 12), (0, 10), (0, 12), (0, 10),
                (1, 12), (1, 10), (1, 12), (1, 10), (2, 12), (2, 10)
            ]

            if count_retries < len(intervals):
                days, hours = intervals[count_retries]
                user_subs.renews_at = payment.renews_at + timedelta(days=days, hours=hours)
                await session.commit()
            else:
                user_subs.status = SubscriptionStatus.EXPIRED
                await session.commit()

        if payment_status == YookassaPaymentStatus.SUCCEEDED.value:
            print('Processing SUCCEEDED payment')
            is_reccuring = False
            payment_method_id = None
            title = None

            payment_method = payment_data.get('payment_method')
            print(f'Payment method: {payment_method}')
            if payment_method and payment_method.get('saved'):
                is_reccuring = True
                payment_method_id = payment_method.get('id')
                title = payment_method.get('title')
                print(f'Recurring payment: id={payment_method_id}, title={title}')

            payment = await PaymentRepository.get(provider_payment_id=yookassa_payment_id,
                                                  session=session)
            if not payment:
                return 400

            if float(payment.amount) != float(value):
                return 400

            invoice = await InvoiceRepository.get(invoice_id=payment.invoice_id, session=session)
            print(f'Invoice found: id={invoice.id}, reason={invoice.reason}, user_subs_id={invoice.user_subs_id}')

            subs = await SubsRepository.get_subs_info(subs_id=invoice.subs_id, session=session)
            if not subs:
                raise ValueError(f"Тариф с id={invoice.subs_id} не найден")

            saved_payment_method_id = None
            if is_reccuring:
                saved_payment_method_id = await UserPaymentMethodsRepository.save(user_id=invoice.user_id,
                                                                                  payment_id=payment_method_id,
                                                                                  title=title,
                                                                                  session=session)

            # Обработка возобновления подписки
            if invoice.reason == InvoiceReason.PAYMENT_METHOD_REBIND:
                print(f'Processing rebind payment: user_id={invoice.user_id}, user_subs_id={invoice.user_subs_id}, is_reccuring={is_reccuring}')
                
                if invoice.user_subs_id:
                    # Для перепривязки всегда сохраняем способ оплаты, даже если не рекуррентный
                    if not saved_payment_method_id and is_reccuring:
                        # Если способ оплаты рекуррентный, но не был сохранен, сохраняем его
                        saved_payment_method_id = await UserPaymentMethodsRepository.save(
                            user_id=invoice.user_id,
                            payment_id=payment_method_id,
                            title=title,
                            session=session
                        )
                    
                    if saved_payment_method_id:
                        # Обновляем способ оплаты для существующей подписки
                        await UserSubsRepository.update_payment_method(
                            user_subs_id=invoice.user_subs_id,
                            payment_method_id=saved_payment_method_id,
                            session=session
                        )
                        
                        # Если способ оплаты рекуррентный, возобновляем подписку
                        if is_reccuring:
                            await UserSubsRepository.set_will_renew(
                                user_id=invoice.user_id, 
                                will_renew=True, 
                                session=session
                            )
                            success_text = '✅ Подписка успешно возобновлена с новым способом оплаты'
                        else:
                            success_text = '✅ Способ оплаты обновлен, но автопродление не включено'
                    else:
                        success_text = '✅ Подписка возобновлена, но способ оплаты не был сохранен'
                    
                    await bot.edit_message_text(
                        chat_id=invoice.user_id, 
                        message_id=invoice.message_id, 
                        text=success_text
                    )
                else:
                    print(f'Error: user_subs_id is None for rebind payment')
                    await bot.edit_message_text(
                        chat_id=invoice.user_id, 
                        message_id=invoice.message_id, 
                        text='❌ Ошибка при возобновлении подписки'
                    )
            else:
                # Обычная обработка подписки
                anchor_payment_id = None
                if invoice.cycle_index == 0 and invoice.reason == InvoiceReason.INITIAL:
                    anchor_payment_id = payment.id

                await SubscriptionService.give_or_extend_subscription(subs=subs,
                                                                      user_id=invoice.user_id,
                                                                      will_renew=is_reccuring,
                                                                      saved_payment_method=saved_payment_method_id,
                                                                      anchor_payment_id=anchor_payment_id,
                                                                      session=session)

            invoice.status = InvoiceStatus.PAID
            payment.status = PaymentStatus.SUCCEEDED

            # Показываем сообщение об успешной оплате только для обычных подписок
            if invoice.reason != InvoiceReason.PAYMENT_METHOD_REBIND:
                await bot.edit_message_text(chat_id=invoice.user_id, message_id=invoice.message_id, text='Подписка успешно подключена')

            await session.commit()

        return 200