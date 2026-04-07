import uuid
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from user_model import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user: User):
        self.session.add(user)
        await self.session.commit()

    async def delete_user(self, user_id: uuid.UUID):
        user = await self.session.get(User, user_id)
        await self.session.delete(user)
        await self.session.commit()

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        user = await self.session.get(User, user_id)
        return user

    async def set_admin(self, user_id: uuid.UUID, department_id: uuid.UUID):
        user = await self.get_user_by_id(user_id)
        if user:
            user.head_of_department_id = department_id
        else:
            user = User(
                id = user_id,
                head_of_department_id = department_id
            )
            self.session.add(user)
        await self.session.commit()
        return user