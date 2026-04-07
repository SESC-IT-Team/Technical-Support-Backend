import uuid
from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sesc_auth_sdk.dependencies import LyceumAuth
from sesc_auth_sdk.enums.role import Role
from sesc_auth_sdk.schemas.user import JwtUserSchema
from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import Role as Subrole
from src.database.session import get_db
from src.users.user_model import User


class TechSupportUser(JwtUserSchema):
    subrole: Subrole
    head_of_department_id: uuid.UUID


class TechSupportAuth(LyceumAuth):
    def __init__(self, allowed_roles: Optional[list[Role]] = None):
        if allowed_roles is None:
            allowed_roles = [Role.admin, Role.teacher, Role.staff]
        else:
            try:
                allowed_roles.remove(Role.student)
            except ValueError:
                pass

        super().__init__(allowed_roles)

    async def __call__(self, jwt_user: JwtUserSchema = Depends(LyceumAuth.verify_authorized), db: AsyncSession = Depends(get_db)) -> TechSupportUser:
        user = await super().__call__(jwt_user)

        stmt = select(User).where(User.id == user.id)
        result = await db.execute(stmt)
        db_user = result.first()

        subrole = getattr(db_user, 'subrole') if db_user else Subrole.USER
        department = getattr(db_user, 'head_of_department_id') if db_user else None
        ts_user = TechSupportUser(id=user.id, role=user.role, permissions=user.permissions,
                                      subrole=subrole,
                                      head_of_department_id=department)

        return ts_user
