from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.db.dialog_repository import DialogRepository
from src.use_cases.usecases import UseCases
from src.adapters.db.chat_history_repository import ChatHistoryRepository
import asyncio

command_router = Router()

@command_router.message(Command('settings'))
async def settings(message: types.Message, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.settings.run(user_id=message.from_user.id, session=session, user=message.from_user)
    await message.answer(text=text, reply_markup=kbd)   


@command_router.message(Command('start'))
async def start_menu(message: types.Message, session: AsyncSession, usecases: UseCases):
    text, kb = await usecases.start_menu.run(user_id=message.from_user.id,
                                             session=session,
                                             user=message.from_user)
    await message.answer(text, reply_markup=kb, parse_mode='html')


@command_router.message(Command('select_ai'))
async def select_ai(message: types.Message, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.select_ai.show_menu(user_id=message.from_user.id, session=session, user=message.from_user)
    try:
        await message.answer(text=text, reply_markup=kbd)
    except Exception as e:
        print(e)


@command_router.message(Command('select_role'))
async def select_role(message: types.Message, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.role.show_menu(user_id=message.from_user.id, session=session, user=message.from_user, page=0)
    await message.answer(text=text, reply_markup=kbd)


@command_router.message(Command('profile'))
async def profile(message: types.Message, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.profile.run(user_id=message.from_user.id, session=session, user=message.from_user)
    await message.answer(text=text, reply_markup=kbd, parse_mode='html')


@command_router.message(Command('clear_history'))
async def clear_history(message: types.Message, session: AsyncSession):
    await message.delete()

    last_dialog = await DialogRepository.get_last(user_id=message.from_user.id, session=session)
    if last_dialog:
        await DialogRepository.end(dialog_id=last_dialog.id, user_id=message.from_user.id, session=session)
        await session.commit()
    msg = await message.answer('''История диалога очищена

Это сообщение удалится само через несколько секунд!''')

    await asyncio.sleep(2)
    await msg.delete()


@command_router.message(Command('policy'))
async def policy(message: types.Message, session: AsyncSession, usecases: UseCases):
    pass