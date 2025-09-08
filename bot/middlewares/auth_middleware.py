from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any
from aiogram.types import Update

from src.adapters.db.user_repository import UserRepository

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        session = data['session']

        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        elif event.pre_checkout_query:
            user = event.pre_checkout_query.from_user

        if not user:
            return 404

        user_in_base = await UserRepository.get_by_id(user_id=user.id, session=session)
        if not user_in_base:
            await UserRepository.create_user(user=user, session=session)
            # send first message
            # todo -> usecase
            return 200

        return await handler(event, data)