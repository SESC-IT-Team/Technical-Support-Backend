from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from user_repository import UserRepository

async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)