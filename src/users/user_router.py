import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from users.user_schemas import CreateAdminResponse

router = APIRouter()




@router.post("/admin")
def create_admin(user_id: uuid.UUID, department_id: uuid.UUID, db: Session = Depends(get_db)):
    # работа с бд
    return CreateAdminResponse(
        status=True
    )
