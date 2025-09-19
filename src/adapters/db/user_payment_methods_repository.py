import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import UserPaymentMethod

class UserPaymentMethodsRepository:
    @staticmethod
    async def save(user_id: int,
                   payment_id: int,
                   title: str,
                   session: AsyncSession):
        payment_method = UserPaymentMethod(user_id=user_id,
                                           payment_method_id=payment_id,
                                           title=title)
        session.add(payment_method)

        await session.flush()
        await session.commit()
        return payment_method.id

    @staticmethod
    async def get_payment_method_id(payment_method_id: int, session: AsyncSession):
        result = await session.execute(
            sa.select(UserPaymentMethod.payment_method_id).where(UserPaymentMethod.id == payment_method_id))
        payment_method_id = result.scalar_one_or_none()
        return payment_method_id

    @staticmethod
    async def delete_by_id(payment_method_id: int, session: AsyncSession):
        """Удаляет способ оплаты по ID"""
        await session.execute(
            sa.delete(UserPaymentMethod).where(UserPaymentMethod.id == payment_method_id)
        )
        await session.commit()

    @staticmethod
    async def delete_by_user_id(user_id: int, session: AsyncSession):
        """Удаляет все способы оплаты пользователя"""
        await session.execute(
            sa.delete(UserPaymentMethod).where(UserPaymentMethod.user_id == user_id)
        )
        await session.commit()

    @staticmethod
    async def get_by_user_id(user_id: int, session: AsyncSession):
        """Получает все способы оплаты пользователя"""
        result = await session.execute(
            sa.select(UserPaymentMethod).where(UserPaymentMethod.user_id == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def clear_payment_method_id(payment_method_id: int, session: AsyncSession):
        """Обнуляет payment_method_id в записи способа оплаты"""
        await session.execute(
            sa.update(UserPaymentMethod)
            .where(UserPaymentMethod.id == payment_method_id)
            .values(payment_method_id=None)
        )
        await session.commit()