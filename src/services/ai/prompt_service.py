from sqlalchemy.ext.asyncio import AsyncSession
from src.adapters.db.role_repository import RoleRepository
from config.texts import default_prompt

class PromptService:
    @staticmethod
    async def get_prompt(user_id: int, session: AsyncSession) -> str:
        role_id = await RoleRepository.get_selected_role_id(user_id, session)
        if not role_id:
            return default_prompt

        prompt = await RoleRepository.get_role_prompt(role_id, session)
        return prompt or default_prompt