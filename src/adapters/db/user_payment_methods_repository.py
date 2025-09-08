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