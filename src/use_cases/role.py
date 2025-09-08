from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.user_subs_repository import UserSubsRepository
from bot.keyboards.keyboards import Keyboard
from src.adapters.db.role_repository import RoleRepository
from config.texts import subs_role_text, select_role_text, create_role_subs_text, edit_roles_text
from bot.states import RoleCreation

class RoleUseCase:
    def __init__(self, redis: RedisCache, keyboard: Keyboard):
        self.redis = redis
        self.keyboard = keyboard

    async def show_menu(self, user_id: int, session: AsyncSession):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                         session=session,
                                                         redis=self.redis)

        roles = await RoleRepository.get_roles(user_id=user_id, include_defaults=True, session=session)
        selected = await RoleRepository.get_selected_role_id(user_id=user_id, session=session)
        description = await RoleRepository.get_role_description(role_id=selected, session=session)

        text = select_role_text % description
        kbd = self.keyboard.get_role_keyboard(user_id=user_id, roles_list=roles,
                                              selected_role_id=selected, subtype=subtype)
        return text, kbd

    async def set(self, user_id: int, role_id: int, session: AsyncSession):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                         session=session,
                                                         redis=self.redis)

        roles = await RoleRepository.get_roles(user_id=user_id, include_defaults=True, session=session)
        roles_available = RoleUseCase.get_ids_roles_available(roles=roles, subtype_id=subtype)

        description = await RoleRepository.get_role_description(role_id=role_id, session=session)
        if not role_id in roles_available:
            text = subs_role_text % description
            trial_used = True
            kbd = self.keyboard.role_subs_keyboard(trial_used=trial_used)
            return text, kbd

        await RoleRepository.update_selected_role(user_id=user_id,
                                                  selected_role=role_id,
                                                  session=session)

        text = select_role_text % description
        kbd = Keyboard.get_role_keyboard(user_id=user_id,
                                         roles_list=roles,
                                         selected_role_id=role_id,
                                         subtype=subtype)
        return text, kbd

    async def edit(self):
        text = edit_roles_text

    async def start_role_creation(self, user_id: int, session: AsyncSession, state: FSMContext):
        subs_info = await UserSubsRepository.get_subs_by_user_id(user_id=user_id, session=session)

        if subs_info.subtype_id == 0:
            trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)
            text = create_role_subs_text
            kbd = self.keyboard.role_subs_keyboard(trial_used=trial_used)
            return text, kbd

        text = "Введите название роли:"
        kbd = self.keyboard.cancel_keyboard()
        await state.set_state(RoleCreation.waiting_for_title)
        return text, kbd

    async def get_role_name(self):
        pass

    async def get_role_description(self):
        pass

    @staticmethod
    def get_ids_roles_available(roles: list, subtype_id: int) -> list[int]:
        if subtype_id == 0:
            return [role.id for role in roles if role.free_available]
        return [role.id for role in roles]