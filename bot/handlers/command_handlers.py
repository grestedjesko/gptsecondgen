from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from src.use_cases.usecases import UseCases
from src.adapters.db.chat_history_repository import ChatHistoryRepository
import asyncio

command_router = Router()


@command_router.message(Command('start'))
async def start_menu(message: types.Message, session: AsyncSession, usecases: UseCases):
    text, kb = await usecases.start_menu.run(user_id=message.from_user.id,
                                             session=session)
    await message.answer(text, reply_markup=kb, parse_mode='html')


@command_router.message(Command('clear_history'))
async def clear_history(message: types.Message, session: AsyncSession):
    await message.delete()
    msg = await message.answer('''История диалога очищена

Это сообщение удалится само через несколько секунд!''')

    await ChatHistoryRepository.clear_history(session=session, user_id=message.from_user.id)

    await asyncio.sleep(2)
    await msg.delete()