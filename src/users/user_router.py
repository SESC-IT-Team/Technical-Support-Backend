import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from users.user_schemas import CreateAdminResponse
from utils.custom_auth.custom_auth import TechSupportUser, TechSupportAuth
from sesc_auth_sdk.enums.role import Role
router = APIRouter()




@router.post("/admin")
def create_admin(user_id: uuid.UUID, department_id: uuid.UUID, user: TechSupportUser = Depends(TechSupportAuth(allowed_roles=[Role.admin]))):
    # работа с бд
    return CreateAdminResponse(
        status=True
    )
