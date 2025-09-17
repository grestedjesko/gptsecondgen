from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.cache.redis_cache import RedisCache
from src.adapters.db.user_subs_repository import UserSubsRepository
from bot.keyboards.keyboards import Keyboard
from src.adapters.db.role_repository import RoleRepository
import config.texts as texts
from bot.states import RoleCreation


TITLE_MIN, TITLE_MAX = 2, 64
TEXT_MIN, TEXT_MAX   = 10, 600

def _norm(s: str) -> str:
    return (s or "").strip()

def _len_ok(s: str, lo: int, hi: int) -> bool:
    return lo <= len(s) <= hi

async def _require_title(state: FSMContext) -> str | None:
    """Проверяем, что в FSM есть title; если нет — очищаем и возвращаем текст-ошибку."""
    data = await state.get_data()
    if not data.get("title"):
        await state.clear()
        return texts.ROLE_MSG_RESET
    return None

class RoleUseCase:
    def __init__(self, redis: RedisCache, keyboard: Keyboard):
        self.redis = redis
        self.keyboard = keyboard

    async def show_menu(self, user_id: int, session: AsyncSession, page: int = 0):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                         session=session,
                                                         redis=self.redis)

        roles = await RoleRepository.get_roles(user_id=user_id, include_defaults=True, session=session)
        selected = await RoleRepository.get_selected_role_id(user_id=user_id, session=session)
        description = await RoleRepository.get_role_description(role_id=selected, session=session)

        text = texts.select_role_text % description
        kbd = self.keyboard.role_keyboard(user_id=user_id,
                                          roles_list=roles,
                                          selected_role_id=selected, subtype=subtype, page=page)
        return text, kbd

    async def set(self, user_id: int, role_id: int, session: AsyncSession):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id,
                                                         session=session,
                                                         redis=self.redis)

        roles = await RoleRepository.get_roles(user_id=user_id, include_defaults=True, session=session)
        roles_available = RoleUseCase.get_ids_roles_available(roles=roles, subtype_id=subtype)

        description = await RoleRepository.get_role_description(role_id=role_id, session=session)
        if not role_id in roles_available:
            text = texts.subs_role_text % description
            trial_used = True
            kbd = self.keyboard.role_subs_keyboard(trial_used=trial_used)
            return text, kbd

        await RoleRepository.update_selected_role(user_id=user_id,
                                                  selected_role=role_id,
                                                  session=session)

        text = texts.select_role_text % description
        kbd = Keyboard.role_keyboard(user_id=user_id,
                                     roles_list=roles,
                                     selected_role_id=role_id,
                                     subtype=subtype)
        return text, kbd

    async def start_role_creation(self, user_id: int, session: AsyncSession, state: FSMContext):
        subtype = await UserSubsRepository.get_subs_type(user_id=user_id, session=session, redis=self.redis)

        if subtype == 0:
            trial_used = await UserSubsRepository.get_trial_used(user_id=user_id, session=session)
            text = texts.create_role_subs_text
            kbd = self.keyboard.role_subs_keyboard(trial_used=trial_used)
            return text, kbd

        existing = await RoleRepository.get_custom_roles(user_id=user_id, session=session)
        if len(existing) >= 5:
            kbd = Keyboard.custom_role_keyboard(roles=existing)
            return texts.ROLE_LIMIT_REACHED, kbd

        text = texts.ROLE_ASK_TITLE
        kbd = self.keyboard.cancel_keyboard()
        await state.set_state(RoleCreation.waiting_for_title)
        return text, kbd


    async def set_role_name(self, user_id: int, session: AsyncSession, state: FSMContext, title: str):
        title = _norm(title)
        if not _len_ok(title, TITLE_MIN, TITLE_MAX):
            return texts.ROLE_MSG_TITLE_LEN

        if await RoleRepository.exists_by_user_and_title(user_id=user_id, title=title, session=session):
            return texts.ROLE_MSG_TITLE_EXISTS

        await state.update_data(title=title)
        await state.set_state(RoleCreation.waiting_for_description)
        return texts.ROLE_MSG_ASK_DESC


    async def set_role_description(self, state: FSMContext, description: str):
        if description == "/skip":
            await state.update_data(description=None)
            await state.set_state(RoleCreation.waiting_for_prompt)
            return texts.ROLE_MSG_ASK_PROMPT

        description = _norm(description)
        if not _len_ok(description, TEXT_MIN, TEXT_MAX):
            return texts.ROLE_MSG_DESC_LEN

        if (err := await _require_title(state)):
            return err

        await state.update_data(description=description)
        await state.set_state(RoleCreation.waiting_for_prompt)
        return texts.ROLE_MSG_ASK_PROMPT


    async def set_role_prompt(self, user_id: int, session: AsyncSession, state: FSMContext, prompt: str):
        prompt = _norm(prompt)
        if not _len_ok(prompt, TEXT_MIN, TEXT_MAX):
            return texts.ROLE_MSG_PROMPT_LEN

        if (err := await _require_title(state)):
            return err

        data = await state.get_data()
        name = data["title"]
        description = data.get("description") or "Пользовательская роль"

        role = await RoleRepository.create(
            user_id=user_id,
            name=name,
            description=description,
            prompt=prompt,
            session=session,
        )
        await RoleRepository.update_selected_role(
            user_id=user_id, selected_role=role.id, session=session
        )
        await session.commit()
        await state.clear()
        return await self.show_menu(user_id=user_id, session=session)

    @staticmethod
    def get_ids_roles_available(roles: list, subtype_id: int) -> list[int]:
        if subtype_id == 0:
            return [role.id for role in roles if role.free_available]
        return [role.id for role in roles]


    async def show_custom(self, user_id: int, session: AsyncSession):
        custom_roles = await RoleRepository.get_custom_roles(user_id=user_id, session=session)
        text = texts.ROLE_CUSTOM_LIST
        kbd = Keyboard.custom_role_keyboard(roles=custom_roles)
        return text, kbd

    async def show_settings(self, user_id: int, role_id: int, session: AsyncSession):
        role_details = await RoleRepository.get_role_details(role_id=role_id, session=session)
        if not role_details:
            return "Роль не найдена", Keyboard.custom_role_keyboard(roles=await RoleRepository.get_custom_roles(user_id=user_id, session=session))
        
        name, description, prompt = role_details
        text = f"<b>📝 {name}</b>\n\n<b>📋 Описание:</b>\n{description or 'Не указано'}\n\n<b>🤖 Промпт:</b>\n{prompt or 'Не указано'}"
        kbd = Keyboard.role_settings_keyboard(role_id=role_id)
        return text, kbd

    async def delete(self, user_id: int, role_id: int, session: AsyncSession):
        deleted = await RoleRepository.delete_role(user_id=user_id, role_id=role_id, session=session)
        if not deleted:
            return texts.ROLE_CANNOT_DELETE, Keyboard.custom_role_keyboard(roles=await RoleRepository.get_custom_roles(user_id=user_id, session=session))
 
        return await self.show_custom(user_id=user_id, session=session)