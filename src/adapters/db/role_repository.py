import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from app.db.models import UserRoles, AiRoles


class RoleRepository:
    @staticmethod
    async def get_roles(session: AsyncSession, user_id: int = None, include_defaults: bool = False):
        filters = []
        if include_defaults:
            filters.append(AiRoles.user_id == 1)
        if user_id is not None:
            filters.append(AiRoles.user_id == user_id)

        if filters:
            stmt = sa.select(AiRoles.id, AiRoles.name, AiRoles.user_id, AiRoles.free_available).where(
                or_(*filters)
            )
        else:
            stmt = sa.select(AiRoles.id, AiRoles.name, AiRoles.user_id, AiRoles.free_available)

        result = await session.execute(stmt)
        return result.fetchall()

    @staticmethod
    async def get_selected_role_id(user_id: int, session: AsyncSession) -> int | None:
        query = sa.select(UserRoles.role_id).where(UserRoles.user_id == user_id)
        result = await session.execute(query)
        res = result.scalar_one_or_none()
        return res if res else 1

    @staticmethod
    async def get_role_description(role_id: int, session: AsyncSession) -> str | None:
        result = await session.execute(
            sa.select(AiRoles.description).where(AiRoles.id == role_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_role_prompt(role_id: int, session: AsyncSession) -> str | None:
        result = await session.execute(
            sa.select(AiRoles.prompt).where(AiRoles.id == role_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_selected_role(user_id: int, selected_role: int, session: AsyncSession):
        query = sa.update(UserRoles).values(role_id=selected_role).where(UserRoles.user_id == user_id)
        await session.execute(query)
        await session.commit()