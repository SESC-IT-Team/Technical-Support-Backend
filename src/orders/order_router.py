from fastapi import Depends, APIRouter
from datetime import datetime

from database.session import SessionLocal, get_db
import uuid
from sqlalchemy.orm import Session

from orders.order_schemas import CreateOrderRequest, CreateOrderResponse

router = APIRouter()

@router.post("/create_orders")
def create_order(data: CreateOrderRequest, db: Session = Depends(get_db)):
    return CreateOrderResponse(
        id = uuid.uuid4(),
        department = data.department,
        from_user_id = uuid.uuid4(),
        worker = uuid.uuid4(),
        title = data.title,
        description = data.description,
        status = "not started",
        created_at = datetime(2026,3,13,17,17,17),
        finished_at = None,
    )

@router.post("/department")
def create_department(data: CreateOrderResponse, db: Session = Depends(get_db)):
    return create_department(
        id = uuid.uuid4(),
        department = data.department
    )



@router.post("/get_orders")
def get_orders(data: CreateOrderRequest, db: Session = Depends(get_db)):
    return get_orders(
        id=uuid.uuid4(),
        department=data.department,
        from_user_id=uuid.uuid4(),
        worker=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status="not started",  # даня сказал сделать так
        created_at=datetime(2026, 3, 13, 17, 17, 17),
        finished_at=None,
    )

@router.post("/change_status")
def change_status(data: CreateOrderResponse, db: Session = Depends(get_db)):
    return change_status(
        id=uuid.uuid4(),
        status="not started", # даня сказал сделать так


    )

@router.post("/set_worker")
def set_worker(data: CreateOrderResponse, db: Session = Depends(get_db)):
    return set_worker(
        id=uuid.uuid4(),
        worker=uuid.uuid4(),

    )