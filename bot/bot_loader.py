from aiogram import Dispatcher
from bot.handlers import callback_handlers, checkout_handlers, command_handlers, message_handlers, role_handlers
from bot.middlewares.auth_middleware import AuthMiddleware
from bot.middlewares.db_middleware import DbSessionMiddleware

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

def register_handlers(dp: Dispatcher, session_factory: async_sessionmaker[AsyncSession]):
    dp.update.middleware(DbSessionMiddleware(session_factory=session_factory))
    dp.update.middleware(AuthMiddleware())

    dp.include_router(checkout_handlers.router)
    dp.include_router(callback_handlers.callback_router)
    dp.include_router(command_handlers.command_router)
    dp.include_router(role_handlers.role_router)
    dp.include_router(message_handlers.message_router)

