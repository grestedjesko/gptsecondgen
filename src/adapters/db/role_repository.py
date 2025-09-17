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
    async def get_role_details(role_id: int, session: AsyncSession):
        """Get full role details: name, description, prompt"""
        result = await session.execute(
            sa.select(AiRoles.name, AiRoles.description, AiRoles.prompt).where(AiRoles.id == role_id)
        )
        return result.first()

    @staticmethod
    async def update_selected_role(user_id: int, selected_role: int, session: AsyncSession):
        query = sa.update(UserRoles).values(role_id=selected_role).where(UserRoles.user_id == user_id)
        await session.execute(query)
        await session.commit()

    @staticmethod
    async def exists_by_user_and_title(user_id: int, title: str, session: AsyncSession):
        query = sa.select(AiRoles).where(AiRoles.user_id == user_id, AiRoles.name == title)
        result = await session.execute(query)
        res = result.scalar_one_or_none()
        return res is not None

    @staticmethod
    async def create(user_id: int, name: str, description: str, prompt: str, session: AsyncSession):
        user_role = AiRoles(user_id=user_id, name=name, description=description, prompt=prompt)
        session.add(user_role)
        await session.flush()
        await session.commit()
        return user_role

    @staticmethod
    async def get_custom_roles(user_id: int, session: AsyncSession):
        query = sa.select(AiRoles).where(AiRoles.user_id == user_id)
        result = await session.execute(query)
        res = result.scalars().all()
        return res

    @staticmethod
    async def delete_role(user_id: int, role_id: int, session: AsyncSession) -> bool:
        """Deletes a role owned by user. Returns True if deleted.

        Does not allow deleting default roles (user_id != owner).
        Also clears selection for users pointing to this role.
        """
        # Ensure the role belongs to the user
        role_query = sa.select(AiRoles).where(AiRoles.id == role_id, AiRoles.user_id == user_id)
        role_result = await session.execute(role_query)
        role = role_result.scalar_one_or_none()
        if role is None:
            return False

        # Unset this role for the owner if selected
        unset_stmt = sa.update(UserRoles).values(role_id=1).where(
            UserRoles.user_id == user_id, UserRoles.role_id == role_id
        )
        await session.execute(unset_stmt)

        # Delete the role
        delete_stmt = sa.delete(AiRoles).where(AiRoles.id == role_id, AiRoles.user_id == user_id)
        await session.execute(delete_stmt)
        await session.commit()
        return True