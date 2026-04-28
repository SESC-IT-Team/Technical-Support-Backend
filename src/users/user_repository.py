import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.users.user_model import User

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