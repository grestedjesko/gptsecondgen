from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from src.use_cases.usecases import UseCases
from src.adapters.db.user_model_repository import UserModelRepository

callback_router = Router()


@callback_router.callback_query(F.data == 'select_ai')
async def select_ai(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.select_ai.show_menu(user_id=call.from_user.id, session=session, user=call.from_user)
    try:
        await call.message.edit_text(text=text, reply_markup=kbd)
    except Exception as e:
        print(e)


@callback_router.callback_query(F.data.startswith("set_model:"))
async def set_model(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    _, mid_str = call.data.split(":")
    model_id = int(mid_str)

    selected = await UserModelRepository.get_selected_model_id(user_id=call.from_user.id, session=session)
    if selected == model_id:
        await call.answer('Модель уже выбрана')
        return

    text, kbd = await usecases.select_ai.set(user_id=call.from_user.id, model_id=model_id, session=session, user=call.from_user)
    try:
        await call.message.edit_text(text=text, reply_markup=kbd)
        await call.answer()
    except Exception as e:
        print(e)


@callback_router.callback_query(F.data == 'select_role')
async def select_role(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.role.show_menu(user_id=call.from_user.id, session=session, user=call.from_user, page=0)
    await call.message.edit_text(text=text, reply_markup=kbd)


@callback_router.callback_query(F.data.startswith('roles_page:'))
async def roles_page(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    _, page_str = call.data.split(':')
    page = int(page_str)
    text, kbd = await usecases.role.show_menu(user_id=call.from_user.id, session=session, user=call.from_user, page=page)
    await call.message.edit_text(text=text, reply_markup=kbd)


@callback_router.callback_query(F.data.startswith("set_role:"))
async def set_role(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    _, role_id = call.data.split(":")
    role_id = int(role_id)
    text, kbd = await usecases.role.set(user_id=call.from_user.id,
                                        role_id=role_id,
                                        session=session,
                                        user=call.from_user)
    try:
        await call.message.edit_text(text=text, reply_markup=kbd)
    except Exception as e:
        print(e)


@callback_router.callback_query(F.data == 'custom_roles')
async def edit_roles(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.role.show_custom(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd)


@callback_router.callback_query(F.data == 'create_role')
async def create_role(call: CallbackQuery, session:AsyncSession, usecases: UseCases, state: FSMContext):
    text, kbd = await usecases.role.start_role_creation(user_id=call.from_user.id,
                                                        session=session,
                                                        state=state,
                                                        user=call.from_user)
    await call.message.delete()
    await call.message.answer(text=text, reply_markup=kbd)


@callback_router.callback_query(F.data.contains('settings_role_id='))
async def role_settings(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    # callback_data is like 'settings_role_id=123'
    role_id = int(call.data.split('=')[1])
    text, kbd = await usecases.role.show_settings(user_id=call.from_user.id,
                                                  role_id=role_id,
                                                  session=session,
                                                  user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data.contains('delete_role_id='))
async def delete_role(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    role_id = int(call.data.split('=')[1])
    text, kbd = await usecases.role.delete(user_id=call.from_user.id,
                                           role_id=role_id,
                                           session=session,
                                           user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd)


@callback_router.callback_query(F.data == 'main_menu')
async def main_menu(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.start_menu.run(user_id=call.from_user.id,
                                              session=session,
                                              user=call.from_user)
    await call.message.edit_text(text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'profile')
async def profile(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.profile.run(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'settings_subs')
async def settings_subs(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.show_settings(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'subs_stop_renew')
async def subs_stop_renew(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.stop_renew(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'subs_extend')
async def subs_extend(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.enable_renew(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'subs_list')
async def subs_list(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.show_subs_menu(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'extend_subs')
async def extend_subs(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.show_extend_subs_menu(user_id=call.from_user.id, session=session, user=call.from_user)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'rebind_payment_method')
async def rebind_payment_method(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.rebind_payment_method(call=call, session=session)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data.startswith('subs_id='))
async def subs_id(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    subs_id = int(call.data.replace('subs_id=', ''))
    if subs_id == 1:
        await start_trial(call, session, usecases)
        return

    text, kbd = await usecases.subscription.generate_payment(call=call, subs_id=subs_id, session=session)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')


@callback_router.callback_query(F.data == 'start_trial')
async def start_trial(call: CallbackQuery, session: AsyncSession, usecases: UseCases):
    text, kbd = await usecases.subscription.generate_payment(call=call, subs_id=1, session=session)
    await call.message.edit_text(text=text, reply_markup=kbd, parse_mode='html')