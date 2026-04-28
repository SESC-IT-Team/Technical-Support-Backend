import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.users.user_schemas import CreateAdminResponse

router = APIRouter()

@router.post("/admin")
def create_admin(user_id: uuid.UUID, department_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # работа с бд
    return CreateAdminResponse(
        status=True
    )
