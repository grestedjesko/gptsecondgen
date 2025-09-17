from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, ContentType
from src.use_cases.usecases import UseCases
from aiogram.utils.chat_action import ChatActionSender
from aiogram.filters import StateFilter
from bot.states import RoleCreation

role_router = Router()

@role_router.message(F.text == '❌ Отмена')
async def cancel_text(message: Message, state: FSMContext, usecases: UseCases, session: AsyncSession):
    await state.clear()
    text, kb = await usecases.start_menu.run(user_id=message.from_user.id,
                                             session=session)
    await message.answer(text, reply_markup=kb, parse_mode='html')


@role_router.message(StateFilter(RoleCreation.waiting_for_title))
async def set_role_title(message: Message, session: AsyncSession, usecases: UseCases, state: FSMContext):
    text = await usecases.role.set_role_name(user_id=message.from_user.id,
                                             session=session,
                                             state=state,
                                             title=message.text)
    await message.answer(text)


@role_router.message(StateFilter(RoleCreation.waiting_for_description))
async def set_role_description(message: Message, usecases: UseCases, state: FSMContext):
    text = await usecases.role.set_role_description(state=state,
                                                    description=message.text)
    await message.answer(text)


@role_router.message(StateFilter(RoleCreation.waiting_for_prompt))
async def set_role_prompt(message: Message, session: AsyncSession, usecases: UseCases, state: FSMContext):
    text, kbd = await usecases.role.set_role_prompt(user_id=message.from_user.id,
                                                    session=session,
                                                    state=state,
                                                    prompt=message.text)
    await message.answer(text, reply_markup=kbd)

